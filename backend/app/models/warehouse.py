from sqlalchemy import Column, Integer, String, Float, Boolean, ForeignKey, Text
from sqlalchemy.orm import relationship
from app.core.database import Base
from app.models.base import TimestampMixin


class Warehouse(Base, TimestampMixin):
    __tablename__ = "warehouses"

    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, ForeignKey("companies.id"), nullable=False)

    name = Column(String(200), nullable=False)
    code = Column(String(20), unique=True, nullable=False, index=True)
    address = Column(Text, nullable=False)
    city = Column(String(100), nullable=False)
    state = Column(String(100), nullable=True)
    country = Column(String(100), nullable=False)
    postal_code = Column(String(20), nullable=True)
    latitude = Column(Float, nullable=True)
    longitude = Column(Float, nullable=True)

    manager_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    phone = Column(String(20), nullable=True)
    email = Column(String(255), nullable=True)
    capacity = Column(Integer, nullable=True)
    is_active = Column(Boolean, default=True, nullable=False)

    # Relationships
    company = relationship("Company", back_populates="warehouses")
    manager = relationship("User", foreign_keys=[manager_id])
    outgoing_shipments = relationship("Shipment", foreign_keys="Shipment.origin_warehouse_id", back_populates="origin_warehouse")
    incoming_shipments = relationship("Shipment", foreign_keys="Shipment.destination_warehouse_id", back_populates="destination_warehouse")

    def __repr__(self):
        return f"<Warehouse {self.code} - {self.name}>"
