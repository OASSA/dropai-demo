"""
DropAI Simulation Engine
Runs as a background asyncio task, continuously driving shipments through their
lifecycle to make the platform feel like a live logistics operation.

Tick cadence: every TICK_SECONDS seconds.
Each tick:
  1. tick_assign  — pair pending shipments with available drivers
  2. tick_advance — move in-progress shipments to their next status
  3. tick_locations — jitter driver GPS (simulates movement)
  4. tick_spawn   — generate new pending shipments when pipeline runs low
"""
import asyncio
import random
import logging
from datetime import datetime, timezone, timedelta

from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import AsyncSessionLocal
from app.models.shipment import Shipment, ShipmentStatus, ShipmentPriority
from app.models.driver import Driver, DriverStatus
from app.models.tracking_log import TrackingLog
from app.models.company import Company
from app.models.user import User
from app.models.role import Role
from app.utils.helpers import generate_tracking_number

logger = logging.getLogger(__name__)

TICK_SECONDS = 30

# Seconds a shipment must spend in each status before the engine advances it
ADVANCE_AFTER = {
    ShipmentStatus.assigned:         120,   # 2 min → picked_up
    ShipmentStatus.picked_up:        300,   # 5 min → in_transit
    ShipmentStatus.in_transit:       600,   # 10 min → out_for_delivery
    ShipmentStatus.out_for_delivery: 180,   # 3 min → delivered / failed
}

NEXT_STATUS = {
    ShipmentStatus.assigned:  ShipmentStatus.picked_up,
    ShipmentStatus.picked_up: ShipmentStatus.in_transit,
    ShipmentStatus.in_transit: ShipmentStatus.out_for_delivery,
}

STATUS_MSG = {
    ShipmentStatus.assigned:         "Assigned to driver — awaiting pickup",
    ShipmentStatus.picked_up:        "Package collected from sender",
    ShipmentStatus.in_transit:       "Shipment in transit to destination",
    ShipmentStatus.out_for_delivery: "Package is out for delivery",
    ShipmentStatus.delivered:        "Package delivered successfully — recipient confirmed",
    ShipmentStatus.failed:           "Delivery attempt failed — recipient not available",
}

SAUDI_CITIES = [
    {"name": "Riyadh",   "lat": 24.7136, "lon": 46.6753},
    {"name": "Jeddah",   "lat": 21.3891, "lon": 39.8579},
    {"name": "Mecca",    "lat": 21.4225, "lon": 39.8262},
    {"name": "Medina",   "lat": 24.5247, "lon": 39.5692},
    {"name": "Dammam",   "lat": 26.4207, "lon": 50.0888},
    {"name": "Khobar",   "lat": 26.2172, "lon": 50.1971},
    {"name": "Tabuk",    "lat": 28.3835, "lon": 36.5662},
    {"name": "Abha",     "lat": 18.2164, "lon": 42.5053},
    {"name": "Jizan",    "lat": 16.8892, "lon": 42.5611},
    {"name": "Buraidah", "lat": 26.3259, "lon": 43.9750},
]

RECIPIENT_NAMES = [
    "Sara Al-Mutairi", "Nora Al-Issa", "Layla Hassan", "Fatima Khalid",
    "Reem Abdullah", "Dana Al-Saud", "Hessa Mohammed", "Maha Al-Faisal",
    "Dalal Ibrahim", "Sheikha Nasser", "Ahmed Al-Ghamdi", "Mohammed Al-Otaibi",
    "Khalid Al-Harbi", "Faisal Al-Rashidi", "Omar Al-Zahrani",
]

STREETS = [
    "King Fahd Road", "Prince Sultan Street", "Al-Madinah Road",
    "Palestine Street", "Al-Corniche", "Airport Road",
    "Industrial Zone Blvd", "Commercial District Ave",
]


async def _log(db: AsyncSession, shipment_id: int, status: ShipmentStatus,
               message: str, lat=None, lon=None):
    db.add(TrackingLog(
        shipment_id=shipment_id,
        status=status,
        message=message,
        latitude=lat,
        longitude=lon,
    ))


# ---------------------------------------------------------------------------
# Tick functions
# ---------------------------------------------------------------------------

async def tick_assign(db: AsyncSession) -> int:
    """Assign pending shipments to the best available driver per company."""
    pending = (await db.execute(
        select(Shipment)
        .where(Shipment.status == ShipmentStatus.pending)
        .limit(10)
    )).scalars().all()

    count = 0
    for s in pending:
        driver = (await db.execute(
            select(Driver)
            .where(
                Driver.company_id == s.company_id,
                Driver.status == DriverStatus.available,
            )
            .order_by(Driver.performance_score.desc())
            .limit(1)
        )).scalar_one_or_none()

        if not driver:
            continue

        now = datetime.now(timezone.utc)
        s.status = ShipmentStatus.assigned
        s.driver_id = driver.id
        s.assigned_at = now
        driver.status = DriverStatus.on_delivery

        await _log(db, s.id, ShipmentStatus.assigned,
                   f"Assigned to driver {driver.license_number}",
                   s.origin_latitude, s.origin_longitude)
        count += 1

    await db.commit()
    return count


