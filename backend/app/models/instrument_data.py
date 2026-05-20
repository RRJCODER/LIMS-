import uuid
from datetime import datetime
from sqlalchemy import String, DateTime, Float, ForeignKey, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID, JSONB

from app.database import Base


class RawInstrumentReading(Base):
    __tablename__ = "raw_instrument_readings"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    equipment_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("equipment.id"), nullable=False)
    test_request_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), ForeignKey("test_requests.id", ondelete="SET NULL"))
    reading_type: Mapped[str] = mapped_column(String(50), nullable=False)
    raw_payload: Mapped[dict] = mapped_column(JSONB, nullable=False, default=dict)
    value: Mapped[float | None] = mapped_column(Float)
    unit: Mapped[str | None] = mapped_column(String(50))
    timestamp: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow, nullable=False)
    session_id: Mapped[str | None] = mapped_column(String(100))

    equipment: Mapped["Equipment"] = relationship()


class GCImport(Base):
    __tablename__ = "gc_imports"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    test_request_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("test_requests.id"), nullable=False)
    equipment_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), ForeignKey("equipment.id", ondelete="SET NULL"))
    import_format: Mapped[str] = mapped_column(String(20), nullable=False)
    original_filename: Mapped[str | None] = mapped_column(String(255))
    file_path: Mapped[str] = mapped_column(String(500), nullable=False)
    imported_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow)
    imported_by_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    peaks: Mapped[list] = mapped_column(JSONB, nullable=False, default=list)
    run_conditions: Mapped[dict | None] = mapped_column(JSONB)

    test_request: Mapped["TestRequest"] = relationship()
    equipment: Mapped["Equipment | None"] = relationship()
    imported_by: Mapped["User"] = relationship()
