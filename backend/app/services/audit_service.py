from sqlalchemy.ext.asyncio import AsyncSession

from app.models.audit import AuditLog, AuditAction
from app.models.user import User


async def log_action(
    db: AsyncSession,
    user: User | None,
    action: AuditAction,
    resource_type: str,
    resource_id: str | None = None,
    old_value: dict | None = None,
    new_value: dict | None = None,
    ip_address: str | None = None,
    extra: dict | None = None,
) -> None:
    entry = AuditLog(
        user_id=user.id if user else None,
        user_email=user.email if user else "system",
        action=action,
        resource_type=resource_type,
        resource_id=resource_id,
        old_value=old_value,
        new_value=new_value,
        ip_address=ip_address,
        extra=extra,
    )
    db.add(entry)
