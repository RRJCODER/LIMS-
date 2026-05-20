"""Westgard rule engine for ISO 17025 §7.7 QC compliance."""
from datetime import date
from typing import NamedTuple
import uuid

import numpy as np
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.models.qc import QCResult, ControlChart, WestgardViolation, WestgardRule


class ViolationResult(NamedTuple):
    rule: WestgardRule
    severity: str
    description: str


async def get_active_chart(db: AsyncSession, analyte_id: uuid.UUID, method_id: uuid.UUID) -> ControlChart | None:
    result = await db.execute(
        select(ControlChart).where(
            ControlChart.analyte_id == analyte_id,
            ControlChart.method_id == method_id,
            ControlChart.is_active == True,
        ).order_by(ControlChart.created_at.desc())
    )
    return result.scalar_one_or_none()


async def get_recent_qc_values(db: AsyncSession, analyte_id: uuid.UUID, n: int = 10) -> list[float]:
    result = await db.execute(
        select(QCResult.measured_value)
        .where(QCResult.analyte_id == analyte_id)
        .order_by(QCResult.run_at.desc())
        .limit(n)
    )
    rows = result.scalars().all()
    return list(reversed(rows))


def apply_westgard_rules(values: list[float], chart: ControlChart) -> list[ViolationResult]:
    violations: list[ViolationResult] = []
    if not values or not chart:
        return violations

    mean = chart.mean
    sd = chart.sd

    deviations = [(v - mean) / sd if sd > 0 else 0 for v in values]

    # 1_2s — Warning: last value > mean±2SD
    if abs(deviations[-1]) > 2:
        violations.append(ViolationResult(WestgardRule.rule_1_2s, "warning",
                                          f"Value {values[-1]:.3f} outside mean±2SD"))

    # 1_3s — Reject: last value > mean±3SD
    if abs(deviations[-1]) > 3:
        violations.append(ViolationResult(WestgardRule.rule_1_3s, "reject",
                                          f"Value {values[-1]:.3f} outside mean±3SD"))

    if len(deviations) >= 2:
        last2 = deviations[-2:]
        # 2_2s — Reject: 2 consecutive > mean±2SD same side
        if all(d > 2 for d in last2) or all(d < -2 for d in last2):
            violations.append(ViolationResult(WestgardRule.rule_2_2s, "reject",
                                              "2 consecutive values outside 2SD on same side"))
        # R_4s — Reject: range of 2 consecutive > 4SD
        if abs(last2[-1] - last2[-2]) > 4:
            violations.append(ViolationResult(WestgardRule.rule_r_4s, "reject",
                                              "Range of 2 consecutive values > 4SD"))

    if len(deviations) >= 4:
        last4 = deviations[-4:]
        # 4_1s — Reject: 4 consecutive > mean±1SD same side
        if all(d > 1 for d in last4) or all(d < -1 for d in last4):
            violations.append(ViolationResult(WestgardRule.rule_4_1s, "reject",
                                              "4 consecutive values outside 1SD on same side"))

    if len(deviations) >= 10:
        last10 = deviations[-10:]
        # 10x — Reject: 10 consecutive same side of mean
        if all(d > 0 for d in last10) or all(d < 0 for d in last10):
            violations.append(ViolationResult(WestgardRule.rule_10x, "reject",
                                              "10 consecutive values on same side of mean"))

    return violations


async def evaluate_westgard(db: AsyncSession, analyte_id: uuid.UUID, method_id: uuid.UUID, new_qc_result: QCResult) -> list[WestgardViolation]:
    chart = await get_active_chart(db, analyte_id, method_id)
    if not chart:
        return []

    values = await get_recent_qc_values(db, analyte_id, n=10)
    if new_qc_result.measured_value not in values:
        values.append(new_qc_result.measured_value)

    violations_data = apply_westgard_rules(values, chart)
    created: list[WestgardViolation] = []

    for v in violations_data:
        violation = WestgardViolation(
            qc_result_id=new_qc_result.id,
            rule_violated=v.rule,
            severity=v.severity,
        )
        db.add(violation)
        created.append(violation)

    return created


def compute_chart_limits(values: list[float]) -> dict:
    arr = np.array(values)
    mean = float(np.mean(arr))
    sd = float(np.std(arr, ddof=1))
    return {
        "mean": mean,
        "sd": sd,
        "ucl": mean + 3 * sd,
        "lcl": mean - 3 * sd,
        "uwl": mean + 2 * sd,
        "lwl": mean - 2 * sd,
        "n_points": len(values),
    }
