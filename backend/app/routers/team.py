"""
Team Router - Team Management
"""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import Optional, List
from pydantic import BaseModel

from ..database import get_db
from ..security import get_current_user, get_password_hash
from ..models.user import User
from ..models.permission import Role

router = APIRouter(prefix="/team", tags=["Team"])


class TeamMemberCreate(BaseModel):
    username: str
    email: str
    password: str
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    phone: Optional[str] = None
    role_id: int
    branch_id: int

class TeamMemberUpdate(BaseModel):
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    role_id: Optional[int] = None
    is_active: Optional[bool] = None


@router.get("")
async def list_team_members(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, le=200),
    is_active: Optional[bool] = None,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """List team members"""
    tenant_id = current_user["tenant_id"]

    query = db.query(User).filter(User.tenant_id == tenant_id)

    if is_active is not None:
        query = query.filter(User.is_active == is_active)

    users = query.order_by(User.created_at.desc()).offset(skip).limit(limit).all()

    # Get roles
    role_ids = list(set(u.role_id for u in users if u.role_id))
    roles = {r.id: r for r in db.query(Role).filter(Role.id.in_(role_ids)).all()}

    return {
        "items": [{
            "id": u.id,
            "username": u.username,
            "email": u.email,
            "first_name": u.first_name,
            "last_name": u.last_name,
            "phone": u.phone,
            "role": roles.get(u.role_id, Role(name="Unknown")).name if u.role_id else "No Role",
            "is_active": u.is_active,
            "created_at": u.created_at.isoformat() if u.created_at else None
        } for u in users],
        "total": query.count()
    }


@router.post("")
async def create_team_member(
    member_data: TeamMemberCreate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Create team member"""
    tenant_id = current_user["tenant_id"]

    # Check for duplicate username/email
    existing = db.query(User).filter(
        (User.username == member_data.username) | (User.email == member_data.email)
    ).first()

    if existing:
        raise HTTPException(status_code=400, detail="Username or email already exists")

    # Verify role belongs to tenant
    role = db.query(Role).filter(
        Role.id == member_data.role_id,
        Role.tenant_id == tenant_id
    ).first()

    if not role:
        raise HTTPException(status_code=400, detail="Invalid role")

    user = User(
        tenant_id=tenant_id,
        username=member_data.username,
        email=member_data.email,
        password_hash=get_password_hash(member_data.password),
        first_name=member_data.first_name,
        last_name=member_data.last_name,
        phone=member_data.phone,
        role_id=member_data.role_id,
        branch_id=member_data.branch_id
    )

    db.add(user)
    db.commit()
    db.refresh(user)

    return {"id": user.id, "message": "Team member created successfully"}


@router.get("/{user_id}")
async def get_team_member(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Get team member details"""
    tenant_id = current_user["tenant_id"]

    user = db.query(User).filter(
        User.id == user_id,
        User.tenant_id == tenant_id
    ).first()

    if not user:
        raise HTTPException(status_code=404, detail="Team member not found")

    role = db.query(Role).filter(Role.id == user.role_id).first() if user.role_id else None

    return {
        "id": user.id,
        "username": user.username,
        "email": user.email,
        "first_name": user.first_name,
        "last_name": user.last_name,
        "phone": user.phone,
        "role_id": user.role_id,
        "role_name": role.name if role else None,
        "is_active": user.is_active,
        "created_at": user.created_at.isoformat() if user.created_at else None
    }


@router.put("/{user_id}")
async def update_team_member(
    user_id: int,
    member_data: TeamMemberUpdate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Update team member"""
    tenant_id = current_user["tenant_id"]

    user = db.query(User).filter(
        User.id == user_id,
        User.tenant_id == tenant_id
    ).first()

    if not user:
        raise HTTPException(status_code=404, detail="Team member not found")

    for field, value in member_data.dict(exclude_unset=True).items():
        setattr(user, field, value)

    db.commit()
    return {"message": "Team member updated successfully"}


@router.delete("/{user_id}")
async def delete_team_member(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Deactivate team member"""
    tenant_id = current_user["tenant_id"]

    user = db.query(User).filter(
        User.id == user_id,
        User.tenant_id == tenant_id
    ).first()

    if not user:
        raise HTTPException(status_code=404, detail="Team member not found")

    if user.id == current_user["user_id"]:
        raise HTTPException(status_code=400, detail="Cannot deactivate yourself")

    user.is_active = False
    db.commit()

    return {"message": "Team member deactivated successfully"}


@router.post("/{user_id}/reset-password")
async def reset_member_password(
    user_id: int,
    new_password: str,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Reset team member password"""
    tenant_id = current_user["tenant_id"]

    user = db.query(User).filter(
        User.id == user_id,
        User.tenant_id == tenant_id
    ).first()

    if not user:
        raise HTTPException(status_code=404, detail="Team member not found")

    user.password_hash = get_password_hash(new_password)
    db.commit()

    return {"message": "Password reset successfully"}
