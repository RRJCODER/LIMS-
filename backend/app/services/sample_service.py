from datetime import datetime, date
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func

from app.models.sample import Sample


async def generate_lab_code(db: AsyncSession) -> str:
    today = date.today()
    prefix = f"LAB-{today.strftime('%Y%m%d')}-"
    result = await db.execute(
        select(func.count(Sample.id)).where(Sample.lab_code.like(f"{prefix}%"))
    )
    count = result.scalar_one() + 1
    return f"{prefix}{count:04d}"


def generate_barcode_value(lab_code: str) -> str:
    return lab_code.replace("-", "")


def get_status_transitions() -> dict:
    from app.models.sample import SampleStatus
    return {
        SampleStatus.received: [SampleStatus.in_preparation, SampleStatus.rejected],
        SampleStatus.in_preparation: [SampleStatus.in_analysis, SampleStatus.rejected],
        SampleStatus.in_analysis: [SampleStatus.qc_review, SampleStatus.rejected],
        SampleStatus.qc_review: [SampleStatus.supervisor_review, SampleStatus.in_analysis],
        SampleStatus.supervisor_review: [SampleStatus.approved, SampleStatus.in_analysis],
        SampleStatus.approved: [SampleStatus.reported],
        SampleStatus.reported: [SampleStatus.archived],
        SampleStatus.archived: [],
        SampleStatus.rejected: [],
    }


def is_valid_transition(current: str, new: str) -> bool:
    from app.models.sample import SampleStatus
    transitions = get_status_transitions()
    current_status = SampleStatus(current)
    new_status = SampleStatus(new)
    return new_status in transitions.get(current_status, [])
