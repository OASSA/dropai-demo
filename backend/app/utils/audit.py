from sqlalchemy.ext.asyncio import AsyncSession
from app.models.audit_log import AuditLog
from typing import Optional, Any
import json


async def log_action(
    db: AsyncSession,
    action: str,
    resource_type: str,
    resource_id: Optional[str] = None,
    user_id: Optional[int] = None,
    old_value: Optional[Any] = None,
    new_value: Optional[Any] = None,
    description: Optional[str] = None,
    ip_address: Optional[str] = None,
    user_agent: Optional[str] = None,
) -> AuditLog:
    """Record an auditable action to the audit log."""
    def _serialize(val):
        if val is None:
            return None
        if isinstance(val, dict):
            return val
        try:
            return json.loads(json.dumps(val, default=str))
        except Exception:
            return {"value": str(val)}

    entry = AuditLog(
        user_id=user_id,
        action=action,
        resource_type=resource_type,
        resource_id=str(resource_id) if resource_id else None,
        old_value=_serialize(old_value),
        new_value=_serialize(new_value),
        description=description,
        ip_address=ip_address,
        user_agent=user_agent,
    )
    db.add(entry)
    # Flush so we get the ID, but let the calling transaction commit
    await db.flush()
    return entry
