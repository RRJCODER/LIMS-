import uuid
from datetime import datetime
from sqlalchemy import String, Boolean, Float, ForeignKey, Text, DateTime
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID

from app.database import Base


class ProductQualityGrade(Base):
    __tablename__ = "product_quality_grades"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    code: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)
    name_es: Mapped[str] = mapped_column(String(200), nullable=False)
    name_en: Mapped[str] = mapped_column(String(200), nullable=False)
    description: Mapped[str | None] = mapped_column(Text)
    regulatory_reference: Mapped[str | None] = mapped_column(String(255))
    is_regulatory: Mapped[bool] = mapped_column(Boolean, default=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_by_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="SET NULL"))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow)

    specifications: Mapped[list["AnalyteSpecification"]] = relationship(back_populates="quality_grade")


class AnalyteSpecification(Base):
    __tablename__ = "analyte_specifications"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    analyte_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("analytes.id"), nullable=False)
    quality_grade_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("product_quality_grades.id"), nullable=False)
    min_limit: Mapped[float | None] = mapped_column(Float)
    max_limit: Mapped[float | None] = mapped_column(Float)
    limit_note: Mapped[str | None] = mapped_column(String(500))
    uncertainty_override: Mapped[float | None] = mapped_column(Float)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    updated_by_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="SET NULL"))
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow)

    analyte: Mapped["Analyte"] = relationship(back_populates="specifications")
    quality_grade: Mapped["ProductQualityGrade"] = relationship(back_populates="specifications")
    updated_by: Mapped["User | None"] = relationship(foreign_keys=[updated_by_id])
