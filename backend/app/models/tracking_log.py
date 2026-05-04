from sqlalchemy import Column, Integer, String, Float, ForeignKey, Text, Enum as SAEnum
from sqlalchemy.orm import relationship
from app.core.database import Base
from app.models.base import TimestampMixin
from app.models.shipment import ShipmentStatus


class TrackingLog(Base, TimestampMixin):
    __tablename__ = "tracking_logs"

    id = Column(Integer, primary_key=True, index=True)
    shipment_id = Column(Integer, ForeignKey("shipments.id"), nullable=False, index=True)
    updated_by = Column(Integer, ForeignKey("users.id"), nullable=True)

    status = Column(SAEnum(ShipmentStatus), nullable=False)
    message = Column(Text, nullable=True)
    location_address = Column(Text, nullable=True)
    latitude = Column(Float, nullable=True)
    longitude = Column(Float, nullable=True)

    # Relationships
    shipment = relationship("Shipment", back_populates="tracking_logs")
    user = relationship("User", foreign_keys=[updated_by])

    def __repr__(self):
        return f"<TrackingLog shipment={self.shipment_id} status={self.status}>"
