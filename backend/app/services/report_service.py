"""CoA generation using WeasyPrint."""
import hashlib
import os
import uuid
from datetime import date
from pathlib import Path

from jinja2 import Environment, FileSystemLoader
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.config import settings
from app.models.report import CertificateOfAnalysis, ReportTemplate
from app.models.sample import Sample
from app.models.test import TestRequest, TestResult
from app.models.method import Analyte

TEMPLATE_DIR = Path(__file__).parent.parent / "templates"


async def get_default_template(db: AsyncSession) -> ReportTemplate | None:
    result = await db.execute(
        select(ReportTemplate).where(ReportTemplate.is_default == True).limit(1)
    )
    return result.scalar_one_or_none()


async def generate_coa_pdf(db: AsyncSession, coa: CertificateOfAnalysis) -> str:
    from weasyprint import HTML

    template_row = await get_default_template(db)

    env = Environment(loader=FileSystemLoader(str(TEMPLATE_DIR)))
    template = env.get_template("coa_olive_oil.html")

    # Fetch all approved results for this sample
    requests = await db.execute(
        select(TestRequest).where(TestRequest.sample_id == coa.sample_id)
    )
    test_requests = requests.scalars().all()

    results_data = []
    for tr in test_requests:
        results = await db.execute(
            select(TestResult, Analyte)
            .join(Analyte, TestResult.analyte_id == Analyte.id)
            .where(TestResult.test_request_id == tr.id)
            .order_by(Analyte.sort_order)
        )
        for result, analyte in results.all():
            results_data.append({
                "analyte_name": analyte.name,
                "analyte_name_es": analyte.name_es or analyte.name,
                "symbol": analyte.symbol or "",
                "value": result.reported_value,
                "unit": result.unit,
                "uncertainty": result.uncertainty,
                "in_spec": result.in_spec,
                "compliance_note": result.compliance_note or "",
            })

    lab_name = (template_row.lab_name if template_row else None) or settings.LAB_NAME
    accreditation = (template_row.accreditation_number if template_row else None) or settings.LAB_ACCREDITATION_NUMBER

    logo_path = template_row.logo_path if template_row else None
    logo_b64 = None
    if logo_path and os.path.exists(logo_path):
        import base64
        with open(logo_path, "rb") as f:
            logo_b64 = base64.b64encode(f.read()).decode()

    html_content = template.render(
        coa=coa,
        sample=coa.sample,
        results=results_data,
        lab_name=lab_name,
        accreditation=accreditation,
        logo_b64=logo_b64,
        issue_date=coa.issue_date,
    )

    pdf_dir = Path(settings.MEDIA_ROOT) / "reports"
    pdf_dir.mkdir(parents=True, exist_ok=True)
    pdf_path = str(pdf_dir / f"{coa.coa_number}_rev{coa.revision}.pdf")

    HTML(string=html_content, base_url=str(TEMPLATE_DIR)).write_pdf(pdf_path)

    with open(pdf_path, "rb") as f:
        pdf_hash = hashlib.sha256(f.read()).hexdigest()

    coa.pdf_path = pdf_path
    coa.pdf_hash = pdf_hash

    return pdf_path


async def generate_coa_number(db: AsyncSession) -> str:
    from sqlalchemy import func
    year = date.today().year
    result = await db.execute(
        select(func.count(CertificateOfAnalysis.id)).where(
            CertificateOfAnalysis.coa_number.like(f"COA-{year}-%")
        )
    )
    count = result.scalar_one() + 1
    return f"COA-{year}-{count:04d}"
