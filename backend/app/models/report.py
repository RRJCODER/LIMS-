import uuid
from datetime import datetime, date
from sqlalchemy import String, Boolean, DateTime, Date, Integer, ForeignKey, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID

from app.database import Base


class CertificateOfAnalysis(Base):
    __tablename__ = "certificates_of_analysis"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    coa_number: Mapped[str] = mapped_column(String(50), unique=True, nullable=False, index=True)
    sample_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("samples.id"), nullable=False)
    issued_by_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    approved_by_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="SET NULL"))
    issue_date: Mapped[date] = mapped_column(Date, nullable=False)
    revision: Mapped[int] = mapped_column(Integer, default=1)
    status: Mapped[str] = mapped_column(String(20), nullable=False, default="draft")
    overall_compliance: Mapped[str | None] = mapped_column(String(100))
    pdf_path: Mapped[str | None] = mapped_column(String(500))
    pdf_hash: Mapped[str | None] = mapped_column(String(64))
    client_sent_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    notes: Mapped[str | None] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow)

    sample: Mapped["Sample"] = relationship()
    issued_by: Mapped["User"] = relationship(foreign_keys=[issued_by_id])
    approved_by: Mapped["User | None"] = relationship(foreign_keys=[approved_by_id])


class ReportTemplate(Base):
    __tablename__ = "report_templates"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    template_path: Mapped[str] = mapped_column(String(500), nullable=False)
    is_default: Mapped[bool] = mapped_column(Boolean, default=False)
    logo_path: Mapped[str | None] = mapped_column(String(500))
    lab_name: Mapped[str | None] = mapped_column(String(500))
    accreditation_number: Mapped[str | None] = mapped_column(String(100))
    lab_address: Mapped[str | None] = mapped_column(Text)
    lab_phone: Mapped[str | None] = mapped_column(String(50))
    lab_email: Mapped[str | None] = mapped_column(String(255))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow)
