import uuid
import enum
from datetime import datetime, date
from sqlalchemy import String, Boolean, Enum, DateTime, Date, Integer, ForeignKey, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID

from app.database import Base


class DocumentType(str, enum.Enum):
    sop = "sop"
    method = "method"
    work_instruction = "work_instruction"
    quality_manual = "quality_manual"
    form = "form"
    policy = "policy"
    certificate = "certificate"
    external_standard = "external_standard"


class DocumentStatus(str, enum.Enum):
    draft = "draft"
    under_review = "under_review"
    approved = "approved"
    obsolete = "obsolete"
    withdrawn = "withdrawn"


class Document(Base):
    __tablename__ = "documents"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    doc_number: Mapped[str] = mapped_column(String(50), unique=True, nullable=False, index=True)
    title: Mapped[str] = mapped_column(String(500), nullable=False)
    document_type: Mapped[DocumentType] = mapped_column(Enum(DocumentType), nullable=False)
    status: Mapped[DocumentStatus] = mapped_column(Enum(DocumentStatus), nullable=False, default=DocumentStatus.draft)
    owner_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    current_version_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), ForeignKey("document_versions.id", use_alter=True, name="fk_document_current_version"), nullable=True)
    review_interval_months: Mapped[int | None] = mapped_column(Integer)
    next_review_date: Mapped[date | None] = mapped_column(Date)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow)

    owner: Mapped["User"] = relationship(foreign_keys=[owner_id])
    versions: Mapped[list["DocumentVersion"]] = relationship(back_populates="document", foreign_keys="DocumentVersion.document_id")


class DocumentVersion(Base):
    __tablename__ = "document_versions"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    document_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("documents.id"), nullable=False)
    version: Mapped[str] = mapped_column(String(20), nullable=False)
    file_path: Mapped[str] = mapped_column(String(500), nullable=False)
    file_hash: Mapped[str] = mapped_column(String(64), nullable=False)
    change_summary: Mapped[str] = mapped_column(Text, nullable=False)
    authored_by_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow)

    document: Mapped["Document"] = relationship(back_populates="versions", foreign_keys=[document_id])
    authored_by: Mapped["User"] = relationship()
    approvals: Mapped[list["ApprovalRecord"]] = relationship(back_populates="document_version")


class ApprovalRecord(Base):
    __tablename__ = "approval_records"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    document_version_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("document_versions.id"), nullable=False)
    step: Mapped[str] = mapped_column(String(50), nullable=False)
    approver_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    decision: Mapped[str] = mapped_column(String(20), nullable=False)
    comments: Mapped[str | None] = mapped_column(Text)
    decided_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow)

    document_version: Mapped["DocumentVersion"] = relationship(back_populates="approvals")
    approver: Mapped["User"] = relationship()
