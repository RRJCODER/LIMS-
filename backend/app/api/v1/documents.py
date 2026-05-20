import uuid, hashlib, shutil
from pathlib import Path
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, status
from fastapi.responses import FileResponse
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.database import get_db
from app.auth.permissions import require_analyst, require_supervisor
from app.models.document import Document, DocumentVersion, DocumentStatus, DocumentType
from app.models.user import User
from app.dependencies import get_current_user
from app.config import settings
from app.services.audit_service import log_action
from app.models.audit import AuditAction

router = APIRouter(prefix="/documents", tags=["documents"])


class DocumentCreate(BaseModel):
    doc_number: str
    title: str
    document_type: DocumentType
    review_interval_months: int | None = None


class DocumentOut(BaseModel):
    id: uuid.UUID
    doc_number: str
    title: str
    document_type: DocumentType
    status: DocumentStatus

    model_config = {"from_attributes": True}


@router.get("/", response_model=list[DocumentOut])
async def list_documents(db: AsyncSession = Depends(get_db), _=Depends(require_analyst)):
    result = await db.execute(select(Document).where(Document.status != DocumentStatus.withdrawn).order_by(Document.doc_number))
    return result.scalars().all()


@router.post("/", response_model=DocumentOut, status_code=201)
async def create_document(
    body: DocumentCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_supervisor),
):
    doc = Document(owner_id=current_user.id, **body.model_dump())
    db.add(doc)
    await db.flush()
    return doc


@router.get("/{doc_id}", response_model=DocumentOut)
async def get_document(doc_id: uuid.UUID, db: AsyncSession = Depends(get_db), _=Depends(require_analyst)):
    result = await db.execute(select(Document).where(Document.id == doc_id))
    doc = result.scalar_one_or_none()
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")
    return doc


@router.post("/{doc_id}/versions", status_code=201)
async def upload_version(
    doc_id: uuid.UUID,
    version: str,
    change_summary: str,
    file: UploadFile = File(...),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_supervisor),
):
    doc_q = await db.execute(select(Document).where(Document.id == doc_id))
    doc = doc_q.scalar_one_or_none()
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")

    dest_dir = Path(settings.MEDIA_ROOT) / "documents" / str(doc_id)
    dest_dir.mkdir(parents=True, exist_ok=True)
    dest = dest_dir / f"v{version}_{file.filename}"

    content = await file.read()
    with open(dest, "wb") as f:
        f.write(content)
    file_hash = hashlib.sha256(content).hexdigest()

    dv = DocumentVersion(
        document_id=doc_id,
        version=version,
        file_path=str(dest),
        file_hash=file_hash,
        change_summary=change_summary,
        authored_by_id=current_user.id,
    )
    db.add(dv)
    await db.flush()
    doc.current_version_id = dv.id
    await log_action(db, current_user, AuditAction.upload, "document_version", str(dv.id))
    return {"id": str(dv.id), "hash": file_hash}


@router.get("/{doc_id}/versions/{version_id}/download")
async def download_version(
    doc_id: uuid.UUID,
    version_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_analyst),
):
    dv_q = await db.execute(select(DocumentVersion).where(DocumentVersion.id == version_id))
    dv = dv_q.scalar_one_or_none()
    if not dv or not Path(dv.file_path).exists():
        raise HTTPException(status_code=404, detail="File not found")
    await log_action(db, current_user, AuditAction.download, "document_version", str(version_id))
    return FileResponse(dv.file_path, filename=Path(dv.file_path).name)
