"""
Purchases Router - Purchase Bills, Debit Notes
"""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime, timedelta
from pydantic import BaseModel
from enum import Enum

from ..database import get_db
from ..security import get_current_user
from ..models.purchase import PurchaseBill, PurchaseBillItem, DebitNote, DebitNoteItem
from ..models.vendor import Vendor
from ..models.product import Product

router = APIRouter(prefix="/purchases", tags=["Purchases"])


# === Pydantic Schemas ===

class PurchaseItemCreate(BaseModel):
    product_id: Optional[int] = None
    description: str
    quantity: float = 1
    unit_price: float = 0
    vat_percent: float = 7.5

class PurchaseBillCreate(BaseModel):
    vendor_id: int
    bill_date: datetime
    due_date: Optional[datetime] = None
    items: List[PurchaseItemCreate]
    reference: Optional[str] = None
    notes: Optional[str] = None
    branch_id: int

class DebitNoteCreate(BaseModel):
    vendor_id: int
    purchase_bill_id: Optional[int] = None
    debit_note_date: datetime
    items: List[PurchaseItemCreate]
    reason: Optional[str] = None
    branch_id: int


# === Purchase Bills ===

@router.get("/bills")
async def list_bills(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, le=200),
    vendor_id: Optional[int] = None,
    is_paid: Optional[bool] = None,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """List purchase bills"""
    tenant_id = current_user["tenant_id"]

    query = db.query(PurchaseBill).filter(PurchaseBill.tenant_id == tenant_id)

    if vendor_id:
        query = query.filter(PurchaseBill.vendor_id == vendor_id)
    if is_paid is not None:
        query = query.filter(PurchaseBill.is_paid == is_paid)
    if start_date:
        query = query.filter(PurchaseBill.bill_date >= start_date)
    if end_date:
        query = query.filter(PurchaseBill.bill_date <= end_date)

    bills = query.order_by(PurchaseBill.created_at.desc()).offset(skip).limit(limit).all()

    vendor_ids = list(set(b.vendor_id for b in bills))
    vendors = {v.id: v for v in db.query(Vendor).filter(Vendor.id.in_(vendor_ids)).all()}

    return {
        "items": [{
            "id": b.id,
            "bill_number": b.bill_number,
            "vendor_id": b.vendor_id,
            "vendor_name": vendors.get(b.vendor_id, Vendor(name="Unknown")).name,
            "bill_date": b.bill_date.isoformat(),
            "due_date": b.due_date.isoformat() if b.due_date else None,
            "total_amount": b.total_amount,
            "paid_amount": b.paid_amount,
            "balance": b.total_amount - b.paid_amount,
            "is_paid": b.is_paid,
            "is_posted": b.is_posted
        } for b in bills],
        "total": query.count()
    }


