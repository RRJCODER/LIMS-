"""WebSocket connection manager for live instrument streams."""
import asyncio
from typing import Any
from fastapi import WebSocket


class ConnectionManager:
    def __init__(self):
        self._connections: dict[str, list[WebSocket]] = {}

    async def connect(self, device_id: str, ws: WebSocket) -> None:
        await ws.accept()
        self._connections.setdefault(device_id, []).append(ws)

    def disconnect(self, device_id: str, ws: WebSocket) -> None:
        conns = self._connections.get(device_id, [])
        if ws in conns:
            conns.remove(ws)

    async def broadcast(self, device_id: str, data: Any) -> None:
        conns = self._connections.get(device_id, [])
        dead: list[WebSocket] = []
        for ws in conns:
            try:
                await ws.send_json(data)
            except Exception:
                dead.append(ws)
        for ws in dead:
            self.disconnect(device_id, ws)


ws_manager = ConnectionManager()
