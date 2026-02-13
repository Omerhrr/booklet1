"""
Roles Router - Role and Permission Management
"""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import Optional, List
from pydantic import BaseModel

from ..database import get_db
from ..security import get_current_user
from ..models.permission import Role, Permission, RolePermission

router = APIRouter(prefix="/roles", tags=["Roles"])


class RoleCreate(BaseModel):
    name: str
    description: Optional[str] = None
    permissions: List[int] = []  # Permission IDs

class RoleUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    permissions: Optional[List[int]] = None


@router.get("")
async def list_roles(
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """List roles for tenant"""
    tenant_id = current_user["tenant_id"]

    roles = db.query(Role).filter(
        Role.tenant_id == tenant_id
    ).order_by(Role.name).all()

    return {
        "items": [{
            "id": r.id,
            "name": r.name,
            "description": r.description,
            "is_system": r.is_system,
            "user_count": len(r.users) if hasattr(r, 'users') else 0
        } for r in roles]
    }


@router.post("")
async def create_role(
    role_data: RoleCreate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Create custom role"""
    tenant_id = current_user["tenant_id"]

    # Check for duplicate name
    existing = db.query(Role).filter(
        Role.tenant_id == tenant_id,
        Role.name == role_data.name
    ).first()

    if existing:
        raise HTTPException(status_code=400, detail="Role name already exists")

    role = Role(
        tenant_id=tenant_id,
        name=role_data.name,
        description=role_data.description,
        is_system=False
    )

    db.add(role)
    db.flush()

    # Assign permissions
    for perm_id in role_data.permissions:
        perm = db.query(Permission).filter(Permission.id == perm_id).first()
        if perm:
            role_perm = RolePermission(
                role_id=role.id,
                permission_id=perm_id
            )
            db.add(role_perm)

    db.commit()

    return {"id": role.id, "message": "Role created successfully"}


@router.get("/{role_id}")
async def get_role(
    role_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Get role details with permissions"""
    tenant_id = current_user["tenant_id"]

    role = db.query(Role).filter(
        Role.id == role_id,
        Role.tenant_id == tenant_id
    ).first()

    if not role:
        raise HTTPException(status_code=404, detail="Role not found")

    # Get role permissions
    role_perms = db.query(RolePermission).filter(
        RolePermission.role_id == role_id
    ).all()

    perm_ids = [rp.permission_id for rp in role_perms]
    permissions = db.query(Permission).filter(Permission.id.in_(perm_ids)).all()

    return {
        "id": role.id,
        "name": role.name,
        "description": role.description,
        "is_system": role.is_system,
        "permissions": [{
            "id": p.id,
            "name": p.name,
            "category": p.category
        } for p in permissions]
    }


@router.put("/{role_id}")
async def update_role(
    role_id: int,
    role_data: RoleUpdate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Update role"""
    tenant_id = current_user["tenant_id"]

    role = db.query(Role).filter(
        Role.id == role_id,
        Role.tenant_id == tenant_id
    ).first()

    if not role:
        raise HTTPException(status_code=404, detail="Role not found")

    if role.is_system:
        raise HTTPException(status_code=400, detail="Cannot modify system roles")

    if role_data.name:
        role.name = role_data.name
    if role_data.description:
        role.description = role_data.description

    if role_data.permissions is not None:
        # Remove existing permissions
        db.query(RolePermission).filter(
            RolePermission.role_id == role_id
        ).delete()

        # Add new permissions
        for perm_id in role_data.permissions:
            role_perm = RolePermission(
                role_id=role.id,
                permission_id=perm_id
            )
            db.add(role_perm)

    db.commit()
    return {"message": "Role updated successfully"}


@router.delete("/{role_id}")
async def delete_role(
    role_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Delete custom role"""
    tenant_id = current_user["tenant_id"]

    role = db.query(Role).filter(
        Role.id == role_id,
        Role.tenant_id == tenant_id
    ).first()

    if not role:
        raise HTTPException(status_code=404, detail="Role not found")

    if role.is_system:
        raise HTTPException(status_code=400, detail="Cannot delete system roles")

    # Check if role has users
    from ..models.user import User
    users = db.query(User).filter(User.role_id == role_id).count()
    if users > 0:
        raise HTTPException(status_code=400, detail=f"Cannot delete role: {users} users assigned")

    # Delete role permissions
    db.query(RolePermission).filter(
        RolePermission.role_id == role_id
    ).delete()

    db.delete(role)
    db.commit()

    return {"message": "Role deleted successfully"}


@router.get("/permissions/all")
async def list_all_permissions(
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """List all available permissions"""
    permissions = db.query(Permission).order_by(Permission.category, Permission.name).all()

    # Group by category
    grouped = {}
    for p in permissions:
        if p.category not in grouped:
            grouped[p.category] = []
        grouped[p.category].append({
            "id": p.id,
            "name": p.name,
            "description": p.description
        })

    return {"permissions_by_category": grouped}
