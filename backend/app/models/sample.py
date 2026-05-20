import uuid
import enum
from datetime import datetime, date
from sqlalchemy import String, Boolean, Enum, DateTime, Date, Float, Integer, ForeignKey, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID

from app.database import Base


class SampleStatus(str, enum.Enum):
    received = "received"
    in_preparation = "in_preparation"
    in_analysis = "in_analysis"
    qc_review = "qc_review"
    supervisor_review = "supervisor_review"
    approved = "approved"
    reported = "reported"
    archived = "archived"
    rejected = "rejected"


class SampleMatrix(str, enum.Enum):
    extra_virgin_olive_oil = "extra_virgin_olive_oil"
    virgin_olive_oil = "virgin_olive_oil"
    refined_olive_oil = "refined_olive_oil"
    olive_pomace_oil = "olive_pomace_oil"
    blend = "blend"
    other = "other"


class Sample(Base):
    __tablename__ = "samples"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    lab_code: Mapped[str] = mapped_column(String(50), unique=True, nullable=False, index=True)
    barcode: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    client_reference: Mapped[str | None] = mapped_column(String(100))
    client_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="SET NULL"))
    client_name: Mapped[str] = mapped_column(String(255), nullable=False)
    client_email: Mapped[str | None] = mapped_column(String(255))
    matrix: Mapped[SampleMatrix] = mapped_column(Enum(SampleMatrix), nullable=False)
    declared_grade_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), ForeignKey("product_quality_grades.id", ondelete="SET NULL"))
    sample_description: Mapped[str | None] = mapped_column(Text)
    origin_country: Mapped[str | None] = mapped_column(String(100))
    harvest_year: Mapped[int | None] = mapped_column(Integer)
    producer: Mapped[str | None] = mapped_column(String(255))
    quantity_received_ml: Mapped[float | None] = mapped_column(Float)
    container_type: Mapped[str | None] = mapped_column(String(100))
    receipt_date: Mapped[date] = mapped_column(Date, nullable=False)
    due_date: Mapped[date | None] = mapped_column(Date)
    status: Mapped[SampleStatus] = mapped_column(Enum(SampleStatus), nullable=False, default=SampleStatus.received)
    priority: Mapped[str] = mapped_column(String(20), default="normal")
    storage_location: Mapped[str | None] = mapped_column(String(100))
    storage_temperature: Mapped[float | None] = mapped_column(Float)
    received_by_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    notes: Mapped[str | None] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow)

    received_by: Mapped["User"] = relationship(foreign_keys=[received_by_id])
    declared_grade: Mapped["ProductQualityGrade | None"] = relationship()
    custody_chain: Mapped[list["SampleCustody"]] = relationship(back_populates="sample", order_by="SampleCustody.transferred_at")
    attachments: Mapped[list["SampleAttachment"]] = relationship(back_populates="sample")
    test_requests: Mapped[list["TestRequest"]] = relationship(back_populates="sample")


class SampleCustody(Base):
    __tablename__ = "sample_custody"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    sample_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("samples.id"), nullable=False)
    from_user_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="SET NULL"))
    to_user_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    transferred_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow, nullable=False)
    location: Mapped[str | None] = mapped_column(String(200))
    notes: Mapped[str | None] = mapped_column(Text)

    sample: Mapped["Sample"] = relationship(back_populates="custody_chain")
    from_user: Mapped["User | None"] = relationship(foreign_keys=[from_user_id])
    to_user: Mapped["User"] = relationship(foreign_keys=[to_user_id])


class SampleAttachment(Base):
    __tablename__ = "sample_attachments"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    sample_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("samples.id"), nullable=False)
    filename: Mapped[str] = mapped_column(String(255), nullable=False)
    file_path: Mapped[str] = mapped_column(String(500), nullable=False)
    file_type: Mapped[str] = mapped_column(String(50), default="other")
    uploaded_by_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    uploaded_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow)

    sample: Mapped["Sample"] = relationship(back_populates="attachments")
    uploaded_by: Mapped["User"] = relationship()
