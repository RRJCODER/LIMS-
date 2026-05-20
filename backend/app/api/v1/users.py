import uuid
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, EmailStr
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.database import get_db
from app.dependencies import get_current_user
from app.auth.permissions import require_admin, require_supervisor
from app.auth.service import hash_password
from app.models.user import User, Role, UserQualification, TrainingRecord
from app.services.audit_service import log_action
from app.models.audit import AuditAction

router = APIRouter(prefix="/users", tags=["users"])


class UserCreate(BaseModel):
    email: EmailStr
    password: str
    full_name: str
    role: Role = Role.analyst
    lab_section: str | None = None


class UserUpdate(BaseModel):
    full_name: str | None = None
    role: Role | None = None
    lab_section: str | None = None
    is_active: bool | None = None


class UserOut(BaseModel):
    id: uuid.UUID
    email: str
    full_name: str
    role: Role
    lab_section: str | None
    is_active: bool

    model_config = {"from_attributes": True}


@router.get("/", response_model=list[UserOut])
async def list_users(
    db: AsyncSession = Depends(get_db),
    _=Depends(require_supervisor),
):
    result = await db.execute(select(User).where(User.is_active == True).order_by(User.full_name))
    return result.scalars().all()


@router.post("/", response_model=UserOut, status_code=status.HTTP_201_CREATED)
async def create_user(
    body: UserCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_admin),
):
    existing = await db.execute(select(User).where(User.email == body.email))
    if existing.scalar_one_or_none():
        raise HTTPException(status_code=400, detail="Email already registered")
    user = User(
        email=body.email,
        hashed_password=hash_password(body.password),
        full_name=body.full_name,
        role=body.role,
        lab_section=body.lab_section,
    )
    db.add(user)
    await db.flush()
    await log_action(db, current_user, AuditAction.create, "user", str(user.id), new_value={"email": user.email, "role": user.role})
    return user


@router.get("/{user_id}", response_model=UserOut)
async def get_user(user_id: uuid.UUID, db: AsyncSession = Depends(get_db), _=Depends(require_supervisor)):
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user


@router.put("/{user_id}", response_model=UserOut)
async def update_user(
    user_id: uuid.UUID,
    body: UserUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_admin),
):
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    old = {"full_name": user.full_name, "role": user.role, "is_active": user.is_active}
    for field, value in body.model_dump(exclude_none=True).items():
        setattr(user, field, value)
    await log_action(db, current_user, AuditAction.update, "user", str(user.id), old_value=old)
    return user
