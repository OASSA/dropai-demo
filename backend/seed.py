"""
DropAI comprehensive seed — creates a fully populated simulation environment.

Generates:
  • 1 super admin
  • 4 logistics companies (multi-tenant isolated)
  • 10 drivers per company  (user record + driver record)
  • 2 warehouse managers per company
  • 2 warehouses per company
  • 60 shipments per company  (spread across all statuses & past 30 days)
  • TrackingLog history for every non-pending shipment

Run:  python seed.py
Safe to re-run — uses ON CONFLICT / existence checks to stay idempotent.
"""
import asyncio
import random
import string
from datetime import datetime, timezone, timedelta

from sqlalchemy import text

from app.core.database import AsyncSessionLocal, engine, Base
from app.core.security import get_password_hash

# ---------------------------------------------------------------------------
# Reference data
# ---------------------------------------------------------------------------

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

FIRST_NAMES = [
    "Ahmed", "Mohammed", "Ali", "Omar", "Ibrahim",
    "Khalid", "Faisal", "Abdullah", "Hassan", "Salman",
    "Nasser", "Tariq", "Walid", "Youssef", "Saad",
    "Reem",  "Nora",   "Sara",  "Layla",  "Fatima",
]

LAST_NAMES = [
    "Al-Rashidi", "Al-Otaibi", "Al-Ghamdi", "Al-Harbi",
    "Al-Qahtani", "Al-Shahrani", "Al-Zahrani", "Al-Shehri",
    "Al-Dosari",  "Al-Anazi",   "Al-Mutairi", "Al-Issa",
]

STREETS = [
    "King Fahd Road", "Prince Sultan Street", "Al-Madinah Road",
    "Palestine Street", "Al-Corniche Blvd", "Airport Road",
    "Industrial Zone", "Commercial District Ave", "Diplomatic Quarter",
    "Old Town Bypass",
]

VEHICLE_TYPES  = ["motorcycle", "car", "van", "truck"]
VEHICLE_PLATES = list("ABCDEFGHJKLMNPQRSTUVWXYZ")  # 23 chars

COMPANIES = [
    {
        "name":  "Acme Logistics",
        "email": "demo@acme-logistics.com",
        "city":  "Jeddah",
        "plan":  "professional",
        "slug":  "acme",
    },
    {
        "name":  "Swift Delivery",
        "email": "info@swift-delivery.sa",
        "city":  "Riyadh",
        "plan":  "enterprise",
        "slug":  "swift",
    },
    {
        "name":  "Saudi Express",
        "email": "ops@saudi-express.sa",
        "city":  "Dammam",
        "plan":  "professional",
        "slug":  "saudiexpress",
    },
    {
        "name":  "Gulf Transport Co",
        "email": "contact@gulf-transport.sa",
        "city":  "Mecca",
        "plan":  "basic",
        "slug":  "gulf",
    },
]

# Shipment status distribution for the 60 seeded shipments per company
STATUS_DIST = (
    ["pending"]          * 10 +
    ["assigned"]         *  5 +
    ["picked_up"]        *  5 +
    ["in_transit"]       * 10 +
    ["out_for_delivery"] *  5 +
    ["delivered"]        * 20 +
    ["failed"]           *  3 +
    ["cancelled"]        *  2
)  # 60 total


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def rnd_tracking() -> str:
    return "DR" + "".join(random.choices(string.digits, k=10))

def rnd_license(slug: str, n: int) -> str:
    return f"SA{slug.upper()[:3]}{n:04d}"

def rnd_plate(slug: str, n: int) -> str:
    letters = random.choices(VEHICLE_PLATES, k=3)
    return f"{''.join(letters)}-{random.randint(1000, 9999)}"

def rnd_name() -> tuple[str, str]:
    return random.choice(FIRST_NAMES), random.choice(LAST_NAMES)

def rnd_phone() -> str:
    return f"+9665{random.randint(10000000, 99999999)}"

