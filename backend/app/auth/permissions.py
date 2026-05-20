from functools import wraps
from fastapi import Depends, HTTPException, status

from app.models.user import Role, User
from app.dependencies import get_current_user


def require_roles(*roles: Role):
    async def checker(current_user: User = Depends(get_current_user)) -> User:
        if current_user.role not in roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Insufficient permissions",
            )
        return current_user
    return checker


require_admin = require_roles(Role.admin)
require_supervisor = require_roles(Role.admin, Role.supervisor)
require_analyst = require_roles(Role.admin, Role.supervisor, Role.analyst)
require_viewer = require_roles(Role.admin, Role.supervisor, Role.analyst, Role.viewer)