async def tick_advance(db: AsyncSession) -> int:
    """Advance in-progress shipments whose updated_at has aged past the threshold."""
    now = datetime.now(timezone.utc)
    count = 0

    for status, delay in ADVANCE_AFTER.items():
        threshold = now - timedelta(seconds=delay)

        rows = (await db.execute(
            select(Shipment)
            .where(
                Shipment.status == status,
                Shipment.updated_at <= threshold,
            )
            .limit(20)
        )).scalars().all()

        for s in rows:
            if status == ShipmentStatus.out_for_delivery:
                # 90 % delivered, 10 % failed
                success = random.random() < 0.90
                s.status = ShipmentStatus.delivered if success else ShipmentStatus.failed
                if success:
                    s.actual_delivery = now
                else:
                    s.failure_reason = "Delivery failed — recipient not available at address"
                lat, lon = s.destination_latitude, s.destination_longitude

                if s.driver_id:
                    drv = (await db.execute(
                        select(Driver).where(Driver.id == s.driver_id)
                    )).scalar_one_or_none()
                    if drv:
                        drv.status = DriverStatus.available
                        drv.total_deliveries += 1
                        if success:
                            drv.successful_deliveries += 1
                        drv.performance_score = round(
                            min(100.0, (drv.successful_deliveries / max(1, drv.total_deliveries)) * 100), 2
                        )
            else:
                next_s = NEXT_STATUS[status]
                s.status = next_s
                if next_s == ShipmentStatus.picked_up:
                    s.actual_pickup = now
                lat, lon = s.origin_latitude, s.origin_longitude

            await _log(db, s.id, s.status, STATUS_MSG[s.status], lat, lon)
            count += 1

    await db.commit()
    return count


async def tick_locations(db: AsyncSession):
    """Simulate driver movement with small GPS jitter."""
    drivers = (await db.execute(
        select(Driver).where(Driver.status == DriverStatus.on_delivery)
    )).scalars().all()

    for d in drivers:
        if d.current_latitude and d.current_longitude:
            d.current_latitude  += random.uniform(-0.008, 0.008)
            d.current_longitude += random.uniform(-0.008, 0.008)
            d.last_location_update = datetime.now(timezone.utc).isoformat()

    if drivers:
        await db.commit()


async def tick_spawn(db: AsyncSession):
    """Spawn new pending shipments when the pipeline runs low (< 10 pending)."""
    pending_count = (await db.execute(
        select(func.count()).select_from(Shipment).where(Shipment.status == ShipmentStatus.pending)
    )).scalar_one()

    if pending_count >= 10:
        return

    companies = (await db.execute(
        select(Company).where(Company.is_active == True)
    )).scalars().all()

    for company in companies:
        admin = (await db.execute(
            select(User)
            .join(Role, User.role_id == Role.id)
            .where(User.company_id == company.id, Role.name == "company_admin")
            .limit(1)
        )).scalar_one_or_none()
        if not admin:
            continue

        for _ in range(random.randint(1, 3)):
            origin = random.choice(SAUDI_CITIES)
            dest   = random.choice([c for c in SAUDI_CITIES if c["name"] != origin["name"]])

            s = Shipment(
                tracking_number=generate_tracking_number(),
                company_id=company.id,
                created_by=admin.id,
                status=ShipmentStatus.pending,
                priority=random.choice(list(ShipmentPriority)),
                origin_city=origin["name"],
                origin_address=f"{random.choice(STREETS)}, {origin['name']}",
                origin_latitude=origin["lat"]  + random.uniform(-0.1, 0.1),
                origin_longitude=origin["lon"] + random.uniform(-0.1, 0.1),
                destination_city=dest["name"],
                destination_address=f"{random.choice(STREETS)}, {dest['name']}",
                destination_latitude=dest["lat"]  + random.uniform(-0.1, 0.1),
                destination_longitude=dest["lon"] + random.uniform(-0.1, 0.1),
                recipient_name=random.choice(RECIPIENT_NAMES),
                recipient_phone=f"+9665{random.randint(10000000, 99999999)}",
                weight_kg=round(random.uniform(0.5, 25.0), 2),
            )
            db.add(s)
            await db.flush()
            await _log(db, s.id, ShipmentStatus.pending,
                       "Shipment created and queued for assignment")

    await db.commit()


# ---------------------------------------------------------------------------
# Main loop
# ---------------------------------------------------------------------------

async def _run_tick():
    for fn in (tick_assign, tick_advance, tick_locations, tick_spawn):
        try:
            async with AsyncSessionLocal() as db:
                result = await fn(db)
                if isinstance(result, int) and result:
                    logger.info(f"[SIM] {fn.__name__}: {result} items")
        except Exception as exc:
            logger.error(f"[SIM] {fn.__name__} error: {exc}", exc_info=True)


async def simulation_loop():
    logger.info("[SIM] Simulation engine starting — initial delay 15 s")
    await asyncio.sleep(15)
    logger.info("[SIM] Simulation engine running (tick every %d s)", TICK_SECONDS)
    while True:
        try:
            await _run_tick()
        except Exception as exc:
            logger.error(f"[SIM] top-level error: {exc}", exc_info=True)
        await asyncio.sleep(TICK_SECONDS)
