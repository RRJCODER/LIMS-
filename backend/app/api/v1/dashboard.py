from datetime import date, timedelta
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func

from app.database import get_db
from app.auth.permissions import require_analyst
from app.models.sample import Sample, SampleStatus
from app.models.test import TestRequest, TestStatus
from app.models.qc import WestgardViolation
from app.models.equipment import Equipment, EquipmentStatus

router = APIRouter(prefix="/dashboard", tags=["dashboard"])


@router.get("/kpis")
async def get_kpis(db: AsyncSession = Depends(get_db), _=Depends(require_analyst)):
    pending_samples = await db.execute(
        select(func.count(Sample.id)).where(
            Sample.status.in_([SampleStatus.received, SampleStatus.in_preparation, SampleStatus.in_analysis])
        )
    )

    overdue = await db.execute(
        select(func.count(Sample.id)).where(
            Sample.due_date < date.today(),
            Sample.status.not_in([SampleStatus.reported, SampleStatus.archived, SampleStatus.rejected]),
        )
    )

    qc_violations = await db.execute(
        select(func.count(WestgardViolation.id)).where(WestgardViolation.resolved == False)
    )

    cal_due = await db.execute(
        select(func.count(Equipment.id)).where(
            Equipment.next_calibration_date <= date.today() + timedelta(days=30),
            Equipment.status == EquipmentStatus.active,
        )
    )

    pending_tests = await db.execute(
        select(func.count(TestRequest.id)).where(
            TestRequest.status.in_([TestStatus.pending, TestStatus.in_progress])
        )
    )

    return {
        "pending_samples": pending_samples.scalar_one(),
        "overdue_samples": overdue.scalar_one(),
        "open_qc_violations": qc_violations.scalar_one(),
        "calibrations_due_30d": cal_due.scalar_one(),
        "pending_tests": pending_tests.scalar_one(),
    }


@router.get("/sample-throughput")
async def sample_throughput(days: int = 30, db: AsyncSession = Depends(get_db), _=Depends(require_analyst)):
    since = date.today() - timedelta(days=days)
    result = await db.execute(
        select(
            func.date_trunc("day", Sample.receipt_date).label("day"),
            func.count(Sample.id).label("count"),
        )
        .where(Sample.receipt_date >= since)
        .group_by("day")
        .order_by("day")
    )
    return [{"date": str(row.day)[:10], "count": row.count} for row in result.all()]
