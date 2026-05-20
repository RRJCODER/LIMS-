"""Minimal HS256 JWT — uses only Python stdlib (no cryptography/cffi required)."""
import base64
import hashlib
import hmac
import json
import time
from typing import Any


def _b64url_encode(data: bytes) -> str:
    return base64.urlsafe_b64encode(data).rstrip(b"=").decode()


def _b64url_decode(s: str) -> bytes:
    padding = (4 - len(s) % 4) % 4
    return base64.urlsafe_b64decode(s + "=" * padding)


class JWTDecodeError(Exception):
    pass


def encode(payload: dict[str, Any], secret: str, algorithm: str = "HS256") -> str:
    if algorithm != "HS256":
        raise ValueError(f"Unsupported algorithm: {algorithm}")
    header = _b64url_encode(json.dumps({"alg": "HS256", "typ": "JWT"}, separators=(",", ":")).encode())
    # Convert datetime exp/iat to int timestamps
    p = {}
    for k, v in payload.items():
        if hasattr(v, "timestamp"):
            p[k] = int(v.timestamp())
        else:
            p[k] = v
    body = _b64url_encode(json.dumps(p, separators=(",", ":")).encode())
    signing_input = f"{header}.{body}".encode()
    sig = _b64url_encode(hmac.new(secret.encode(), signing_input, hashlib.sha256).digest())
    return f"{header}.{body}.{sig}"


def decode(token: str, secret: str, algorithms: list[str] | None = None) -> dict[str, Any]:
    try:
        parts = token.split(".")
        if len(parts) != 3:
            raise JWTDecodeError("Invalid token structure")
        header, body, sig = parts
        expected_sig = _b64url_encode(
            hmac.new(secret.encode(), f"{header}.{body}".encode(), hashlib.sha256).digest()
        )
        if not hmac.compare_digest(sig, expected_sig):
            raise JWTDecodeError("Invalid signature")
        payload = json.loads(_b64url_decode(body))
        if "exp" in payload and payload["exp"] < time.time():
            raise JWTDecodeError("Token has expired")
        return payload
    except JWTDecodeError:
        raise
    except Exception as exc:
        raise JWTDecodeError(str(exc)) from exc
