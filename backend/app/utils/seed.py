"""
Seed script: creates admin user, quality grades, and pre-loaded olive oil methods.
Run once after migrations: python -m app.utils.seed
"""
import asyncio
import uuid
from datetime import date

from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy import select

from app.config import settings
from app.models.user import User, Role
from app.models.specification import ProductQualityGrade, AnalyteSpecification
from app.models.method import AnalyticalMethod, MethodStatus, Analyte

engine = create_async_engine(settings.DATABASE_URL)
Session = async_sessionmaker(engine, expire_on_commit=False)


QUALITY_GRADES = [
    {"code": "EVOO", "name_es": "Aceite de Oliva Virgen Extra", "name_en": "Extra Virgin Olive Oil",
     "regulatory_reference": "EU Reg. 2016/2095 + IOC/T.15/NC No.3/Rev.14", "is_regulatory": True},
    {"code": "VOO", "name_es": "Aceite de Oliva Virgen", "name_en": "Virgin Olive Oil",
     "regulatory_reference": "EU Reg. 2016/2095", "is_regulatory": True},
    {"code": "LAMPANTE", "name_es": "Aceite de Oliva Virgen Lampante", "name_en": "Lampante Virgin Olive Oil",
     "regulatory_reference": "EU Reg. 2016/2095", "is_regulatory": True},
    {"code": "ROO", "name_es": "Aceite de Oliva Refinado", "name_en": "Refined Olive Oil",
     "regulatory_reference": "EU Reg. 2016/2095", "is_regulatory": True},
    {"code": "OO", "name_es": "Aceite de Oliva", "name_en": "Olive Oil (blend)",
     "regulatory_reference": "EU Reg. 2016/2095", "is_regulatory": True},
    {"code": "OPOO", "name_es": "Aceite de Orujo de Oliva", "name_en": "Olive Pomace Oil",
     "regulatory_reference": "EU Reg. 2016/2095", "is_regulatory": True},
]

