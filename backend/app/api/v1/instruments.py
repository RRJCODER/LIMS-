import uuid
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, WebSocket, WebSocketDisconnect
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.database import get_db
from app.auth.permissions import require_analyst
from app.models.equipment import Equipment
from app.models.instrument_data import GCImport
from app.models.user import User
from app.dependencies import get_current_user
from app.instrument_bridge.websocket_manager import ws_manager
from app.instrument_bridge.gc.jcamp_parser import JCAMPParser, GCCSVParser
from app.config import settings
import os
from pathlib import Path

router = APIRouter(prefix="/instruments", tags=["instruments"])


@router.get("/devices")
async def list_devices(db: AsyncSession = Depends(get_db), _=Depends(require_analyst)):
    result = await db.execute(
        select(Equipment).where(Equipment.comm_protocol.isnot(None))
    )
    return result.scalars().all()


@router.post("/devices/{device_id}/tare")
async def tare_balance(device_id: uuid.UUID, db: AsyncSession = Depends(get_db), _=Depends(require_analyst)):
    eq_q = await db.execute(select(Equipment).where(Equipment.id == device_id))
    eq = eq_q.scalar_one_or_none()
    if not eq or eq.comm_protocol != "sics":
        raise HTTPException(status_code=400, detail="Device not found or not a SICS balance")
    # In production: call SICSDriver.tare() via instrument manager
    return {"status": "tare_sent", "device_id": str(device_id)}


@router.websocket("/ws/{device_id}")
async def instrument_ws(device_id: str, websocket: WebSocket):
    await ws_manager.connect(device_id, websocket)
    try:
        while True:
            data = await websocket.receive_text()
            # Echo back / handle client commands
            await ws_manager.broadcast(device_id, {"echo": data})
    except WebSocketDisconnect:
        ws_manager.disconnect(device_id, websocket)


@router.post("/gc/import", status_code=201)
async def import_gc(
    test_request_id: uuid.UUID,
    file: UploadFile = File(...),
    equipment_id: uuid.UUID | None = None,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_analyst),
):
    content = (await file.read()).decode("utf-8", errors="replace")

    filename = file.filename or ""
    if filename.lower().endswith((".jdx", ".dx")):
        parser = JCAMPParser()
        fmt = "jcamp_dx"
    else:
        parser = GCCSVParser()
        fmt = "csv"

    peaks = parser.parse(content)

    dest_dir = Path(settings.MEDIA_ROOT) / "gc_imports"
    dest_dir.mkdir(parents=True, exist_ok=True)
    dest = dest_dir / f"{test_request_id}_{filename}"
    with open(dest, "w") as f:
        f.write(content)

    gc_import = GCImport(
        test_request_id=test_request_id,
        equipment_id=equipment_id,
        import_format=fmt,
        original_filename=filename,
        file_path=str(dest),
        imported_by_id=current_user.id,
        peaks=[{"name": p.name, "rt": p.retention_time_min, "area": p.area, "area_pct": p.area_percent} for p in peaks],
    )
    db.add(gc_import)
    await db.flush()
    return {"id": str(gc_import.id), "peaks_found": len(peaks), "peaks": gc_import.peaks}


@router.get("/gc/imports")
async def list_gc_imports(db: AsyncSession = Depends(get_db), _=Depends(require_analyst)):
    result = await db.execute(select(GCImport).order_by(GCImport.imported_at.desc()).limit(50))
    return result.scalars().all()
