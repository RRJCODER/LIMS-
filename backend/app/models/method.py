import uuid
import enum
from datetime import datetime, date
from sqlalchemy import String, Boolean, Enum, DateTime, Date, Float, Integer, ForeignKey, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID

from app.database import Base


class MethodStatus(str, enum.Enum):
    draft = "draft"
    under_review = "under_review"
    approved = "approved"
    obsolete = "obsolete"


class AnalyticalMethod(Base):
    __tablename__ = "analytical_methods"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    code: Mapped[str] = mapped_column(String(50), unique=True, nullable=False, index=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    name_es: Mapped[str] = mapped_column(String(255), nullable=False, default="")
    reference_standard: Mapped[str | None] = mapped_column(String(255))
    category: Mapped[str] = mapped_column(String(50), nullable=False)
    instrument_type: Mapped[str | None] = mapped_column(String(50))
    status: Mapped[MethodStatus] = mapped_column(Enum(MethodStatus), nullable=False, default=MethodStatus.draft)
    current_version_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), ForeignKey("method_versions.id", use_alter=True, name="fk_method_current_version"), nullable=True)
    created_by_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow)

    versions: Mapped[list["MethodVersion"]] = relationship(back_populates="method", foreign_keys="MethodVersion.method_id")
    analytes: Mapped[list["Analyte"]] = relationship(back_populates="method")
    created_by: Mapped["User"] = relationship(foreign_keys=[created_by_id])


class MethodVersion(Base):
    __tablename__ = "method_versions"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    method_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("analytical_methods.id"), nullable=False)
    version_number: Mapped[str] = mapped_column(String(20), nullable=False)
    content_path: Mapped[str | None] = mapped_column(String(500))
    change_summary: Mapped[str | None] = mapped_column(Text)
    authored_by_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    reviewed_by_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="SET NULL"))
    approved_by_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="SET NULL"))
    effective_date: Mapped[date | None] = mapped_column(Date)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow)

    method: Mapped["AnalyticalMethod"] = relationship(back_populates="versions", foreign_keys=[method_id])
    authored_by: Mapped["User"] = relationship(foreign_keys=[authored_by_id])


class Analyte(Base):
    __tablename__ = "analytes"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    method_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("analytical_methods.id"), nullable=False)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    name_es: Mapped[str] = mapped_column(String(255), nullable=False, default="")
    symbol: Mapped[str | None] = mapped_column(String(50))
    unit: Mapped[str] = mapped_column(String(50), nullable=False)
    decimal_places: Mapped[int] = mapped_column(Integer, default=2)
    lod: Mapped[float | None] = mapped_column(Float)
    loq: Mapped[float | None] = mapped_column(Float)
    uncertainty_percent: Mapped[float | None] = mapped_column(Float)
    uncertainty_coverage_factor: Mapped[float] = mapped_column(Float, default=2.0)
    sort_order: Mapped[int] = mapped_column(Integer, default=0)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)

    method: Mapped["AnalyticalMethod"] = relationship(back_populates="analytes")
    specifications: Mapped[list["AnalyteSpecification"]] = relationship(back_populates="analyte")
