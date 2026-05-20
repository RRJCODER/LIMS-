import uuid
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.database import get_db
from app.auth.permissions import require_analyst, require_supervisor
from app.models.test import TestRequest, TestResult, TestStatus
from app.models.sample import Sample
from app.models.method import Analyte
from app.models.user import User
from app.dependencies import get_current_user
from app.services.test_service import validate_result_compliance, calculate_uncertainty
from app.services.audit_service import log_action
from app.models.audit import AuditAction

router = APIRouter(prefix="/tests", tags=["tests"])


class TestRequestCreate(BaseModel):
    sample_id: uuid.UUID
    method_id: uuid.UUID
    priority: str = "normal"
    notes: str | None = None


class ResultCreate(BaseModel):
    analyte_id: uuid.UUID
    raw_value: float | None = None
    reported_value: float | None = None
    text_value: str | None = None
    unit: str
    is_below_lod: bool = False
    is_below_loq: bool = False
    dilution_factor: float | None = None
    sample_weight_g: float | None = None
    volume_ml: float | None = None
    instrument_id: uuid.UUID | None = None


class TestOut(BaseModel):
    id: uuid.UUID
    sample_id: uuid.UUID
    method_id: uuid.UUID
    status: TestStatus
    priority: str
    created_at: datetime

    model_config = {"from_attributes": True}


@router.get("/", response_model=list[TestOut])
async def list_tests(
    status_filter: str | None = None,
    db: AsyncSession = Depends(get_db),
    _=Depends(require_analyst),
):
    q = select(TestRequest).order_by(TestRequest.created_at.desc())
    if status_filter:
        q = q.where(TestRequest.status == status_filter)
    result = await db.execute(q)
    return result.scalars().all()


@router.post("/", response_model=TestOut, status_code=201)
async def create_test(
    body: TestRequestCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_analyst),
):
    test = TestRequest(
        requested_by_id=current_user.id,
        assigned_analyst_id=current_user.id,
        **body.model_dump(),
    )
    db.add(test)
    await db.flush()
    await log_action(db, current_user, AuditAction.create, "test_request", str(test.id))
    return test


@router.get("/{test_id}")
async def get_test(test_id: uuid.UUID, db: AsyncSession = Depends(get_db), _=Depends(require_analyst)):
    result = await db.execute(select(TestRequest).where(TestRequest.id == test_id))
    test = result.scalar_one_or_none()
    if not test:
        raise HTTPException(status_code=404, detail="Test not found")
    return test


@router.post("/{test_id}/results", status_code=201)
async def enter_results(
    test_id: uuid.UUID,
    results: list[ResultCreate],
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_analyst),
):
    test_q = await db.execute(select(TestRequest).where(TestRequest.id == test_id))
    test = test_q.scalar_one_or_none()
    if not test:
        raise HTTPException(status_code=404, detail="Test not found")

    sample_q = await db.execute(select(Sample).where(Sample.id == test.sample_id))
    sample = sample_q.scalar_one_or_none()

    created_ids = []
    for r in results:
        analyte_q = await db.execute(select(Analyte).where(Analyte.id == r.analyte_id))
        analyte = analyte_q.scalar_one_or_none()
        uncertainty = calculate_uncertainty(r.reported_value or r.raw_value, analyte.uncertainty_percent if analyte else None)

        result_row = TestResult(
            test_request_id=test_id,
            analyte_id=r.analyte_id,
            raw_value=r.raw_value,
            reported_value=r.reported_value,
            text_value=r.text_value,
            unit=r.unit,
            is_below_lod=r.is_below_lod,
            is_below_loq=r.is_below_loq,
            uncertainty=uncertainty,
            dilution_factor=r.dilution_factor,
            sample_weight_g=r.sample_weight_g,
            volume_ml=r.volume_ml,
            instrument_id=r.instrument_id,
            entered_by_id=current_user.id,
        )

        if sample and sample.declared_grade_id:
            in_spec, note = await validate_result_compliance(db, result_row, sample)
            result_row.in_spec = in_spec
            result_row.compliance_note = note

        db.add(result_row)
        await db.flush()
        created_ids.append(str(result_row.id))

    test.status = TestStatus.results_entered
    test.completed_at = datetime.utcnow()
    await log_action(db, current_user, AuditAction.create, "test_results", str(test_id),
                     new_value={"result_count": len(results)})
    return {"created": created_ids}


@router.post("/{test_id}/approve")
async def approve_test(
    test_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_supervisor),
):
    test_q = await db.execute(select(TestRequest).where(TestRequest.id == test_id))
    test = test_q.scalar_one_or_none()
    if not test:
        raise HTTPException(status_code=404, detail="Test not found")
    test.status = TestStatus.approved
    await log_action(db, current_user, AuditAction.approve, "test_request", str(test_id))
    return {"status": test.status}