METHODS = [
    {
        "code": "OO-FFA-001",
        "name": "Free Fatty Acids (as oleic acid)",
        "name_es": "Acidez libre (como ácido oleico)",
        "reference_standard": "IOC/T.15/NC No.3/Rev.14",
        "category": "chemistry",
        "instrument_type": "balance",
        "analytes": [
            {"name": "Free Fatty Acids (FFA)", "name_es": "Acidez Libre (% ác. oleico)",
             "symbol": "FFA", "unit": "%", "decimal_places": 2, "uncertainty_percent": 3.0,
             "specs": {"EVOO": (None, 0.8), "VOO": (None, 2.0), "LAMPANTE": (None, None),
                       "ROO": (None, 0.3), "OO": (None, 1.0)}},
        ],
    },
    {
        "code": "OO-PV-001",
        "name": "Peroxide Value",
        "name_es": "Índice de peróxidos",
        "reference_standard": "IOC/T.15/NC No.3/Rev.14",
        "category": "chemistry",
        "instrument_type": "balance",
        "analytes": [
            {"name": "Peroxide Value (PV)", "name_es": "Índice de Peróxidos",
             "symbol": "PV", "unit": "meq O₂/kg", "decimal_places": 1, "uncertainty_percent": 4.0,
             "specs": {"EVOO": (None, 20.0), "VOO": (None, 20.0), "ROO": (None, 5.0), "OO": (None, 15.0)}},
        ],
    },
    {
        "code": "OO-UV-001",
        "name": "UV Spectrophotometric Constants",
        "name_es": "Constantes Espectrofotométricas UV",
        "reference_standard": "EU Reg. 2568/91 Annex IX",
        "category": "spectrophotometry",
        "instrument_type": "uvvis",
        "analytes": [
            {"name": "K232", "name_es": "K232", "symbol": "K232", "unit": "—", "decimal_places": 2,
             "uncertainty_percent": 2.0,
             "specs": {"EVOO": (None, 2.50), "VOO": (None, 2.60)}},
            {"name": "K268", "name_es": "K268", "symbol": "K268", "unit": "—", "decimal_places": 3, "sort_order": 1},
            {"name": "K270", "name_es": "K270", "symbol": "K270", "unit": "—", "decimal_places": 3,
             "uncertainty_percent": 2.0,
             "specs": {"EVOO": (None, 0.22), "VOO": (None, 0.25)}, "sort_order": 2},
            {"name": "K272", "name_es": "K272", "symbol": "K272", "unit": "—", "decimal_places": 3, "sort_order": 3},
            {"name": "ΔK (delta-K)", "name_es": "ΔK", "symbol": "ΔK", "unit": "—", "decimal_places": 3,
             "specs": {"EVOO": (None, 0.01), "VOO": (None, 0.01)}, "sort_order": 4},
        ],
    },
    {
        "code": "OO-GC-001",
        "name": "Fatty Acid Composition",
        "name_es": "Composición en Ácidos Grasos",
        "reference_standard": "EU Reg. 2568/91 Annex I",
        "category": "gc",
        "instrument_type": "gc",
        "analytes": [
            {"name": "Myristic acid (C14:0)", "name_es": "Ác. mirístico (C14:0)", "symbol": "C14:0",
             "unit": "%", "decimal_places": 2, "specs": {"EVOO": (None, 0.05), "VOO": (None, 0.05)}, "sort_order": 0},
            {"name": "Palmitic acid (C16:0)", "name_es": "Ác. palmítico (C16:0)", "symbol": "C16:0",
             "unit": "%", "decimal_places": 2, "specs": {"EVOO": (7.5, 20.0), "VOO": (7.5, 20.0)}, "sort_order": 1},
            {"name": "Palmitoleic acid (C16:1)", "name_es": "Ác. palmitoleico (C16:1)", "symbol": "C16:1",
             "unit": "%", "decimal_places": 2, "specs": {"EVOO": (None, 0.6), "VOO": (None, 0.6)}, "sort_order": 2},
            {"name": "Heptadecanoic acid (C17:0)", "name_es": "Ác. heptadecanoico (C17:0)", "symbol": "C17:0",
             "unit": "%", "decimal_places": 2, "specs": {"EVOO": (None, 0.3), "VOO": (None, 0.3)}, "sort_order": 3},
            {"name": "Heptadecenoic acid (C17:1)", "name_es": "Ác. heptadecenoico (C17:1)", "symbol": "C17:1",
             "unit": "%", "decimal_places": 2, "specs": {"EVOO": (None, 0.3), "VOO": (None, 0.3)}, "sort_order": 4},
            {"name": "Stearic acid (C18:0)", "name_es": "Ác. esteárico (C18:0)", "symbol": "C18:0",
             "unit": "%", "decimal_places": 2, "specs": {"EVOO": (0.5, 5.0), "VOO": (0.5, 5.0)}, "sort_order": 5},
            {"name": "Oleic acid (C18:1)", "name_es": "Ác. oleico (C18:1)", "symbol": "C18:1",
             "unit": "%", "decimal_places": 2, "specs": {"EVOO": (55.0, 83.0), "VOO": (55.0, 83.0)}, "sort_order": 6},
            {"name": "Linoleic acid (C18:2)", "name_es": "Ác. linoleico (C18:2)", "symbol": "C18:2",
             "unit": "%", "decimal_places": 2, "specs": {"EVOO": (3.5, 21.0), "VOO": (3.5, 21.0)}, "sort_order": 7},
            {"name": "Linolenic acid (C18:3)", "name_es": "Ác. linolénico (C18:3)", "symbol": "C18:3",
             "unit": "%", "decimal_places": 2, "specs": {"EVOO": (None, 1.0), "VOO": (None, 1.0)}, "sort_order": 8},
            {"name": "Arachidic acid (C20:0)", "name_es": "Ác. araquídico (C20:0)", "symbol": "C20:0",
             "unit": "%", "decimal_places": 2, "specs": {"EVOO": (None, 0.6), "VOO": (None, 0.6)}, "sort_order": 9},
            {"name": "Eicosenoic acid (C20:1)", "name_es": "Ác. eicosenóico (C20:1)", "symbol": "C20:1",
             "unit": "%", "decimal_places": 2, "specs": {"EVOO": (None, 0.4), "VOO": (None, 0.4)}, "sort_order": 10},
            {"name": "Behenic acid (C22:0)", "name_es": "Ác. behénico (C22:0)", "symbol": "C22:0",
             "unit": "%", "decimal_places": 2, "specs": {"EVOO": (None, 0.2), "VOO": (None, 0.2)}, "sort_order": 11},
            {"name": "Lignoceric acid (C24:0)", "name_es": "Ác. lignocérico (C24:0)", "symbol": "C24:0",
             "unit": "%", "decimal_places": 2, "specs": {"EVOO": (None, 0.2), "VOO": (None, 0.2)}, "sort_order": 12},
        ],
    },
    {
        "code": "OO-PP-001",
        "name": "Total Polyphenols",
        "name_es": "Polifenoles Totales",
        "reference_standard": "Folin-Ciocalteu / COI/T.20/Doc.29",
        "category": "spectrophotometry",
        "instrument_type": "uvvis",
        "analytes": [
            {"name": "Total Polyphenols", "name_es": "Polifenoles Totales",
             "symbol": "Polyphenols", "unit": "mg/kg", "decimal_places": 0, "uncertainty_percent": 5.0},
        ],
    },
    {
        "code": "OO-SN-001",
        "name": "Organoleptic Assessment (Panel Test)",
        "name_es": "Valoración Organoléptica (Panel Test)",
        "reference_standard": "COI/T.20/Doc.No 15/Rev.10",
        "category": "sensory",
        "instrument_type": "panel",
        "analytes": [
            {"name": "Fruitiness (median)", "name_es": "Frutado (mediana)", "symbol": "Fruitiness",
             "unit": "score 0-10", "decimal_places": 1, "sort_order": 0},
            {"name": "Bitterness (median)", "name_es": "Amargo (mediana)", "symbol": "Bitterness",
             "unit": "score 0-10", "decimal_places": 1, "sort_order": 1},
            {"name": "Pungency (median)", "name_es": "Picante (mediana)", "symbol": "Pungency",
             "unit": "score 0-10", "decimal_places": 1, "sort_order": 2},
            {"name": "Defect Median", "name_es": "Mediana de Defectos", "symbol": "DefectMedian",
             "unit": "score 0-10", "decimal_places": 1, "sort_order": 3,
             "specs": {"EVOO": (None, 0.0), "VOO": (None, 3.5)}},
        ],
    },
]


