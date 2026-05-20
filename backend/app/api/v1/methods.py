import uuid
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.database import get_db
from app.auth.permissions import require_analyst, require_supervisor
from app.models.method import AnalyticalMethod, MethodVersion, Analyte, MethodStatus
from app.models.user import User
from app.dependencies import get_current_user

router = APIRouter(prefix="/methods", tags=["methods"])


class MethodOut(BaseModel):
    id: uuid.UUID
    code: str
    name: str
    name_es: str
    reference_standard: str | None
    category: str
    instrument_type: str | None
    status: MethodStatus

    model_config = {"from_attributes": True}


class AnalyteOut(BaseModel):
    id: uuid.UUID
    name: str
    name_es: str
    symbol: str | None
    unit: str
    decimal_places: int
    lod: float | None
    loq: float | None
    uncertainty_percent: float | None
    sort_order: int

    model_config = {"from_attributes": True}


class AnalyteCreate(BaseModel):
    name: str
    name_es: str = ""
    symbol: str | None = None
    unit: str
    decimal_places: int = 2
    lod: float | None = None
    loq: float | None = None
    uncertainty_percent: float | None = None
    sort_order: int = 0


@router.get("/", response_model=list[MethodOut])
async def list_methods(db: AsyncSession = Depends(get_db), _=Depends(require_analyst)):
    result = await db.execute(select(AnalyticalMethod).order_by(AnalyticalMethod.code))
    return result.scalars().all()


@router.get("/{method_id}", response_model=MethodOut)
async def get_method(method_id: uuid.UUID, db: AsyncSession = Depends(get_db), _=Depends(require_analyst)):
    result = await db.execute(select(AnalyticalMethod).where(AnalyticalMethod.id == method_id))
    method = result.scalar_one_or_none()
    if not method:
        raise HTTPException(status_code=404, detail="Method not found")
    return method


@router.get("/{method_id}/analytes", response_model=list[AnalyteOut])
async def list_analytes(method_id: uuid.UUID, db: AsyncSession = Depends(get_db), _=Depends(require_analyst)):
    result = await db.execute(
        select(Analyte).where(Analyte.method_id == method_id, Analyte.is_active == True).order_by(Analyte.sort_order)
    )
    return result.scalars().all()


@router.post("/{method_id}/analytes", response_model=AnalyteOut, status_code=201)
async def create_analyte(
    method_id: uuid.UUID,
    body: AnalyteCreate,
    db: AsyncSession = Depends(get_db),
    _=Depends(require_supervisor),
):
    analyte = Analyte(method_id=method_id, **body.model_dump())
    db.add(analyte)
    await db.flush()
    return analyte
