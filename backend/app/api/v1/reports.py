import uuid
from datetime import date
from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import FileResponse
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from pathlib import Path

from app.database import get_db
from app.auth.permissions import require_analyst, require_supervisor
from app.models.report import CertificateOfAnalysis
from app.models.user import User
from app.dependencies import get_current_user
from app.services.report_service import generate_coa_pdf, generate_coa_number
from app.services.audit_service import log_action
from app.models.audit import AuditAction

router = APIRouter(prefix="/reports", tags=["reports"])


class CoACreate(BaseModel):
    sample_id: uuid.UUID
    notes: str | None = None


@router.get("/coa")
async def list_coas(db: AsyncSession = Depends(get_db), _=Depends(require_analyst)):
    result = await db.execute(select(CertificateOfAnalysis).order_by(CertificateOfAnalysis.created_at.desc()))
    return result.scalars().all()


@router.post("/coa", status_code=201)
async def create_coa(
    body: CoACreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_supervisor),
):
    coa_number = await generate_coa_number(db)
    coa = CertificateOfAnalysis(
        coa_number=coa_number,
        sample_id=body.sample_id,
        issued_by_id=current_user.id,
        issue_date=date.today(),
        notes=body.notes,
    )
    db.add(coa)
    await db.flush()

    try:
        pdf_path = await generate_coa_pdf(db, coa)
    except Exception as e:
        # PDF generation failure is non-fatal in dev (WeasyPrint deps may not be installed)
        pdf_path = None

    await log_action(db, current_user, AuditAction.create, "coa", str(coa.id))
    return {"id": str(coa.id), "coa_number": coa_number, "pdf_path": pdf_path}


@router.get("/coa/{coa_id}/pdf")
async def get_coa_pdf(
    coa_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_analyst),
):
    coa_q = await db.execute(select(CertificateOfAnalysis).where(CertificateOfAnalysis.id == coa_id))
    coa = coa_q.scalar_one_or_none()
    if not coa:
        raise HTTPException(status_code=404, detail="CoA not found")
    if not coa.pdf_path or not Path(coa.pdf_path).exists():
        raise HTTPException(status_code=404, detail="PDF not yet generated")
    await log_action(db, current_user, AuditAction.print, "coa", str(coa_id))
    return FileResponse(coa.pdf_path, media_type="application/pdf", filename=f"{coa.coa_number}.pdf")
