from sqlalchemy import Column, Integer, String, Float, Boolean, ForeignKey, Enum as SAEnum, Text
from sqlalchemy.orm import relationship
from app.core.database import Base
from app.models.base import TimestampMixin
import enum


class DriverStatus(str, enum.Enum):
    available = "available"
    on_delivery = "on_delivery"
    off_duty = "off_duty"
    suspended = "suspended"


class VehicleType(str, enum.Enum):
    motorcycle = "motorcycle"
    car = "car"
    van = "van"
    truck = "truck"


class Driver(Base, TimestampMixin):
    __tablename__ = "drivers"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, unique=True)
    company_id = Column(Integer, ForeignKey("companies.id"), nullable=False)

    license_number = Column(String(100), unique=True, nullable=False)
    vehicle_type = Column(SAEnum(VehicleType), nullable=False)
    vehicle_plate = Column(String(20), nullable=False)
    vehicle_model = Column(String(100), nullable=True)

    status = Column(SAEnum(DriverStatus), default=DriverStatus.available, nullable=False)

    # Location (updated in real-time)
    current_latitude = Column(Float, nullable=True)
    current_longitude = Column(Float, nullable=True)
    last_location_update = Column(String(50), nullable=True)

    # Performance metrics (updated by AI service)
    performance_score = Column(Float, default=100.0, nullable=False)
    total_deliveries = Column(Integer, default=0, nullable=False)
    successful_deliveries = Column(Integer, default=0, nullable=False)
    average_rating = Column(Float, default=5.0, nullable=False)

    notes = Column(Text, nullable=True)

    # Relationships
    user = relationship("User", back_populates="driver_profile", lazy="selectin")
    shipments = relationship("Shipment", back_populates="driver")

    @property
    def success_rate(self) -> float:
        if self.total_deliveries == 0:
            return 100.0
        return round((self.successful_deliveries / self.total_deliveries) * 100, 2)

    def __repr__(self):
        return f"<Driver {self.license_number}>"
