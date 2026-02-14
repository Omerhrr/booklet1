"""
Vendors Router - Supplier Management
"""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import Optional
from pydantic import BaseModel

from ..database import get_db
from ..security import get_current_user
from ..models.vendor import Vendor
from ..models.purchase import PurchaseBill

router = APIRouter(prefix="/vendors", tags=["Vendors"])


class VendorCreate(BaseModel):
    name: str
    email: Optional[str] = None
    phone: Optional[str] = None
    address: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    country: str = "Nigeria"
    tax_id: Optional[str] = None
    contact_person: Optional[str] = None
    payment_terms: Optional[str] = "Net 30"
    bank_name: Optional[str] = None
    bank_account: Optional[str] = None

class VendorUpdate(BaseModel):
    name: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    address: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    tax_id: Optional[str] = None
    contact_person: Optional[str] = None
    payment_terms: Optional[str] = None
    bank_name: Optional[str] = None
    bank_account: Optional[str] = None
    is_active: Optional[bool] = None


@router.get("")
async def list_vendors(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, le=200),
    is_active: Optional[bool] = None,
    search: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """List vendors"""
    tenant_id = current_user["tenant_id"]

    query = db.query(Vendor).filter(Vendor.tenant_id == tenant_id)

    if is_active is not None:
        query = query.filter(Vendor.is_active == is_active)
    if search:
        query = query.filter(Vendor.name.ilike(f"%{search}%"))

    vendors = query.order_by(Vendor.name).offset(skip).limit(limit).all()

    return {
        "items": [{
            "id": v.id,
            "name": v.name,
            "email": v.email,
            "phone": v.phone,
            "city": v.city,
            "state": v.state,
            "contact_person": v.contact_person,
            "payment_terms": v.payment_terms,
            "is_active": v.is_active
        } for v in vendors],
        "total": query.count()
    }


@router.post("")
async def create_vendor(
    vendor_data: VendorCreate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Create vendor"""
    tenant_id = current_user["tenant_id"]

    # Check for duplicate name
    existing = db.query(Vendor).filter(
        Vendor.tenant_id == tenant_id,
        Vendor.name == vendor_data.name
    ).first()

    if existing:
        raise HTTPException(status_code=400, detail="Vendor name already exists")

    vendor = Vendor(
        tenant_id=tenant_id,
        name=vendor_data.name,
        email=vendor_data.email,
        phone=vendor_data.phone,
        address=vendor_data.address,
        city=vendor_data.city,
        state=vendor_data.state,
        country=vendor_data.country,
        tax_id=vendor_data.tax_id,
        contact_person=vendor_data.contact_person,
        payment_terms=vendor_data.payment_terms,
        bank_name=vendor_data.bank_name,
        bank_account=vendor_data.bank_account
    )

    db.add(vendor)
    db.commit()
    db.refresh(vendor)

    return {"id": vendor.id, "message": "Vendor created successfully"}


@router.get("/{vendor_id}")
async def get_vendor(
    vendor_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Get vendor details"""
    tenant_id = current_user["tenant_id"]

    vendor = db.query(Vendor).filter(
        Vendor.id == vendor_id,
        Vendor.tenant_id == tenant_id
    ).first()

    if not vendor:
        raise HTTPException(status_code=404, detail="Vendor not found")

    # Calculate outstanding balance
    bills = db.query(PurchaseBill).filter(
        PurchaseBill.vendor_id == vendor_id
    ).all()

    total_purchases = sum(b.total_amount for b in bills)
    total_paid = sum(b.paid_amount for b in bills)
    outstanding = total_purchases - total_paid

    return {
        "id": vendor.id,
        "name": vendor.name,
        "email": vendor.email,
        "phone": vendor.phone,
        "address": vendor.address,
        "city": vendor.city,
        "state": vendor.state,
        "country": vendor.country,
        "tax_id": vendor.tax_id,
        "contact_person": vendor.contact_person,
        "payment_terms": vendor.payment_terms,
        "bank_name": vendor.bank_name,
        "bank_account": vendor.bank_account,
        "is_active": vendor.is_active,
        "stats": {
            "total_purchases": total_purchases,
            "total_paid": total_paid,
            "outstanding_balance": outstanding,
            "bill_count": len(bills)
        }
    }


@router.put("/{vendor_id}")
async def update_vendor(
    vendor_id: int,
    vendor_data: VendorUpdate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Update vendor"""
    tenant_id = current_user["tenant_id"]

    vendor = db.query(Vendor).filter(
        Vendor.id == vendor_id,
        Vendor.tenant_id == tenant_id
    ).first()

    if not vendor:
        raise HTTPException(status_code=404, detail="Vendor not found")

    for field, value in vendor_data.dict(exclude_unset=True).items():
        setattr(vendor, field, value)

    db.commit()
    return {"message": "Vendor updated successfully"}


@router.delete("/{vendor_id}")
async def delete_vendor(
    vendor_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Delete vendor (soft delete)"""
    tenant_id = current_user["tenant_id"]

    vendor = db.query(Vendor).filter(
        Vendor.id == vendor_id,
        Vendor.tenant_id == tenant_id
    ).first()

    if not vendor:
        raise HTTPException(status_code=404, detail="Vendor not found")

    # Check for existing bills
    bills = db.query(PurchaseBill).filter(PurchaseBill.vendor_id == vendor_id).count()
    if bills > 0:
        vendor.is_active = False
        db.commit()
        return {"message": "Vendor deactivated (has purchase history)"}

    db.delete(vendor)
    db.commit()
    return {"message": "Vendor deleted successfully"}
