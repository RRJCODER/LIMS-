import uuid
from datetime import date
from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
import os, shutil
from pathlib import Path

from app.database import get_db
from app.dependencies import get_current_user
from app.auth.permissions import require_analyst
from app.models.sample import Sample, SampleCustody, SampleAttachment, SampleStatus, SampleMatrix
from app.models.user import User
from app.services.sample_service import generate_lab_code, generate_barcode_value, is_valid_transition
from app.services.audit_service import log_action
from app.models.audit import AuditAction
from app.config import settings

router = APIRouter(prefix="/samples", tags=["samples"])


class SampleCreate(BaseModel):
    client_name: str
    client_email: str | None = None
    client_reference: str | None = None
    matrix: SampleMatrix
    declared_grade_id: uuid.UUID | None = None
    sample_description: str | None = None
    origin_country: str | None = None
    harvest_year: int | None = None
    producer: str | None = None
    quantity_received_ml: float | None = None
    container_type: str | None = None
    receipt_date: date
    due_date: date | None = None
    priority: str = "normal"
    storage_location: str | None = None
    storage_temperature: float | None = None
    notes: str | None = None


class StatusUpdate(BaseModel):
    status: SampleStatus
    notes: str | None = None


class SampleOut(BaseModel):
    id: uuid.UUID
    lab_code: str
    barcode: str
    client_name: str
    matrix: SampleMatrix
    status: SampleStatus
    priority: str
    receipt_date: date
    due_date: date | None

    model_config = {"from_attributes": True}


@router.get("/", response_model=list[SampleOut])
async def list_samples(
    status_filter: str | None = None,
    db: AsyncSession = Depends(get_db),
    _=Depends(require_analyst),
):
    q = select(Sample).order_by(Sample.receipt_date.desc())
    if status_filter:
        q = q.where(Sample.status == status_filter)
    result = await db.execute(q)
    return result.scalars().all()


@router.post("/", response_model=SampleOut, status_code=status.HTTP_201_CREATED)
async def create_sample(
    body: SampleCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_analyst),
):
    lab_code = await generate_lab_code(db)
    barcode = generate_barcode_value(lab_code)
    sample = Sample(
        lab_code=lab_code,
        barcode=barcode,
        received_by_id=current_user.id,
        **body.model_dump(),
    )
    db.add(sample)
    await db.flush()
    # Record initial custody
    custody = SampleCustody(
        sample_id=sample.id,
        to_user_id=current_user.id,
        location=body.storage_location,
    )
    db.add(custody)
    await log_action(db, current_user, AuditAction.create, "sample", str(sample.id),
                     new_value={"lab_code": lab_code, "client": body.client_name})
    return sample


@router.get("/{sample_id}")
async def get_sample(
    sample_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    _=Depends(require_analyst),
):
    result = await db.execute(select(Sample).where(Sample.id == sample_id))
    sample = result.scalar_one_or_none()
    if not sample:
        raise HTTPException(status_code=404, detail="Sample not found")
    return sample


@router.patch("/{sample_id}/status")
async def update_status(
    sample_id: uuid.UUID,
    body: StatusUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_analyst),
):
    result = await db.execute(select(Sample).where(Sample.id == sample_id))
    sample = result.scalar_one_or_none()
    if not sample:
        raise HTTPException(status_code=404, detail="Sample not found")
    if not is_valid_transition(sample.status, body.status):
        raise HTTPException(status_code=400, detail=f"Invalid transition: {sample.status} → {body.status}")
    old_status = sample.status
    sample.status = body.status
    await log_action(db, current_user, AuditAction.update, "sample", str(sample_id),
                     old_value={"status": old_status}, new_value={"status": body.status})
    return {"id": str(sample_id), "status": sample.status}


@router.get("/{sample_id}/custody")
async def get_custody(sample_id: uuid.UUID, db: AsyncSession = Depends(get_db), _=Depends(require_analyst)):
    result = await db.execute(
        select(SampleCustody).where(SampleCustody.sample_id == sample_id).order_by(SampleCustody.transferred_at)
    )
    return result.scalars().all()


@router.post("/{sample_id}/attachments", status_code=status.HTTP_201_CREATED)
async def upload_attachment(
    sample_id: uuid.UUID,
    file: UploadFile = File(...),
    file_type: str = "other",
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_analyst),
):
    dest_dir = Path(settings.MEDIA_ROOT) / "attachments" / str(sample_id)
    dest_dir.mkdir(parents=True, exist_ok=True)
    dest = dest_dir / file.filename
    with open(dest, "wb") as f:
        shutil.copyfileobj(file.file, f)
    attachment = SampleAttachment(
        sample_id=sample_id,
        filename=file.filename,
        file_path=str(dest),
        file_type=file_type,
        uploaded_by_id=current_user.id,
    )
    db.add(attachment)
    await db.flush()
    return {"id": str(attachment.id), "filename": file.filename}
