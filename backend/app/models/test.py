import uuid
import enum
from datetime import datetime, date
from sqlalchemy import String, Boolean, Enum, DateTime, Float, Integer, ForeignKey, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID

from app.database import Base


class TestStatus(str, enum.Enum):
    pending = "pending"
    in_progress = "in_progress"
    results_entered = "results_entered"
    qc_check = "qc_check"
    supervisor_review = "supervisor_review"
    approved = "approved"
    failed_qc = "failed_qc"
    retest_required = "retest_required"


class TestRequest(Base):
    __tablename__ = "test_requests"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    sample_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("samples.id"), nullable=False)
    method_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("analytical_methods.id"), nullable=False)
    method_version_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), ForeignKey("method_versions.id", ondelete="SET NULL"))
    assigned_analyst_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="SET NULL"))
    requested_by_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    priority: Mapped[str] = mapped_column(String(20), default="normal")
    status: Mapped[TestStatus] = mapped_column(Enum(TestStatus), nullable=False, default=TestStatus.pending)
    scheduled_date: Mapped[date | None] = mapped_column(DateTime(timezone=True))
    started_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    completed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    batch_id: Mapped[str | None] = mapped_column(String(50))
    notes: Mapped[str | None] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow)

    sample: Mapped["Sample"] = relationship(back_populates="test_requests")
    method: Mapped["AnalyticalMethod"] = relationship()
    method_version: Mapped["MethodVersion | None"] = relationship()
    assigned_analyst: Mapped["User | None"] = relationship(foreign_keys=[assigned_analyst_id])
    requested_by: Mapped["User"] = relationship(foreign_keys=[requested_by_id])
    results: Mapped[list["TestResult"]] = relationship(back_populates="test_request")


class TestResult(Base):
    __tablename__ = "test_results"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    test_request_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("test_requests.id"), nullable=False)
    analyte_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("analytes.id"), nullable=False)
    raw_value: Mapped[float | None] = mapped_column(Float)
    reported_value: Mapped[float | None] = mapped_column(Float)
    text_value: Mapped[str | None] = mapped_column(Text)
    unit: Mapped[str] = mapped_column(String(50), nullable=False)
    is_below_lod: Mapped[bool] = mapped_column(Boolean, default=False)
    is_below_loq: Mapped[bool] = mapped_column(Boolean, default=False)
    uncertainty: Mapped[float | None] = mapped_column(Float)
    in_spec: Mapped[bool | None] = mapped_column(Boolean)
    compliance_note: Mapped[str | None] = mapped_column(Text)
    instrument_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), ForeignKey("equipment.id", ondelete="SET NULL"))
    raw_instrument_reading_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), ForeignKey("raw_instrument_readings.id", ondelete="SET NULL"))
    entered_by_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    entered_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow)
    approved_by_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="SET NULL"))
    approved_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    replicate_number: Mapped[int] = mapped_column(Integer, default=1)
    dilution_factor: Mapped[float | None] = mapped_column(Float)
    sample_weight_g: Mapped[float | None] = mapped_column(Float)
    volume_ml: Mapped[float | None] = mapped_column(Float)

    test_request: Mapped["TestRequest"] = relationship(back_populates="results")
    analyte: Mapped["Analyte"] = relationship()
    entered_by: Mapped["User"] = relationship(foreign_keys=[entered_by_id])
    approved_by: Mapped["User | None"] = relationship(foreign_keys=[approved_by_id])
    instrument: Mapped["Equipment | None"] = relationship(foreign_keys=[instrument_id])
