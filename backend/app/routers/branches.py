"""
Branches Router - Multi-location Management
"""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import Optional
from pydantic import BaseModel

from ..database import get_db
from ..security import get_current_user
from ..models.branch import Branch

router = APIRouter(prefix="/branches", tags=["Branches"])


class BranchCreate(BaseModel):
    name: str
    code: Optional[str] = None
    address: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    country: str = "Nigeria"
    phone: Optional[str] = None
    email: Optional[str] = None
    is_head_office: bool = False

class BranchUpdate(BaseModel):
    name: Optional[str] = None
    code: Optional[str] = None
    address: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[str] = None
    is_active: Optional[bool] = None


@router.get("")
async def list_branches(
    is_active: Optional[bool] = None,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """List branches"""
    tenant_id = current_user["tenant_id"]

    query = db.query(Branch).filter(Branch.tenant_id == tenant_id)

    if is_active is not None:
        query = query.filter(Branch.is_active == is_active)

    branches = query.order_by(Branch.name).all()

    return {
        "items": [{
            "id": b.id,
            "name": b.name,
            "code": b.code,
            "city": b.city,
            "state": b.state,
            "phone": b.phone,
            "is_head_office": b.is_head_office,
            "is_active": b.is_active
        } for b in branches]
    }


@router.post("")
async def create_branch(
    branch_data: BranchCreate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Create branch"""
    tenant_id = current_user["tenant_id"]

    # Check for duplicate name
    existing = db.query(Branch).filter(
        Branch.tenant_id == tenant_id,
        Branch.name == branch_data.name
    ).first()

    if existing:
        raise HTTPException(status_code=400, detail="Branch name already exists")

    # If setting as head office, remove flag from other branches
    if branch_data.is_head_office:
        db.query(Branch).filter(
            Branch.tenant_id == tenant_id,
            Branch.is_head_office == True
        ).update({"is_head_office": False})

    branch = Branch(
        tenant_id=tenant_id,
        name=branch_data.name,
        code=branch_data.code,
        address=branch_data.address,
        city=branch_data.city,
        state=branch_data.state,
        country=branch_data.country,
        phone=branch_data.phone,
        email=branch_data.email,
        is_head_office=branch_data.is_head_office
    )

    db.add(branch)
    db.commit()
    db.refresh(branch)

    return {"id": branch.id, "message": "Branch created successfully"}


@router.get("/{branch_id}")
async def get_branch(
    branch_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Get branch details"""
    tenant_id = current_user["tenant_id"]

    branch = db.query(Branch).filter(
        Branch.id == branch_id,
        Branch.tenant_id == tenant_id
    ).first()

    if not branch:
        raise HTTPException(status_code=404, detail="Branch not found")

    # Get stats
    from ..models.user import User
    from ..models.sales import SalesInvoice
    from ..models.product import Product

    user_count = db.query(User).filter(User.branch_id == branch_id).count()
    product_count = db.query(Product).filter(Product.branch_id == branch_id).count()

    return {
        "id": branch.id,
        "name": branch.name,
        "code": branch.code,
        "address": branch.address,
        "city": branch.city,
        "state": branch.state,
        "country": branch.country,
        "phone": branch.phone,
        "email": branch.email,
        "is_head_office": branch.is_head_office,
        "is_active": branch.is_active,
        "stats": {
            "users": user_count,
            "products": product_count
        }
    }


@router.put("/{branch_id}")
async def update_branch(
    branch_id: int,
    branch_data: BranchUpdate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Update branch"""
    tenant_id = current_user["tenant_id"]

    branch = db.query(Branch).filter(
        Branch.id == branch_id,
        Branch.tenant_id == tenant_id
    ).first()

    if not branch:
        raise HTTPException(status_code=404, detail="Branch not found")

    for field, value in branch_data.dict(exclude_unset=True).items():
        setattr(branch, field, value)

    db.commit()
    return {"message": "Branch updated successfully"}


@router.delete("/{branch_id}")
async def delete_branch(
    branch_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Deactivate branch"""
    tenant_id = current_user["tenant_id"]

    branch = db.query(Branch).filter(
        Branch.id == branch_id,
        Branch.tenant_id == tenant_id
    ).first()

    if not branch:
        raise HTTPException(status_code=404, detail="Branch not found")

    if branch.is_head_office:
        raise HTTPException(status_code=400, detail="Cannot deactivate head office")

    # Check for users in branch
    from ..models.user import User
    users = db.query(User).filter(User.branch_id == branch_id).count()
    if users > 0:
        branch.is_active = False
        db.commit()
        return {"message": f"Branch deactivated (has {users} users)"}

    db.delete(branch)
    db.commit()
    return {"message": "Branch deleted successfully"}


@router.post("/{branch_id}/set-head-office")
async def set_head_office(
    branch_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Set branch as head office"""
    tenant_id = current_user["tenant_id"]

    branch = db.query(Branch).filter(
        Branch.id == branch_id,
        Branch.tenant_id == tenant_id
    ).first()

    if not branch:
        raise HTTPException(status_code=404, detail="Branch not found")

    # Remove head office from all branches
    db.query(Branch).filter(
        Branch.tenant_id == tenant_id
    ).update({"is_head_office": False})

    branch.is_head_office = True
    db.commit()

    return {"message": f"{branch.name} set as head office"}
