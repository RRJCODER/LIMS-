import uuid
from datetime import date, timedelta
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.database import get_db
from app.auth.permissions import require_analyst, require_supervisor
from app.models.equipment import Equipment, CalibrationRecord, MaintenanceLog, EquipmentStatus
from app.models.user import User
from app.dependencies import get_current_user

router = APIRouter(prefix="/equipment", tags=["equipment"])


class EquipmentOut(BaseModel):
    id: uuid.UUID
    lab_id: str
    name: str
    manufacturer: str
    model: str
    serial_number: str
    equipment_type: str
    status: EquipmentStatus
    next_calibration_date: date | None
    comm_protocol: str | None
    comm_port: str | None

    model_config = {"from_attributes": True}


class EquipmentCreate(BaseModel):
    lab_id: str
    name: str
    manufacturer: str
    model: str
    serial_number: str
    equipment_type: str
    location: str | None = None
    calibration_interval_days: int | None = None
    comm_protocol: str | None = None
    comm_port: str | None = None
    comm_baud_rate: int | None = None
    notes: str | None = None


class CalibrationCreate(BaseModel):
    calibration_date: date
    calibration_type: str = "internal"
    external_provider: str | None = None
    certificate_number: str | None = None
    result: str = "pass"
    due_date: date
    notes: str | None = None


@router.get("/", response_model=list[EquipmentOut])
async def list_equipment(db: AsyncSession = Depends(get_db), _=Depends(require_analyst)):
    result = await db.execute(select(Equipment).where(Equipment.status != EquipmentStatus.retired).order_by(Equipment.lab_id))
    return result.scalars().all()


@router.post("/", response_model=EquipmentOut, status_code=201)
async def create_equipment(
    body: EquipmentCreate,
    db: AsyncSession = Depends(get_db),
    _=Depends(require_supervisor),
):
    eq = Equipment(**body.model_dump())
    db.add(eq)
    await db.flush()
    return eq


@router.get("/due-calibration")
async def due_calibration(days_ahead: int = 30, db: AsyncSession = Depends(get_db), _=Depends(require_analyst)):
    cutoff = date.today() + timedelta(days=days_ahead)
    result = await db.execute(
        select(Equipment).where(
            Equipment.next_calibration_date <= cutoff,
            Equipment.status == EquipmentStatus.active,
        ).order_by(Equipment.next_calibration_date)
    )
    return result.scalars().all()


@router.get("/{eq_id}/calibrations")
async def list_calibrations(eq_id: uuid.UUID, db: AsyncSession = Depends(get_db), _=Depends(require_analyst)):
    result = await db.execute(
        select(CalibrationRecord).where(CalibrationRecord.equipment_id == eq_id).order_by(CalibrationRecord.calibration_date.desc())
    )
    return result.scalars().all()


@router.post("/{eq_id}/calibrations", status_code=201)
async def create_calibration(
    eq_id: uuid.UUID,
    body: CalibrationCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_supervisor),
):
    cal = CalibrationRecord(equipment_id=eq_id, performed_by_id=current_user.id, **body.model_dump())
    db.add(cal)
    # Update equipment calibration dates
    eq_q = await db.execute(select(Equipment).where(Equipment.id == eq_id))
    eq = eq_q.scalar_one_or_none()
    if eq:
        eq.last_calibration_date = body.calibration_date
        eq.next_calibration_date = body.due_date
    await db.flush()
    return {"id": str(cal.id)}
