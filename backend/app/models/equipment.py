import uuid
import enum
from datetime import datetime, date
from sqlalchemy import String, Boolean, Enum, DateTime, Date, Float, Integer, ForeignKey, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID, JSONB

from app.database import Base


class EquipmentStatus(str, enum.Enum):
    active = "active"
    under_calibration = "under_calibration"
    under_maintenance = "under_maintenance"
    out_of_service = "out_of_service"
    retired = "retired"


class Equipment(Base):
    __tablename__ = "equipment"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    lab_id: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    manufacturer: Mapped[str] = mapped_column(String(255), nullable=False)
    model: Mapped[str] = mapped_column(String(255), nullable=False)
    serial_number: Mapped[str] = mapped_column(String(100), nullable=False)
    asset_tag: Mapped[str | None] = mapped_column(String(100))
    equipment_type: Mapped[str] = mapped_column(String(50), nullable=False)
    status: Mapped[EquipmentStatus] = mapped_column(Enum(EquipmentStatus), nullable=False, default=EquipmentStatus.active)
    location: Mapped[str | None] = mapped_column(String(200))
    last_calibration_date: Mapped[date | None] = mapped_column(Date)
    next_calibration_date: Mapped[date | None] = mapped_column(Date)
    calibration_interval_days: Mapped[int | None] = mapped_column(Integer)
    calibration_cert_path: Mapped[str | None] = mapped_column(String(500))
    comm_protocol: Mapped[str | None] = mapped_column(String(50))
    comm_port: Mapped[str | None] = mapped_column(String(100))
    comm_baud_rate: Mapped[int | None] = mapped_column(Integer)
    comm_config: Mapped[dict | None] = mapped_column(JSONB)
    purchase_date: Mapped[date | None] = mapped_column(Date)
    warranty_expiry: Mapped[date | None] = mapped_column(Date)
    notes: Mapped[str | None] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow)

    calibration_records: Mapped[list["CalibrationRecord"]] = relationship(back_populates="equipment")
    maintenance_logs: Mapped[list["MaintenanceLog"]] = relationship(back_populates="equipment")


class CalibrationRecord(Base):
    __tablename__ = "calibration_records"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    equipment_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("equipment.id"), nullable=False)
    calibration_date: Mapped[date] = mapped_column(Date, nullable=False)
    calibration_type: Mapped[str] = mapped_column(String(50), nullable=False, default="internal")
    performed_by_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    external_provider: Mapped[str | None] = mapped_column(String(255))
    certificate_number: Mapped[str | None] = mapped_column(String(100))
    certificate_path: Mapped[str | None] = mapped_column(String(500))
    result: Mapped[str] = mapped_column(String(20), nullable=False, default="pass")
    due_date: Mapped[date] = mapped_column(Date, nullable=False)
    measurements: Mapped[dict | None] = mapped_column(JSONB)
    notes: Mapped[str | None] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow)

    equipment: Mapped["Equipment"] = relationship(back_populates="calibration_records")
    performed_by: Mapped["User"] = relationship()


class MaintenanceLog(Base):
    __tablename__ = "maintenance_logs"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    equipment_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("equipment.id"), nullable=False)
    maintenance_date: Mapped[date] = mapped_column(Date, nullable=False)
    maintenance_type: Mapped[str] = mapped_column(String(50), nullable=False, default="preventive")
    description: Mapped[str] = mapped_column(Text, nullable=False)
    performed_by_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="SET NULL"))
    external_technician: Mapped[str | None] = mapped_column(String(255))
    cost: Mapped[float | None] = mapped_column(Float)
    downtime_hours: Mapped[float | None] = mapped_column(Float)
    parts_replaced: Mapped[str | None] = mapped_column(Text)
    next_maintenance_date: Mapped[date | None] = mapped_column(Date)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow)

    equipment: Mapped["Equipment"] = relationship(back_populates="maintenance_logs")
    performed_by: Mapped["User | None"] = relationship(foreign_keys=[performed_by_id])