def rnd_coords(city: dict, jitter: float = 0.15) -> tuple[float, float]:
    return (
        city["lat"] + random.uniform(-jitter, jitter),
        city["lon"] + random.uniform(-jitter, jitter),
    )

def ts(days_ago: float, hour: int = 10) -> datetime:
    """UTC datetime N days in the past."""
    t = datetime.now(timezone.utc) - timedelta(days=days_ago)
    return t.replace(hour=hour, minute=random.randint(0, 59), second=0, microsecond=0)

def ts_after(base_dt: datetime, minutes: int) -> datetime:
    return base_dt + timedelta(minutes=minutes)


# ---------------------------------------------------------------------------
# Core seed logic
# ---------------------------------------------------------------------------

async def seed():
    # ── 1. Ensure tables exist ──────────────────────────────────────────────
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    async with AsyncSessionLocal() as db:

        # ── 2. Roles ─────────────────────────────────────────────────────────
        await db.execute(text("""
            INSERT INTO roles (name, description) VALUES
              ('super_admin',       'Full system access'),
              ('company_admin',     'Manage company resources'),
              ('warehouse_manager', 'Manage shipments and drivers'),
              ('driver',            'View and update assigned deliveries'),
              ('customer',          'Track shipments via tracking number')
            ON CONFLICT (name) DO NOTHING
        """))
        await db.commit()

        role = {}
        for rname in ("super_admin", "company_admin", "warehouse_manager", "driver", "customer"):
            r = await db.execute(text("SELECT id FROM roles WHERE name = :n"), {"n": rname})
            role[rname] = r.scalar()

        # ── 3. Super admin company + user ────────────────────────────────────
        r = await db.execute(text("SELECT id FROM companies WHERE email = 'admin@dropai.io'"))
        sa_company_id = r.scalar()
        if not sa_company_id:
            await db.execute(text("""
                INSERT INTO companies (name, email, city, country, subscription_plan, is_active)
                VALUES ('DropAI HQ', 'admin@dropai.io', 'Riyadh', 'Saudi Arabia', 'enterprise', TRUE)
            """))
            await db.commit()
            r = await db.execute(text("SELECT id FROM companies WHERE email = 'admin@dropai.io'"))
            sa_company_id = r.scalar()

        r = await db.execute(text("SELECT id FROM users WHERE email = 'admin@dropai.io'"))
        if not r.scalar():
            await db.execute(text("""
                INSERT INTO users
                  (email, hashed_password, first_name, last_name, role_id, company_id, is_active, status)
                VALUES
                  ('admin@dropai.io', :pw, 'Super', 'Admin', :rid, :cid, TRUE, 'active')
            """), {"pw": get_password_hash("Admin@123"), "rid": role["super_admin"], "cid": sa_company_id})
            await db.commit()
            print("✅ Super admin created: admin@dropai.io / Admin@123")

        # ── 4. Simulation companies ──────────────────────────────────────────
        for co in COMPANIES:
            r = await db.execute(text("SELECT id FROM companies WHERE email = :e"), {"e": co["email"]})
            co_id = r.scalar()
            if not co_id:
                await db.execute(text("""
                    INSERT INTO companies
                      (name, email, city, country, subscription_plan, is_active)
                    VALUES (:name, :email, :city, 'Saudi Arabia', :plan, TRUE)
                """), {"name": co["name"], "email": co["email"],
                       "city": co["city"], "plan": co["plan"]})
                await db.commit()
                r = await db.execute(text("SELECT id FROM companies WHERE email = :e"), {"e": co["email"]})
                co_id = r.scalar()

            co["id"] = co_id

            # ── Company admin ────────────────────────────────────────────────
            admin_email = f"admin@{co['slug']}.demo"
            r = await db.execute(text("SELECT id FROM users WHERE email = :e"), {"e": admin_email})
            admin_id = r.scalar()
            if not admin_id:
                fn, ln = rnd_name()
                await db.execute(text("""
                    INSERT INTO users
                      (email, hashed_password, first_name, last_name,
                       role_id, company_id, is_active, status)
                    VALUES (:e, :pw, :fn, :ln, :rid, :cid, TRUE, 'active')
                """), {
                    "e": admin_email, "pw": get_password_hash("Company@123"),
                    "fn": fn, "ln": ln,
                    "rid": role["company_admin"], "cid": co_id,
                })
                await db.commit()
                r = await db.execute(text("SELECT id FROM users WHERE email = :e"), {"e": admin_email})
                admin_id = r.scalar()
                print(f"  ✅ Company admin: {admin_email} / Company@123")

            co["admin_id"] = admin_id

            # ── Warehouse managers ───────────────────────────────────────────
            mgr_ids = []
            for i in range(1, 3):
                mgr_email = f"manager{i}@{co['slug']}.demo"
                r = await db.execute(text("SELECT id FROM users WHERE email = :e"), {"e": mgr_email})
                mgr_id = r.scalar()
                if not mgr_id:
                    fn, ln = rnd_name()
                    await db.execute(text("""
                        INSERT INTO users
                          (email, hashed_password, first_name, last_name,
                           role_id, company_id, is_active, status)
                        VALUES (:e, :pw, :fn, :ln, :rid, :cid, TRUE, 'active')
                    """), {
                        "e": mgr_email, "pw": get_password_hash("Manager@123"),
                        "fn": fn, "ln": ln,
                        "rid": role["warehouse_manager"], "cid": co_id,
                    })
                    await db.commit()
                    r = await db.execute(text("SELECT id FROM users WHERE email = :e"), {"e": mgr_email})
                    mgr_id = r.scalar()
                mgr_ids.append(mgr_id)

            # ── Warehouses ───────────────────────────────────────────────────
            wh_ids = []
            for i, city in enumerate(random.sample(SAUDI_CITIES, 2)):
                code = f"{co['slug'].upper()[:4]}-WH{i+1:02d}"
                r = await db.execute(text("SELECT id FROM warehouses WHERE code = :c"), {"c": code})
                wh_id = r.scalar()
                if not wh_id:
                    lat, lon = rnd_coords(city)
                    await db.execute(text("""
                        INSERT INTO warehouses
                          (company_id, name, code, address, city, country,
                           latitude, longitude, manager_id, capacity, is_active)
                        VALUES (:cid, :name, :code, :addr, :city, 'Saudi Arabia',
                                :lat, :lon, :mgr, 500, TRUE)
                    """), {
                        "cid": co_id,
                        "name": f"{co['name']} — {city['name']} Hub",
                        "code": code,
                        "addr": f"{random.choice(STREETS)}, {city['name']}",
                        "city": city["name"],
                        "lat": lat, "lon": lon,
                        "mgr": mgr_ids[i % len(mgr_ids)],
                    })
                    await db.commit()
                    r = await db.execute(text("SELECT id FROM warehouses WHERE code = :c"), {"c": code})
                    wh_id = r.scalar()
                wh_ids.append(wh_id)

            # ── Drivers (10 per company) ─────────────────────────────────────
            driver_ids = []
            for n in range(1, 11):
                drv_email = f"driver{n}@{co['slug']}.demo"
                r = await db.execute(text("SELECT id FROM users WHERE email = :e"), {"e": drv_email})
                drv_user_id = r.scalar()
                if not drv_user_id:
                    fn, ln = rnd_name()
                    await db.execute(text("""
                        INSERT INTO users
                          (email, hashed_password, first_name, last_name,
                           role_id, company_id, is_active, status)
                        VALUES (:e, :pw, :fn, :ln, :rid, :cid, TRUE, 'active')
                    """), {
                        "e": drv_email, "pw": get_password_hash("Driver@123"),
                        "fn": fn, "ln": ln,
                        "rid": role["driver"], "cid": co_id,
                    })
                    await db.commit()
                    r = await db.execute(text("SELECT id FROM users WHERE email = :e"), {"e": drv_email})
                    drv_user_id = r.scalar()

                # Driver record
                lic = rnd_license(co["slug"], n)
                r = await db.execute(text("SELECT id FROM drivers WHERE license_number = :l"), {"l": lic})
                drv_id = r.scalar()
                if not drv_id:
                    city = random.choice(SAUDI_CITIES)
                    lat, lon = rnd_coords(city, 0.05)
                    deliveries = random.randint(20, 200)
                    successes  = int(deliveries * random.uniform(0.80, 1.0))
                    score      = round((successes / deliveries) * 100, 2)
                    await db.execute(text("""
                        INSERT INTO drivers
                          (user_id, company_id, license_number, vehicle_type, vehicle_plate,
                           vehicle_model, status, current_latitude, current_longitude,
                           last_location_update, performance_score,
                           total_deliveries, successful_deliveries, average_rating)
                        VALUES
                          (:uid, :cid, :lic, :vtype, :plate,
                           :model, 'available', :lat, :lon,
                           :upd, :score, :total, :succ, :rating)
                    """), {
                        "uid": drv_user_id, "cid": co_id,
                        "lic": lic,
                        "vtype": random.choice(VEHICLE_TYPES),
                        "plate": rnd_plate(co["slug"], n),
                        "model": random.choice(["Toyota Hilux", "Ford Transit", "Yamaha NMAX",
                                                "Kia Bongo", "Mitsubishi L200", "Nissan Patrol"]),
                        "lat": lat, "lon": lon,
                        "upd": datetime.now(timezone.utc).isoformat(),
                        "score": score, "total": deliveries, "succ": successes,
                        "rating": round(random.uniform(3.8, 5.0), 1),
                    })
                    await db.commit()
                    r = await db.execute(text("SELECT id FROM drivers WHERE license_number = :l"), {"l": lic})
                    drv_id = r.scalar()
                driver_ids.append(drv_id)

            print(f"  ✅ {co['name']}: 10 drivers, 2 warehouses, 2 managers ready")

            # ── Shipments (60 per company) ───────────────────────────────────
            r = await db.execute(
                text("SELECT COUNT(*) FROM shipments WHERE company_id = :cid"),
                {"cid": co_id}
            )
            existing = r.scalar()
            if existing >= 60:
                print(f"  ⏭  {co['name']}: already has {existing} shipments, skipping")
                continue

            statuses = STATUS_DIST[:]
            random.shuffle(statuses)

            # Track which drivers are currently "on_delivery" so we don't overload them
            busy_drivers: set[int] = set()

            for i, status in enumerate(statuses):
                origin_city = random.choice(SAUDI_CITIES)
                dest_city   = random.choice([c for c in SAUDI_CITIES if c["name"] != origin_city["name"]])
                o_lat, o_lon = rnd_coords(origin_city)
                d_lat, d_lon = rnd_coords(dest_city)

                tracking = rnd_tracking()
                created_days_ago = random.uniform(0.5, 28)
                created_ts = ts(created_days_ago)

                recipient_names = [
                    "Sara Al-Mutairi", "Nora Al-Issa", "Layla Hassan", "Fatima Khalid",
                    "Reem Abdullah", "Dana Al-Saud", "Hessa Mohammed", "Maha Al-Faisal",
                    "Dalal Ibrahim", "Sheikha Nasser", "Ahmed Al-Ghamdi", "Mohammed Al-Otaibi",
                    "Khalid Al-Harbi", "Faisal Al-Rashidi", "Omar Al-Zahrani",
                ]
                priorities = ["low", "normal", "normal", "normal", "high", "urgent"]

                # Base shipment fields
                base = {
                    "tracking":  tracking,
                    "cid":       co_id,
                    "status":    status,
                    "priority":  random.choice(priorities),
                    "o_addr":    f"{random.choice(STREETS)}, {origin_city['name']}",
                    "o_city":    origin_city["name"],
                    "o_lat":     o_lat, "o_lon": o_lon,
                    "d_addr":    f"{random.choice(STREETS)}, {dest_city['name']}",
                    "d_city":    dest_city["name"],
                    "d_lat":     d_lat, "d_lon": d_lon,
                    "rname":     random.choice(recipient_names),
                    "rphone":    rnd_phone(),
                    "weight":    round(random.uniform(0.5, 30.0), 2),
                    "fragile":   random.random() < 0.15,
                    "value":     round(random.uniform(50, 5000), 2),
                    "created_by": admin_id,
                    "created_at": created_ts,
                    "updated_at": created_ts,
                }

                # Assign a driver for non-pending statuses
                driver_id = None
                assigned_at = None
                actual_pickup = None
                actual_delivery = None
                failure_reason = None

                if status not in ("pending", "cancelled"):
                    # Pick an available (not busy) driver
                    avail = [d for d in driver_ids if d not in busy_drivers]
                    if not avail:
                        avail = driver_ids  # allow overlap for historical data
                    driver_id = random.choice(avail)
                    if status in ("assigned", "picked_up", "in_transit", "out_for_delivery"):
                        busy_drivers.add(driver_id)

                    assigned_at = ts_after(created_ts, random.randint(10, 60))
                    base["updated_at"] = assigned_at

                    if status in ("picked_up", "in_transit", "out_for_delivery",
                                  "delivered", "failed"):
                        actual_pickup = ts_after(assigned_at, random.randint(20, 90))
                        base["updated_at"] = actual_pickup

                    if status == "delivered":
                        actual_delivery = ts_after(
                            actual_pickup, random.randint(60, 480)
                        )
                        base["updated_at"] = actual_delivery
                    elif status == "failed":
                        failure_reason = random.choice([
                            "Recipient not available",
                            "Wrong address — returned to sender",
                            "Customer refused delivery",
                        ])
                        base["updated_at"] = ts_after(actual_pickup, random.randint(60, 300))

                await db.execute(text("""
                    INSERT INTO shipments (
                        tracking_number, company_id, status, priority,
                        origin_address, origin_city, origin_latitude, origin_longitude,
                        destination_address, destination_city, destination_latitude, destination_longitude,
                        recipient_name, recipient_phone,
                        weight_kg, is_fragile, declared_value,
                        driver_id, assigned_at, actual_pickup, actual_delivery, failure_reason,
                        created_by, created_at, updated_at
                    ) VALUES (
                        :tracking, :cid, :status, :priority,
                        :o_addr, :o_city, :o_lat, :o_lon,
                        :d_addr, :d_city, :d_lat, :d_lon,
                        :rname, :rphone,
                        :weight, :fragile, :value,
                        :drv, :assigned_at, :actual_pickup, :actual_delivery, :failure_reason,
                        :created_by, :created_at, :updated_at
                    )
                """), {
                    **base,
                    "drv": driver_id,
                    "assigned_at": assigned_at,
                    "actual_pickup": actual_pickup,
                    "actual_delivery": actual_delivery,
                    "failure_reason": failure_reason,
                })

            await db.commit()

            # ── Mark on-delivery drivers as busy ──────────────────────────────
            if busy_drivers:
                for drv_id in list(busy_drivers)[:5]:  # keep at most 5 busy
                    await db.execute(
                        text("UPDATE drivers SET status = 'on_delivery' WHERE id = :id"),
                        {"id": drv_id}
                    )
                await db.commit()

            # ── Tracking logs for non-pending shipments ───────────────────────
            rows = (await db.execute(
                text("""
                    SELECT id, status, origin_latitude, origin_longitude,
                           destination_latitude, destination_longitude,
                           assigned_at, actual_pickup, actual_delivery, created_at
                    FROM shipments
                    WHERE company_id = :cid AND status != 'pending'
                """),
                {"cid": co_id}
            )).fetchall()

            log_data = []
            for row in rows:
                (sid, status, o_lat, o_lon, d_lat, d_lon,
                 assigned_at, actual_pickup, actual_delivery, created_at) = row

                # Always add a "created" log
                log_data.append({
                    "sid": sid, "status": "pending",
                    "msg": "Shipment created and waiting for assignment",
                    "lat": o_lat, "lon": o_lon, "ts": created_at,
                })

                if status in ("assigned", "picked_up", "in_transit",
                              "out_for_delivery", "delivered", "failed"):
                    log_data.append({
                        "sid": sid, "status": "assigned",
                        "msg": "Driver assigned — heading to pickup location",
                        "lat": o_lat, "lon": o_lon,
                        "ts": assigned_at or created_at,
                    })

                if status in ("picked_up", "in_transit", "out_for_delivery",
                              "delivered", "failed"):
                    log_data.append({
                        "sid": sid, "status": "picked_up",
                        "msg": "Package collected from sender",
                        "lat": o_lat, "lon": o_lon,
                        "ts": actual_pickup or assigned_at,
                    })

                if status in ("in_transit", "out_for_delivery", "delivered", "failed"):
                    log_data.append({
                        "sid": sid, "status": "in_transit",
                        "msg": "Shipment in transit to destination city",
                        "lat": (o_lat + d_lat) / 2 if o_lat and d_lat else o_lat,
                        "lon": (o_lon + d_lon) / 2 if o_lon and d_lon else o_lon,
                        "ts": actual_pickup or assigned_at,
                    })

                if status in ("out_for_delivery", "delivered", "failed"):
                    log_data.append({
                        "sid": sid, "status": "out_for_delivery",
                        "msg": "Package is out for delivery",
                        "lat": d_lat, "lon": d_lon,
                        "ts": actual_pickup or assigned_at,
                    })

                if status == "delivered":
                    log_data.append({
                        "sid": sid, "status": "delivered",
                        "msg": "Package delivered successfully — recipient confirmed",
                        "lat": d_lat, "lon": d_lon,
                        "ts": actual_delivery or actual_pickup,
                    })

                if status == "failed":
                    log_data.append({
                        "sid": sid, "status": "failed",
                        "msg": "Delivery attempt failed — recipient not available",
                        "lat": d_lat, "lon": d_lon,
                        "ts": actual_pickup or assigned_at,
                    })

                if status == "cancelled":
                    log_data.append({
                        "sid": sid, "status": "cancelled",
                        "msg": "Shipment cancelled by company admin",
                        "lat": o_lat, "lon": o_lon, "ts": created_at,
                    })

            for entry in log_data:
                await db.execute(text("""
                    INSERT INTO tracking_logs
                      (shipment_id, status, message, latitude, longitude, created_at, updated_at)
                    VALUES (:sid, :status, :msg, :lat, :lon, :ts, :ts)
                """), entry)

            await db.commit()
            print(f"  ✅ {co['name']}: 60 shipments + tracking logs seeded")

        # ── Summary ──────────────────────────────────────────────────────────
        print("\n" + "═" * 55)
        print("  DropAI Simulation Environment — Ready")
        print("═" * 55)
        print("  Super Admin   : admin@dropai.io       / Admin@123")
        for co in COMPANIES:
            slug = co["slug"]
            print(f"\n  {co['name']}")
            print(f"    Company Admin : admin@{slug}.demo    / Company@123")
            print(f"    Managers      : manager1@{slug}.demo / Manager@123")
            print(f"    Drivers       : driver1@{slug}.demo  / Driver@123  (×10)")
        print("═" * 55)


if __name__ == "__main__":
    asyncio.run(seed())
