import uuid
import enum
from datetime import datetime, date
from sqlalchemy import String, Boolean, Enum, DateTime, Date, ForeignKey, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID

from app.database import Base


class Role(str, enum.Enum):
    admin = "admin"
    supervisor = "supervisor"
    analyst = "analyst"
    viewer = "viewer"
    client = "client"


class User(Base):
    __tablename__ = "users"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    email: Mapped[str] = mapped_column(String(255), unique=True, nullable=False, index=True)
    hashed_password: Mapped[str] = mapped_column(String(255), nullable=False)
    full_name: Mapped[str] = mapped_column(String(255), nullable=False)
    role: Mapped[Role] = mapped_column(Enum(Role), nullable=False, default=Role.analyst)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    lab_section: Mapped[str | None] = mapped_column(String(100))
    signature_image: Mapped[str | None] = mapped_column(String(500))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow)

    qualifications: Mapped[list["UserQualification"]] = relationship(back_populates="user", foreign_keys="UserQualification.user_id")
    training_records: Mapped[list["TrainingRecord"]] = relationship(back_populates="user")


class UserQualification(Base):
    __tablename__ = "user_qualifications"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    method_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("analytical_methods.id"), nullable=False)
    qualified_by_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    qualification_date: Mapped[date] = mapped_column(Date, nullable=False)
    expiry_date: Mapped[date | None] = mapped_column(Date)
    certificate_path: Mapped[str | None] = mapped_column(String(500))
    notes: Mapped[str | None] = mapped_column(Text)

    user: Mapped["User"] = relationship(back_populates="qualifications", foreign_keys=[user_id])
    qualified_by: Mapped["User"] = relationship(foreign_keys=[qualified_by_id])


class TrainingRecord(Base):
    __tablename__ = "training_records"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    training_title: Mapped[str] = mapped_column(String(255), nullable=False)
    training_date: Mapped[date] = mapped_column(Date, nullable=False)
    trainer: Mapped[str] = mapped_column(String(255), nullable=False)
    evidence_path: Mapped[str | None] = mapped_column(String(500))
    notes: Mapped[str | None] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow)

    user: Mapped["User"] = relationship(back_populates="training_records")
