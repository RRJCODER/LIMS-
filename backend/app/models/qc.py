import uuid
import enum
from datetime import datetime, date
from sqlalchemy import String, Boolean, Enum, DateTime, Date, Float, Integer, ForeignKey, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID

from app.database import Base


class QCType(str, enum.Enum):
    blank = "blank"
    method_blank = "method_blank"
    calibration_standard = "calibration_standard"
    control_standard = "control_standard"
    duplicate = "duplicate"
    spike = "spike"
    proficiency_sample = "proficiency_sample"


class WestgardRule(str, enum.Enum):
    rule_1_2s = "1_2s"
    rule_1_3s = "1_3s"
    rule_2_2s = "2_2s"
    rule_r_4s = "R_4s"
    rule_4_1s = "4_1s"
    rule_10x = "10x"


class QCBatch(Base):
    __tablename__ = "qc_batches"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    batch_code: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)
    method_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("analytical_methods.id"), nullable=False)
    analyte_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("analytes.id"), nullable=False)
    qc_type: Mapped[QCType] = mapped_column(Enum(QCType), nullable=False)
    analyst_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    run_date: Mapped[date] = mapped_column(Date, nullable=False)
    notes: Mapped[str | None] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow)

    method: Mapped["AnalyticalMethod"] = relationship()
    analyte: Mapped["Analyte"] = relationship()
    analyst: Mapped["User"] = relationship()
    qc_results: Mapped[list["QCResult"]] = relationship(back_populates="qc_batch")


class QCResult(Base):
    __tablename__ = "qc_results"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    qc_batch_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("qc_batches.id"), nullable=False)
    analyte_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("analytes.id"), nullable=False)
    expected_value: Mapped[float | None] = mapped_column(Float)
    measured_value: Mapped[float] = mapped_column(Float, nullable=False)
    unit: Mapped[str] = mapped_column(String(50), nullable=False)
    z_score: Mapped[float | None] = mapped_column(Float)
    percent_recovery: Mapped[float | None] = mapped_column(Float)
    run_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow)
    instrument_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), ForeignKey("equipment.id", ondelete="SET NULL"))

    qc_batch: Mapped["QCBatch"] = relationship(back_populates="qc_results")
    analyte: Mapped["Analyte"] = relationship()
    violations: Mapped[list["WestgardViolation"]] = relationship(back_populates="qc_result")


class ControlChart(Base):
    __tablename__ = "control_charts"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    method_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("analytical_methods.id"), nullable=False)
    analyte_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("analytes.id"), nullable=False)
    qc_type: Mapped[QCType] = mapped_column(Enum(QCType), nullable=False)
    established_from: Mapped[date] = mapped_column(Date, nullable=False)
    established_to: Mapped[date] = mapped_column(Date, nullable=False)
    n_points: Mapped[int] = mapped_column(Integer, nullable=False)
    mean: Mapped[float] = mapped_column(Float, nullable=False)
    sd: Mapped[float] = mapped_column(Float, nullable=False)
    ucl: Mapped[float] = mapped_column(Float, nullable=False)
    lcl: Mapped[float] = mapped_column(Float, nullable=False)
    uwl: Mapped[float] = mapped_column(Float, nullable=False)
    lwl: Mapped[float] = mapped_column(Float, nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_by_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow)

    method: Mapped["AnalyticalMethod"] = relationship()
    analyte: Mapped["Analyte"] = relationship()


class WestgardViolation(Base):
    __tablename__ = "westgard_violations"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    qc_result_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("qc_results.id"), nullable=False)
    rule_violated: Mapped[WestgardRule] = mapped_column(Enum(WestgardRule), nullable=False)
    severity: Mapped[str] = mapped_column(String(20), nullable=False)
    investigated_by_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="SET NULL"))
    investigation_notes: Mapped[str | None] = mapped_column(Text)
    resolved: Mapped[bool] = mapped_column(Boolean, default=False)
    resolved_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow)

    qc_result: Mapped["QCResult"] = relationship(back_populates="violations")
    investigated_by: Mapped["User | None"] = relationship(foreign_keys=[investigated_by_id])
