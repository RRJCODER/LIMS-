import uuid
from datetime import date
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.database import get_db
from app.auth.permissions import require_analyst, require_supervisor
from app.models.qc import QCBatch, QCResult, ControlChart, WestgardViolation, QCType
from app.models.user import User
from app.dependencies import get_current_user
from app.services.qc_service import evaluate_westgard, compute_chart_limits

router = APIRouter(prefix="/qc", tags=["qc"])


class QCBatchCreate(BaseModel):
    method_id: uuid.UUID
    analyte_id: uuid.UUID
    qc_type: QCType
    run_date: date
    notes: str | None = None


class QCResultCreate(BaseModel):
    analyte_id: uuid.UUID
    expected_value: float | None = None
    measured_value: float
    unit: str
    instrument_id: uuid.UUID | None = None


@router.get("/batches")
async def list_batches(db: AsyncSession = Depends(get_db), _=Depends(require_analyst)):
    result = await db.execute(select(QCBatch).order_by(QCBatch.run_date.desc()))
    return result.scalars().all()


@router.post("/batches", status_code=201)
async def create_batch(
    body: QCBatchCreate,
    results: list[QCResultCreate],
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_analyst),
):
    from datetime import datetime
    batch_code = f"QC-{body.run_date.strftime('%Y%m%d')}-{uuid.uuid4().hex[:6].upper()}"
    batch = QCBatch(batch_code=batch_code, analyst_id=current_user.id, **body.model_dump())
    db.add(batch)
    await db.flush()

    violations = []
    for r in results:
        qc_result = QCResult(
            qc_batch_id=batch.id,
            analyte_id=r.analyte_id,
            expected_value=r.expected_value,
            measured_value=r.measured_value,
            unit=r.unit,
            instrument_id=r.instrument_id,
        )
        if r.expected_value:
            qc_result.percent_recovery = (r.measured_value / r.expected_value) * 100
        db.add(qc_result)
        await db.flush()

        viols = await evaluate_westgard(db, r.analyte_id, body.method_id, qc_result)
        violations.extend([v.rule for v in viols])

    return {"batch_id": str(batch.id), "violations": violations}


@router.get("/charts")
async def list_charts(db: AsyncSession = Depends(get_db), _=Depends(require_analyst)):
    result = await db.execute(select(ControlChart).where(ControlChart.is_active == True))
    return result.scalars().all()


@router.get("/charts/{chart_id}/data")
async def get_chart_data(
    chart_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    _=Depends(require_analyst),
):
    chart_q = await db.execute(select(ControlChart).where(ControlChart.id == chart_id))
    chart = chart_q.scalar_one_or_none()
    if not chart:
        raise HTTPException(status_code=404, detail="Chart not found")

    results = await db.execute(
        select(QCResult)
        .where(QCResult.analyte_id == chart.analyte_id)
        .order_by(QCResult.run_at)
        .limit(100)
    )
    rows = results.scalars().all()

    return {
        "chart": {
            "mean": chart.mean, "sd": chart.sd,
            "ucl": chart.ucl, "lcl": chart.lcl,
            "uwl": chart.uwl, "lwl": chart.lwl,
        },
        "data": [
            {"date": r.run_at.isoformat(), "value": r.measured_value,
             "z_score": r.z_score, "id": str(r.id)}
            for r in rows
        ],
    }


@router.get("/violations")
async def list_violations(resolved: bool | None = None, db: AsyncSession = Depends(get_db), _=Depends(require_analyst)):
    q = select(WestgardViolation).order_by(WestgardViolation.created_at.desc())
    if resolved is not None:
        q = q.where(WestgardViolation.resolved == resolved)
    result = await db.execute(q)
    return result.scalars().all()


@router.get("/summary")
async def qc_summary(db: AsyncSession = Depends(get_db), _=Depends(require_analyst)):
    unresolved = await db.execute(
        select(WestgardViolation).where(WestgardViolation.resolved == False)
    )
    return {"unresolved_violations": len(unresolved.scalars().all())}
