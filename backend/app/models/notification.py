from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, Text, Enum as SAEnum
from sqlalchemy.orm import relationship
from app.core.database import Base
from app.models.base import TimestampMixin
import enum


class NotificationType(str, enum.Enum):
    info = "info"
    success = "success"
    warning = "warning"
    error = "error"
    shipment_update = "shipment_update"
    delay_alert = "delay_alert"
    assignment = "assignment"
    system = "system"


class NotificationChannel(str, enum.Enum):
    in_app = "in_app"
    email = "email"
    whatsapp = "whatsapp"
    sms = "sms"


class Notification(Base, TimestampMixin):
    __tablename__ = "notifications"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    shipment_id = Column(Integer, ForeignKey("shipments.id"), nullable=True)

    type = Column(SAEnum(NotificationType), nullable=False)
    channel = Column(SAEnum(NotificationChannel), default=NotificationChannel.in_app, nullable=False)
    title = Column(String(255), nullable=False)
    message = Column(Text, nullable=False)
    is_read = Column(Boolean, default=False, nullable=False)
    sent_at = Column(String(50), nullable=True)

    # Relationships
    user = relationship("User", back_populates="notifications")
    shipment = relationship("Shipment", back_populates="notifications")

    def __repr__(self):
        return f"<Notification {self.type} -> user={self.user_id}>"
