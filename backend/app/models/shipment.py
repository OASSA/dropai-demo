from sqlalchemy import Column, Integer, String, Float, Boolean, ForeignKey, Enum as SAEnum, Text, DateTime
from sqlalchemy.orm import relationship
from app.core.database import Base
from app.models.base import TimestampMixin
import enum


class ShipmentStatus(str, enum.Enum):
    pending = "pending"
    assigned = "assigned"
    picked_up = "picked_up"
    in_transit = "in_transit"
    out_for_delivery = "out_for_delivery"
    delivered = "delivered"
    failed = "failed"
    cancelled = "cancelled"
    returned = "returned"


class ShipmentPriority(str, enum.Enum):
    low = "low"
    normal = "normal"
    high = "high"
    urgent = "urgent"


class Shipment(Base, TimestampMixin):
    __tablename__ = "shipments"

    id = Column(Integer, primary_key=True, index=True)
    tracking_number = Column(String(50), unique=True, nullable=False, index=True)
    company_id = Column(Integer, ForeignKey("companies.id"), nullable=False)

    # Status
    status = Column(SAEnum(ShipmentStatus), default=ShipmentStatus.pending, nullable=False, index=True)
    priority = Column(SAEnum(ShipmentPriority), default=ShipmentPriority.normal, nullable=False)

    # Origin & Destination
    origin_warehouse_id = Column(Integer, ForeignKey("warehouses.id"), nullable=True)
    destination_warehouse_id = Column(Integer, ForeignKey("warehouses.id"), nullable=True)
    origin_address = Column(Text, nullable=False)
    origin_city = Column(String(100), nullable=False)
    origin_latitude = Column(Float, nullable=True)
    origin_longitude = Column(Float, nullable=True)
    destination_address = Column(Text, nullable=False)
    destination_city = Column(String(100), nullable=False)
    destination_latitude = Column(Float, nullable=True)
    destination_longitude = Column(Float, nullable=True)

    # Recipient
    recipient_name = Column(String(200), nullable=False)
    recipient_phone = Column(String(20), nullable=False)
    recipient_email = Column(String(255), nullable=True)

    # Package details
    weight_kg = Column(Float, nullable=True)
    dimensions = Column(String(100), nullable=True)  # "LxWxH cm"
    description = Column(Text, nullable=True)
    declared_value = Column(Float, nullable=True)
    is_fragile = Column(Boolean, default=False)

    # Assignment
    driver_id = Column(Integer, ForeignKey("drivers.id"), nullable=True)
    assigned_at = Column(DateTime(timezone=True), nullable=True)

    # Timing
    scheduled_pickup = Column(DateTime(timezone=True), nullable=True)
    actual_pickup = Column(DateTime(timezone=True), nullable=True)
    scheduled_delivery = Column(DateTime(timezone=True), nullable=True)
    actual_delivery = Column(DateTime(timezone=True), nullable=True)

    # AI predictions
    predicted_eta = Column(DateTime(timezone=True), nullable=True)
    predicted_distance_km = Column(Float, nullable=True)
    optimized_route = Column(Text, nullable=True)  # JSON string of waypoints

    # Metadata
    created_by = Column(Integer, ForeignKey("users.id"), nullable=False)
    notes = Column(Text, nullable=True)
    failure_reason = Column(Text, nullable=True)

    # Relationships
    company = relationship("Company", back_populates="shipments")
    driver = relationship("Driver", back_populates="shipments")
    origin_warehouse = relationship("Warehouse", foreign_keys=[origin_warehouse_id], back_populates="outgoing_shipments")
    destination_warehouse = relationship("Warehouse", foreign_keys=[destination_warehouse_id], back_populates="incoming_shipments")
    creator = relationship("User", foreign_keys=[created_by])
    tracking_logs = relationship("TrackingLog", back_populates="shipment", order_by="TrackingLog.created_at")
    notifications = relationship("Notification", back_populates="shipment")

    def __repr__(self):
        return f"<Shipment {self.tracking_number} - {self.status}>"
