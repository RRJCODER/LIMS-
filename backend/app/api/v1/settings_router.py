import uuid, shutil, os
from pathlib import Path
from fastapi import APIRouter, Depends, UploadFile, File, HTTPException
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.database import get_db
from app.auth.permissions import require_supervisor, require_analyst
from app.models.specification import ProductQualityGrade, AnalyteSpecification
from app.models.report import ReportTemplate
from app.models.user import User
from app.dependencies import get_current_user
from app.config import settings

router = APIRouter(prefix="/settings", tags=["settings"])


class GradeCreate(BaseModel):
    code: str
    name_es: str
    name_en: str
    description: str | None = None
    regulatory_reference: str | None = None
    is_regulatory: bool = True


class SpecUpdate(BaseModel):
    min_limit: float | None = None
    max_limit: float | None = None
    limit_note: str | None = None
    uncertainty_override: float | None = None


class LabProfile(BaseModel):
    lab_name: str | None = None
    accreditation_number: str | None = None
    lab_address: str | None = None
    lab_phone: str | None = None
    lab_email: str | None = None


@router.get("/quality-grades")
async def list_grades(db: AsyncSession = Depends(get_db), _=Depends(require_analyst)):
    result = await db.execute(select(ProductQualityGrade).where(ProductQualityGrade.is_active == True).order_by(ProductQualityGrade.code))
    return result.scalars().all()


@router.post("/quality-grades", status_code=201)
async def create_grade(
    body: GradeCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_supervisor),
):
    grade = ProductQualityGrade(created_by_id=current_user.id, **body.model_dump())
    db.add(grade)
    await db.flush()
    return {"id": str(grade.id), "code": grade.code}


@router.get("/specifications")
async def get_specs(db: AsyncSession = Depends(get_db), _=Depends(require_analyst)):
    result = await db.execute(select(AnalyteSpecification).where(AnalyteSpecification.is_active == True))
    return result.scalars().all()


@router.put("/specifications/{analyte_id}/{grade_id}")
async def update_spec(
    analyte_id: uuid.UUID,
    grade_id: uuid.UUID,
    body: SpecUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_supervisor),
):
    result = await db.execute(
        select(AnalyteSpecification).where(
            AnalyteSpecification.analyte_id == analyte_id,
            AnalyteSpecification.quality_grade_id == grade_id,
        )
    )
    spec = result.scalar_one_or_none()
    if spec:
        for k, v in body.model_dump(exclude_none=True).items():
            setattr(spec, k, v)
        spec.updated_by_id = current_user.id
    else:
        spec = AnalyteSpecification(
            analyte_id=analyte_id,
            quality_grade_id=grade_id,
            updated_by_id=current_user.id,
            **body.model_dump(),
        )
        db.add(spec)
    await db.flush()
    return {"analyte_id": str(analyte_id), "grade_id": str(grade_id)}


@router.get("/lab-profile")
async def get_lab_profile(db: AsyncSession = Depends(get_db), _=Depends(require_analyst)):
    result = await db.execute(select(ReportTemplate).where(ReportTemplate.is_default == True).limit(1))
    tmpl = result.scalar_one_or_none()
    if not tmpl:
        return {"lab_name": settings.LAB_NAME, "accreditation_number": settings.LAB_ACCREDITATION_NUMBER, "logo_url": None}
    logo_url = f"/media/logos/{Path(tmpl.logo_path).name}" if tmpl.logo_path else None
    return {
        "lab_name": tmpl.lab_name or settings.LAB_NAME,
        "accreditation_number": tmpl.accreditation_number or settings.LAB_ACCREDITATION_NUMBER,
        "lab_address": tmpl.lab_address,
        "lab_phone": tmpl.lab_phone,
        "lab_email": tmpl.lab_email,
        "logo_url": logo_url,
    }


@router.put("/lab-profile")
async def update_lab_profile(
    body: LabProfile,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_supervisor),
):
    result = await db.execute(select(ReportTemplate).where(ReportTemplate.is_default == True).limit(1))
    tmpl = result.scalar_one_or_none()
    if not tmpl:
        tmpl = ReportTemplate(name="Default", template_path="coa_olive_oil.html", is_default=True)
        db.add(tmpl)
    for k, v in body.model_dump(exclude_none=True).items():
        setattr(tmpl, k, v)
    await db.flush()
    return {"updated": True}


@router.post("/lab-profile/logo")
async def upload_logo(
    file: UploadFile = File(...),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_supervisor),
):
    logo_dir = Path(settings.MEDIA_ROOT) / "logos"
    logo_dir.mkdir(parents=True, exist_ok=True)
    dest = logo_dir / file.filename
    with open(dest, "wb") as f:
        shutil.copyfileobj(file.file, f)

    result = await db.execute(select(ReportTemplate).where(ReportTemplate.is_default == True).limit(1))
    tmpl = result.scalar_one_or_none()
    if not tmpl:
        tmpl = ReportTemplate(name="Default", template_path="coa_olive_oil.html", is_default=True)
        db.add(tmpl)
    tmpl.logo_path = str(dest)
    await db.flush()
    return {"logo_path": str(dest), "filename": file.filename}
