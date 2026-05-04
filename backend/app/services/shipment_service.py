from datetime import datetime, timezone
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException, status

from app.repositories.shipment_repository import ShipmentRepository
from app.repositories.driver_repository import DriverRepository
from app.models.shipment import Shipment, ShipmentStatus
from app.models.tracking_log import TrackingLog
from app.models.driver import DriverStatus
from app.schemas.shipment import ShipmentCreate, ShipmentAssign, ShipmentStatusUpdate
from app.services.ai_service import ai_service
from app.services.notification_service import notification_service
from app.models.notification import NotificationType, NotificationChannel
from app.utils.audit import log_action
from app.utils.helpers import generate_tracking_number


class ShipmentService:
    async def create(
        self,
        db: AsyncSession,
        payload: ShipmentCreate,
        company_id: int,
        created_by: int,
    ) -> Shipment:
        tracking_number = generate_tracking_number()
        shipment = Shipment(
            tracking_number=tracking_number,
            company_id=company_id,
            created_by=created_by,
            **payload.model_dump(exclude_none=True),
        )

        # Run AI ETA prediction if coordinates are present
        if (
            payload.origin_latitude and payload.origin_longitude
            and payload.destination_latitude and payload.destination_longitude
        ):
            eta, dist = ai_service.predict_eta(
                payload.origin_latitude,
                payload.origin_longitude,
                payload.destination_latitude,
                payload.destination_longitude,
                payload.priority.value,
            )
            shipment.predicted_eta = eta
            shipment.predicted_distance_km = dist

        db.add(shipment)
        await db.flush()
        await db.refresh(shipment)

        # Initial tracking log
        log = TrackingLog(
            shipment_id=shipment.id,
            updated_by=created_by,
            status=ShipmentStatus.pending,
            message="Shipment created and waiting for assignment",
        )
        db.add(log)

        await log_action(
            db,
            action="CREATE_SHIPMENT",
            resource_type="shipment",
            resource_id=shipment.id,
            user_id=created_by,
            new_value={"tracking_number": tracking_number, "status": "pending"},
        )

        return shipment

    async def assign_driver(
        self,
        db: AsyncSession,
        shipment_id: int,
        payload: ShipmentAssign,
        assigned_by: int,
    ) -> Shipment:
        ship_repo = ShipmentRepository(db)
        driver_repo = DriverRepository(db)

        shipment = await ship_repo.get(shipment_id)
        if not shipment:
            raise HTTPException(status_code=404, detail="Shipment not found")
        if shipment.status not in (ShipmentStatus.pending, ShipmentStatus.assigned):
            raise HTTPException(status_code=400, detail="Cannot reassign a shipment that is in transit or completed")

        driver = await driver_repo.get(payload.driver_id)
        if not driver:
            raise HTTPException(status_code=404, detail="Driver not found")

        old_driver_id = shipment.driver_id
        shipment.driver_id = driver.id
        shipment.status = ShipmentStatus.assigned
        shipment.assigned_at = datetime.now(timezone.utc)

        driver.status = DriverStatus.on_delivery
        db.add(driver)

        log = TrackingLog(
            shipment_id=shipment.id,
            updated_by=assigned_by,
            status=ShipmentStatus.assigned,
            message=f"Assigned to driver {driver.id}",
        )
        db.add(log)

        # Notify driver
        await notification_service.send(
            db,
            user_id=driver.user_id,
            title="New Delivery Assignment",
            message=f"You have been assigned shipment {shipment.tracking_number}",
            notification_type=NotificationType.assignment,
            shipment_id=shipment.id,
        )

        await log_action(
            db,
            action="ASSIGN_DRIVER",
            resource_type="shipment",
            resource_id=shipment_id,
            user_id=assigned_by,
            old_value={"driver_id": old_driver_id},
            new_value={"driver_id": driver.id},
        )

        return shipment

    async def update_status(
        self,
        db: AsyncSession,
        shipment_id: int,
        payload: ShipmentStatusUpdate,
        updated_by: int,
    ) -> Shipment:
        repo = ShipmentRepository(db)
        shipment = await repo.get(shipment_id)
        if not shipment:
            raise HTTPException(status_code=404, detail="Shipment not found")

        old_status = shipment.status
        shipment.status = payload.status

        now = datetime.now(timezone.utc)
        if payload.status == ShipmentStatus.picked_up:
            shipment.actual_pickup = now
        elif payload.status == ShipmentStatus.delivered:
            shipment.actual_delivery = now
            # Update driver metrics
            if shipment.driver_id:
                driver_repo = DriverRepository(db)
                driver = await driver_repo.get(shipment.driver_id)
                if driver:
                    driver.total_deliveries += 1
                    driver.successful_deliveries += 1
                    driver.performance_score = ai_service.score_driver(
                        driver.total_deliveries, driver.successful_deliveries, driver.average_rating
                    )
                    driver.status = DriverStatus.available
                    db.add(driver)
        elif payload.status == ShipmentStatus.failed:
            shipment.failure_reason = payload.message
            if shipment.driver_id:
                driver_repo = DriverRepository(db)
                driver = await driver_repo.get(shipment.driver_id)
                if driver:
                    driver.total_deliveries += 1
                    driver.performance_score = ai_service.score_driver(
                        driver.total_deliveries, driver.successful_deliveries, driver.average_rating
                    )
                    driver.status = DriverStatus.available
                    db.add(driver)

        log = TrackingLog(
            shipment_id=shipment.id,
            updated_by=updated_by,
            status=payload.status,
            message=payload.message,
            latitude=payload.latitude,
            longitude=payload.longitude,
            location_address=payload.location_address,
        )
        db.add(log)

        await log_action(
            db,
            action="UPDATE_STATUS",
            resource_type="shipment",
            resource_id=shipment_id,
            user_id=updated_by,
            old_value={"status": old_status.value},
            new_value={"status": payload.status.value},
        )

        return shipment


shipment_service = ShipmentService()
