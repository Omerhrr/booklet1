"""
Customer Router - CRUD Operations
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from pydantic import BaseModel, EmailStr
from typing import Optional, List
from datetime import datetime

from ..database import get_db
from ..routers.auth import get_current_active_user
from ..security import PermissionChecker

router = APIRouter()


# Schemas
class CustomerCreate(BaseModel):
    name: str
    email: Optional[EmailStr] = None
    phone: Optional[str] = None
    address: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    country: str = "Nigeria"
    credit_limit: Optional[float] = None
    payment_terms: Optional[int] = None
    tax_id: Optional[str] = None


class CustomerUpdate(BaseModel):
    name: Optional[str] = None
    email: Optional[EmailStr] = None
    phone: Optional[str] = None
    address: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    country: Optional[str] = None
    credit_limit: Optional[float] = None
    payment_terms: Optional[int] = None
    tax_id: Optional[str] = None
    is_active: Optional[bool] = None


class CustomerResponse(BaseModel):
    id: int
    customer_number: Optional[str]
    name: str
    email: Optional[str]
    phone: Optional[str]
    address: Optional[str]
    city: Optional[str]
    state: Optional[str]
    country: str
    credit_limit: Optional[float]
    payment_terms: Optional[int]
    tax_id: Optional[str]
    is_active: bool
    balance: float = 0.0
    created_at: datetime
    
    class Config:
        from_attributes = True


@router.get("", response_model=List[CustomerResponse])
async def list_customers(
    skip: int = 0,
    limit: int = 50,
    search: Optional[str] = None,
    is_active: Optional[bool] = None,
    session: dict = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """List all customers"""
    # PermissionChecker(["customers:view"])(session["user"], db)
    
    # TODO: Implement actual query with tenant isolation
    return []


@router.post("", response_model=CustomerResponse, status_code=status.HTTP_201_CREATED)
async def create_customer(
    customer_data: CustomerCreate,
    session: dict = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Create new customer"""
    # PermissionChecker(["customers:create"])(session["user"], db)
    
    # TODO: Implement customer creation
    raise HTTPException(status_code=501, detail="Not implemented")


@router.get("/{customer_id}", response_model=CustomerResponse)
async def get_customer(
    customer_id: int,
    session: dict = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get customer by ID"""
    # PermissionChecker(["customers:view"])(session["user"], db)
    
    # TODO: Implement
    raise HTTPException(status_code=404, detail="Customer not found")


@router.put("/{customer_id}", response_model=CustomerResponse)
async def update_customer(
    customer_id: int,
    customer_data: CustomerUpdate,
    session: dict = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Update customer"""
    # PermissionChecker(["customers:edit"])(session["user"], db)
    
    # TODO: Implement
    raise HTTPException(status_code=404, detail="Customer not found")


@router.delete("/{customer_id}")
async def delete_customer(
    customer_id: int,
    session: dict = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Delete customer"""
    # PermissionChecker(["customers:delete"])(session["user"], db)
    
    # TODO: Implement
    raise HTTPException(status_code=404, detail="Customer not found")
