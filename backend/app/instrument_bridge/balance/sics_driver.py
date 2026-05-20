"""Mettler-Toledo SICS (Standard Interface Command Set) balance driver."""
import asyncio
import logging

logger = logging.getLogger(__name__)

SICS_COMMANDS = {
    "stable_weight": b"S\r\n",
    "immediate_weight": b"SI\r\n",
    "tare": b"T\r\n",
    "zero": b"Z\r\n",
    "reset": b"@\r\n",
    "get_id": b"I4\r\n",
}


class WeightReading:
    def __init__(self, raw: str, value: float, unit: str, stable: bool):
        self.raw = raw
        self.value = value
        self.unit = unit
        self.stable = stable

    def dict(self):
        return {"raw": self.raw, "value": self.value, "unit": self.unit, "stable": self.stable}


class SICSDriver:
    """
    Async SICS driver using pyserial-asyncio.
    Protocol: 9600 baud, 8N1, XON/XOFF.
    Response format: 'S S      12.3456 g'
    """

    def __init__(self, port: str, baud: int = 9600, timeout: float = 3.0):
        self.port = port
        self.baud = baud
        self.timeout = timeout
        self._reader = None
        self._writer = None
        self._connected = False

    async def connect(self) -> None:
        import serial_asyncio
        self._reader, self._writer = await serial_asyncio.open_serial_connection(
            url=self.port, baudrate=self.baud,
            bytesize=8, parity="N", stopbits=1,
            xonxoff=True, rtscts=False,
        )
        self._connected = True
        logger.info("SICS balance connected on %s", self.port)

    async def disconnect(self) -> None:
        if self._writer:
            self._writer.close()
        self._connected = False

    async def _send_command(self, cmd: bytes) -> str:
        if not self._connected:
            raise RuntimeError("Balance not connected")
        self._writer.write(cmd)
        try:
            line = await asyncio.wait_for(self._reader.readline(), timeout=self.timeout)
            return line.decode("ascii", errors="replace").strip()
        except asyncio.TimeoutError:
            raise RuntimeError("Balance response timeout")

    def _parse_response(self, raw: str) -> WeightReading:
        parts = raw.split()
        if len(parts) < 3:
            raise ValueError(f"Unexpected SICS response: {raw!r}")
        try:
            stable = parts[1] == "S"
            value = float(parts[2])
            unit = parts[3] if len(parts) > 3 else "g"
        except (IndexError, ValueError) as e:
            raise ValueError(f"Failed to parse SICS response {raw!r}: {e}")
        return WeightReading(raw=raw, value=value, unit=unit, stable=stable)

    async def read_stable_weight(self) -> WeightReading:
        raw = await self._send_command(SICS_COMMANDS["stable_weight"])
        return self._parse_response(raw)

    async def read_immediate(self) -> WeightReading:
        raw = await self._send_command(SICS_COMMANDS["immediate_weight"])
        return self._parse_response(raw)

    async def tare(self) -> str:
        return await self._send_command(SICS_COMMANDS["tare"])

    async def zero(self) -> str:
        return await self._send_command(SICS_COMMANDS["zero"])

    async def get_id(self) -> str:
        return await self._send_command(SICS_COMMANDS["get_id"])

    @property
    def is_connected(self) -> bool:
        return self._connected
