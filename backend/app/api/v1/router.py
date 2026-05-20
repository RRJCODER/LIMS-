from fastapi import APIRouter

from app.api.v1 import users, samples, methods, tests, qc, equipment, documents, instruments, reports, dashboard, settings_router

router = APIRouter(prefix="/api/v1")

router.include_router(users.router)
router.include_router(samples.router)
router.include_router(methods.router)
router.include_router(tests.router)
router.include_router(qc.router)
router.include_router(equipment.router)
router.include_router(documents.router)
router.include_router(instruments.router)
router.include_router(reports.router)
router.include_router(dashboard.router)
router.include_router(settings_router.router)