async def seed():
    async with Session() as db:
        # Create admin user
        existing = await db.execute(select(User).where(User.email == "admin@olivelims.local"))
        if not existing.scalar_one_or_none():
            from app.auth.service import hash_password
            admin = User(
                email="admin@olivelims.local",
                hashed_password=hash_password("Admin1234!"),
                full_name="System Administrator",
                role=Role.admin,
            )
            db.add(admin)
            await db.flush()
            print("✓ Admin user created: admin@olivelims.local / Admin1234!")
        else:
            admin_q = await db.execute(select(User).where(User.email == "admin@olivelims.local"))
            admin = admin_q.scalar_one()
            print("  Admin user already exists")

        # Create quality grades
        grade_map: dict[str, ProductQualityGrade] = {}
        for gd in QUALITY_GRADES:
            ex = await db.execute(select(ProductQualityGrade).where(ProductQualityGrade.code == gd["code"]))
            if not ex.scalar_one_or_none():
                grade = ProductQualityGrade(created_by_id=admin.id, **gd)
                db.add(grade)
                await db.flush()
                grade_map[gd["code"]] = grade
                print(f"  ✓ Grade: {gd['code']}")
            else:
                grade_map[gd["code"]] = ex.scalar_one()

        # Create methods and analytes
        for md in METHODS:
            analytes_data = md.pop("analytes", [])
            ex = await db.execute(select(AnalyticalMethod).where(AnalyticalMethod.code == md["code"]))
            if not ex.scalar_one_or_none():
                method = AnalyticalMethod(created_by_id=admin.id, status=MethodStatus.approved, **md)
                db.add(method)
                await db.flush()
                print(f"  ✓ Method: {md['code']}")

                for i, ad in enumerate(analytes_data):
                    specs = ad.pop("specs", {})
                    ad.setdefault("sort_order", i)
                    analyte = Analyte(method_id=method.id, **ad)
                    db.add(analyte)
                    await db.flush()

                    for grade_code, (min_l, max_l) in specs.items():
                        if grade_code in grade_map:
                            spec = AnalyteSpecification(
                                analyte_id=analyte.id,
                                quality_grade_id=grade_map[grade_code].id,
                                min_limit=min_l,
                                max_limit=max_l,
                                limit_note=method.reference_standard,
                                updated_by_id=admin.id,
                            )
                            db.add(spec)
            else:
                print(f"  Method already exists: {md['code']}")

        await db.commit()
        print("\n✅ Seed complete!")


if __name__ == "__main__":
    asyncio.run(seed())
