"""Result validation, uncertainty, compliance classification, and GC peak mapping."""
import uuid
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.models.test import TestResult
from app.models.specification import AnalyteSpecification
from app.models.sample import Sample


async def validate_result_compliance(
    db: AsyncSession,
    result: TestResult,
    sample: Sample,
) -> tuple[bool | None, str | None]:
    if result.reported_value is None:
        return None, None

    spec = await db.execute(
        select(AnalyteSpecification).where(
            AnalyteSpecification.analyte_id == result.analyte_id,
            AnalyteSpecification.quality_grade_id == sample.declared_grade_id,
            AnalyteSpecification.is_active == True,
        )
    )
    spec_row = spec.scalar_one_or_none()

    if not spec_row:
        return None, "No limits configured for this analyte/grade combination"

    val = result.reported_value
    note_parts = []

    if spec_row.min_limit is not None and val < spec_row.min_limit:
        note_parts.append(f"Below minimum {spec_row.min_limit}")
        return False, "; ".join(note_parts)

    if spec_row.max_limit is not None and val > spec_row.max_limit:
        note_parts.append(f"Exceeds maximum {spec_row.max_limit}")
        return False, "; ".join(note_parts)

    return True, spec_row.limit_note


def calculate_uncertainty(raw_value: float, uncertainty_percent: float | None, coverage_factor: float = 2.0) -> float | None:
    if uncertainty_percent is None or raw_value is None:
        return None
    return abs(raw_value) * (uncertainty_percent / 100) * coverage_factor


def classify_olive_oil(results: dict[str, float | None]) -> str:
    """Classify sample based on key chemical parameters per EU/IOC standards."""
    ffa = results.get("FFA")
    pv = results.get("PV")
    k232 = results.get("K232")
    k270 = results.get("K270")
    delta_k = results.get("DeltaK")
    fruitiness = results.get("Fruitiness")
    defect_median = results.get("DefectMedian")

    required = [ffa, pv]
    if any(v is None for v in required):
        return "Insufficient data"

    if (ffa <= 0.8 and pv <= 20
            and (k232 is None or k232 <= 2.50)
            and (k270 is None or k270 <= 0.22)
            and (delta_k is None or delta_k <= 0.01)
            and (fruitiness is None or fruitiness > 0)
            and (defect_median is None or defect_median == 0)):
        return "EVOO"

    if ffa <= 2.0 and pv <= 20:
        return "VOO"

    if ffa > 2.0:
        return "Lampante Virgin"

    return "Non-conforming"


def calculate_delta_k(k268: float, k270: float, k272: float) -> float:
    """EU Reg. 2568/91 Annex IX — delta extinction correction."""
    return k270 - (k268 + k272) / 2