@router.post("/bills")
async def create_bill(
    bill_data: PurchaseBillCreate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Create purchase bill"""
    tenant_id = current_user["tenant_id"]

    # Verify vendor exists
    vendor = db.query(Vendor).filter(
        Vendor.id == bill_data.vendor_id,
        Vendor.tenant_id == tenant_id
    ).first()

    if not vendor:
        raise HTTPException(status_code=404, detail="Vendor not found")

    # Generate bill number
    last_bill = db.query(PurchaseBill).filter(
        PurchaseBill.tenant_id == tenant_id
    ).order_by(PurchaseBill.id.desc()).first()

    bill_num = f"PB-{datetime.now().year}-{(last_bill.id + 1) if last_bill else 1:05d}"

    # Set default due date (30 days)
    if not bill_data.due_date:
        bill_data.due_date = bill_data.bill_date + timedelta(days=30)

    # Calculate totals
    subtotal = 0
    vat_amount = 0

    for item in bill_data.items:
        line_subtotal = item.quantity * item.unit_price
        line_vat = line_subtotal * (item.vat_percent / 100)
        subtotal += line_subtotal
        vat_amount += line_vat

    total_amount = subtotal + vat_amount

    bill = PurchaseBill(
        tenant_id=tenant_id,
        branch_id=bill_data.branch_id,
        vendor_id=bill_data.vendor_id,
        bill_number=bill_num,
        bill_date=bill_data.bill_date,
        due_date=bill_data.due_date,
        subtotal=subtotal,
        vat_amount=vat_amount,
        total_amount=total_amount,
        reference=bill_data.reference,
        notes=bill_data.notes
    )

    db.add(bill)
    db.flush()

    for item_data in bill_data.items:
        line_subtotal = item_data.quantity * item_data.unit_price
        line_vat = line_subtotal * (item_data.vat_percent / 100)
        line_total = line_subtotal + line_vat

        item = PurchaseBillItem(
            purchase_bill_id=bill.id,
            product_id=item_data.product_id,
            description=item_data.description,
            quantity=item_data.quantity,
            unit_price=item_data.unit_price,
            vat_percent=item_data.vat_percent,
            line_total=line_total
        )
        db.add(item)

        # Update product stock and cost
        if item_data.product_id:
            product = db.query(Product).filter(Product.id == item_data.product_id).first()
            if product and product.track_inventory:
                product.stock_quantity += item_data.quantity
                # Update purchase price
                product.purchase_price = item_data.unit_price

    db.commit()

    return {
        "id": bill.id,
        "bill_number": bill_num,
        "total_amount": total_amount,
        "message": "Purchase bill created successfully"
    }


@router.get("/bills/{bill_id}")
async def get_bill(
    bill_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Get purchase bill details"""
    tenant_id = current_user["tenant_id"]

    bill = db.query(PurchaseBill).filter(
        PurchaseBill.id == bill_id,
        PurchaseBill.tenant_id == tenant_id
    ).first()

    if not bill:
        raise HTTPException(status_code=404, detail="Purchase bill not found")

    items = db.query(PurchaseBillItem).filter(
        PurchaseBillItem.purchase_bill_id == bill_id
    ).all()

    vendor = db.query(Vendor).filter(Vendor.id == bill.vendor_id).first()

    return {
        "id": bill.id,
        "bill_number": bill.bill_number,
        "vendor": {
            "id": vendor.id,
            "name": vendor.name,
            "email": vendor.email,
            "phone": vendor.phone,
            "address": vendor.address
        } if vendor else None,
        "bill_date": bill.bill_date.isoformat(),
        "due_date": bill.due_date.isoformat() if bill.due_date else None,
        "items": [{
            "id": i.id,
            "product_id": i.product_id,
            "description": i.description,
            "quantity": i.quantity,
            "unit_price": i.unit_price,
            "vat_percent": i.vat_percent,
            "line_total": i.line_total
        } for i in items],
        "subtotal": bill.subtotal,
        "vat_amount": bill.vat_amount,
        "total_amount": bill.total_amount,
        "paid_amount": bill.paid_amount,
        "balance": bill.total_amount - bill.paid_amount,
        "is_paid": bill.is_paid,
        "reference": bill.reference,
        "notes": bill.notes,
        "is_posted": bill.is_posted
    }


@router.post("/bills/{bill_id}/post")
async def post_bill(
    bill_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Post purchase bill to ledger"""
    tenant_id = current_user["tenant_id"]

    bill = db.query(PurchaseBill).filter(
        PurchaseBill.id == bill_id,
        PurchaseBill.tenant_id == tenant_id
    ).first()

    if not bill:
        raise HTTPException(status_code=404, detail="Purchase bill not found")

    if bill.is_posted:
        raise HTTPException(status_code=400, detail="Bill already posted")

    bill.is_posted = True
    bill.posted_at = datetime.utcnow()

    db.commit()

    return {"message": "Purchase bill posted successfully"}


@router.delete("/bills/{bill_id}")
async def delete_bill(
    bill_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Delete purchase bill (only if not posted)"""
    tenant_id = current_user["tenant_id"]

    bill = db.query(PurchaseBill).filter(
        PurchaseBill.id == bill_id,
        PurchaseBill.tenant_id == tenant_id
    ).first()

    if not bill:
        raise HTTPException(status_code=404, detail="Purchase bill not found")

    if bill.is_posted:
        raise HTTPException(status_code=400, detail="Cannot delete posted bill")

    # Restore stock
    items = db.query(PurchaseBillItem).filter(
        PurchaseBillItem.purchase_bill_id == bill_id
    ).all()

    for item in items:
        if item.product_id:
            product = db.query(Product).filter(Product.id == item.product_id).first()
            if product and product.track_inventory:
                product.stock_quantity -= item.quantity

    # Delete items
    db.query(PurchaseBillItem).filter(
        PurchaseBillItem.purchase_bill_id == bill_id
    ).delete()

    db.delete(bill)
    db.commit()

    return {"message": "Purchase bill deleted successfully"}


# === Debit Notes ===

@router.get("/debit-notes")
async def list_debit_notes(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, le=200),
    vendor_id: Optional[int] = None,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """List debit notes"""
    tenant_id = current_user["tenant_id"]

    query = db.query(DebitNote).filter(DebitNote.tenant_id == tenant_id)

    if vendor_id:
        query = query.filter(DebitNote.vendor_id == vendor_id)

    debit_notes = query.order_by(DebitNote.created_at.desc()).offset(skip).limit(limit).all()

    vendor_ids = list(set(dn.vendor_id for dn in debit_notes))
    vendors = {v.id: v for v in db.query(Vendor).filter(Vendor.id.in_(vendor_ids)).all()}

    return {
        "items": [{
            "id": dn.id,
            "debit_note_number": dn.debit_note_number,
            "vendor_name": vendors.get(dn.vendor_id, Vendor(name="Unknown")).name,
            "debit_note_date": dn.debit_note_date.isoformat(),
            "total_amount": dn.total_amount,
            "reason": dn.reason
        } for dn in debit_notes],
        "total": query.count()
    }


@router.post("/debit-notes")
async def create_debit_note(
    debit_note_data: DebitNoteCreate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Create debit note"""
    tenant_id = current_user["tenant_id"]

    last_dn = db.query(DebitNote).filter(
        DebitNote.tenant_id == tenant_id
    ).order_by(DebitNote.id.desc()).first()

    dn_num = f"DN-{datetime.now().year}-{(last_dn.id + 1) if last_dn else 1:05d}"

    total_amount = sum(
        item.quantity * item.unit_price for item in debit_note_data.items
    )

    debit_note = DebitNote(
        tenant_id=tenant_id,
        branch_id=debit_note_data.branch_id,
        vendor_id=debit_note_data.vendor_id,
        purchase_bill_id=debit_note_data.purchase_bill_id,
        debit_note_number=dn_num,
        debit_note_date=debit_note_data.debit_note_date,
        total_amount=total_amount,
        reason=debit_note_data.reason
    )

    db.add(debit_note)
    db.flush()

    for item_data in debit_note_data.items:
        item = DebitNoteItem(
            debit_note_id=debit_note.id,
            product_id=item_data.product_id,
            description=item_data.description,
            quantity=item_data.quantity,
            unit_price=item_data.unit_price,
            line_total=item_data.quantity * item_data.unit_price
        )
        db.add(item)

        # Reduce stock
        if item_data.product_id:
            product = db.query(Product).filter(Product.id == item_data.product_id).first()
            if product and product.track_inventory:
                product.stock_quantity -= item_data.quantity

    db.commit()

    return {
        "id": debit_note.id,
        "debit_note_number": dn_num,
        "message": "Debit note created successfully"
    }


# === Dashboard Stats ===

@router.get("/dashboard")
async def get_purchases_dashboard(
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Get purchases dashboard statistics"""
    tenant_id = current_user["tenant_id"]

    from datetime import datetime
    first_day = datetime.now().replace(day=1, hour=0, minute=0, second=0, microsecond=0)

    total_purchases = db.query(db.func.sum(PurchaseBill.total_amount)).filter(
        PurchaseBill.tenant_id == tenant_id,
        PurchaseBill.bill_date >= first_day
    ).scalar() or 0

    outstanding = db.query(db.func.sum(PurchaseBill.total_amount - PurchaseBill.paid_amount)).filter(
        PurchaseBill.tenant_id == tenant_id,
        PurchaseBill.is_paid == False
    ).scalar() or 0

    overdue_count = db.query(PurchaseBill).filter(
        PurchaseBill.tenant_id == tenant_id,
        PurchaseBill.due_date < datetime.now(),
        PurchaseBill.is_paid == False
    ).count()

    return {
        "total_purchases_month": total_purchases,
        "outstanding_payables": outstanding,
        "overdue_bills": overdue_count
    }
