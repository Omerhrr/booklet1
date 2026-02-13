"""
Sales Router - Invoices, Credit Notes
"""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime, timedelta
from pydantic import BaseModel
from enum import Enum

from ..database import get_db
from ..security import get_current_user
from ..models.sales import SalesInvoice, SalesInvoiceItem, CreditNote, CreditNoteItem, InvoicePaymentStatus
from ..models.customer import Customer
from ..models.product import Product

router = APIRouter(prefix="/sales", tags=["Sales"])


# === Pydantic Schemas ===

class InvoiceItemCreate(BaseModel):
    product_id: Optional[int] = None
    description: str
    quantity: float = 1
    unit_price: float = 0
    discount_percent: float = 0
    vat_percent: float = 7.5  # Nigerian VAT

class InvoiceCreate(BaseModel):
    customer_id: int
    invoice_date: datetime
    due_date: Optional[datetime] = None
    items: List[InvoiceItemCreate]
    notes: Optional[str] = None
    terms: Optional[str] = None
    branch_id: int

class InvoiceUpdate(BaseModel):
    notes: Optional[str] = None
    terms: Optional[str] = None

class CreditNoteCreate(BaseModel):
    customer_id: int
    sales_invoice_id: Optional[int] = None
    credit_note_date: datetime
    items: List[InvoiceItemCreate]
    reason: Optional[str] = None
    branch_id: int


# === Sales Invoices ===

@router.get("/invoices")
async def list_invoices(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, le=200),
    status: Optional[InvoicePaymentStatus] = None,
    customer_id: Optional[int] = None,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """List sales invoices"""
    tenant_id = current_user["tenant_id"]

    query = db.query(SalesInvoice).filter(SalesInvoice.tenant_id == tenant_id)

    if status:
        query = query.filter(SalesInvoice.status == status)
    if customer_id:
        query = query.filter(SalesInvoice.customer_id == customer_id)
    if start_date:
        query = query.filter(SalesInvoice.invoice_date >= start_date)
    if end_date:
        query = query.filter(SalesInvoice.invoice_date <= end_date)

    invoices = query.order_by(SalesInvoice.created_at.desc()).offset(skip).limit(limit).all()

    # Get customer names
    customer_ids = list(set(i.customer_id for i in invoices))
    customers = {c.id: c for c in db.query(Customer).filter(Customer.id.in_(customer_ids)).all()}

    return {
        "items": [{
            "id": i.id,
            "invoice_number": i.invoice_number,
            "customer_id": i.customer_id,
            "customer_name": customers.get(i.customer_id, Customer(name="Unknown")).name,
            "invoice_date": i.invoice_date.isoformat(),
            "due_date": i.due_date.isoformat() if i.due_date else None,
            "total_amount": i.total_amount,
            "paid_amount": i.paid_amount,
            "balance": i.total_amount - i.paid_amount,
            "status": i.status.value,
            "is_posted": i.is_posted
        } for i in invoices],
        "total": query.count()
    }


@router.post("/invoices")
async def create_invoice(
    invoice_data: InvoiceCreate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Create sales invoice"""
    tenant_id = current_user["tenant_id"]

    # Verify customer exists
    customer = db.query(Customer).filter(
        Customer.id == invoice_data.customer_id,
        Customer.tenant_id == tenant_id
    ).first()

    if not customer:
        raise HTTPException(status_code=404, detail="Customer not found")

    # Generate invoice number
    last_invoice = db.query(SalesInvoice).filter(
        SalesInvoice.tenant_id == tenant_id
    ).order_by(SalesInvoice.id.desc()).first()

    invoice_num = f"INV-{datetime.now().year}-{(last_invoice.id + 1) if last_invoice else 1:05d}"

    # Set default due date (30 days)
    if not invoice_data.due_date:
        invoice_data.due_date = invoice_data.invoice_date + timedelta(days=30)

    # Calculate totals
    subtotal = 0
    vat_amount = 0

    for item in invoice_data.items:
        line_subtotal = item.quantity * item.unit_price
        line_discount = line_subtotal * (item.discount_percent / 100)
        line_vat = (line_subtotal - line_discount) * (item.vat_percent / 100)
        subtotal += line_subtotal - line_discount
        vat_amount += line_vat

    total_amount = subtotal + vat_amount

    # Create invoice
    invoice = SalesInvoice(
        tenant_id=tenant_id,
        branch_id=invoice_data.branch_id,
        customer_id=invoice_data.customer_id,
        invoice_number=invoice_num,
        invoice_date=invoice_data.invoice_date,
        due_date=invoice_data.due_date,
        subtotal=subtotal,
        vat_amount=vat_amount,
        total_amount=total_amount,
        notes=invoice_data.notes,
        terms=invoice_data.terms
    )

    db.add(invoice)
    db.flush()

    # Create invoice items
    for item_data in invoice_data.items:
        line_subtotal = item_data.quantity * item_data.unit_price
        line_discount = line_subtotal * (item_data.discount_percent / 100)
        line_vat = (line_subtotal - line_discount) * (item_data.vat_percent / 100)
        line_total = line_subtotal - line_discount + line_vat

        item = SalesInvoiceItem(
            sales_invoice_id=invoice.id,
            product_id=item_data.product_id,
            description=item_data.description,
            quantity=item_data.quantity,
            unit_price=item_data.unit_price,
            discount_percent=item_data.discount_percent,
            vat_percent=item_data.vat_percent,
            line_total=line_total
        )
        db.add(item)

        # Update product stock if applicable
        if item_data.product_id:
            product = db.query(Product).filter(Product.id == item_data.product_id).first()
            if product and product.track_inventory:
                product.stock_quantity -= item_data.quantity

    db.commit()

    return {
        "id": invoice.id,
        "invoice_number": invoice_num,
        "total_amount": total_amount,
        "message": "Invoice created successfully"
    }


@router.get("/invoices/{invoice_id}")
async def get_invoice(
    invoice_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Get invoice details"""
    tenant_id = current_user["tenant_id"]

    invoice = db.query(SalesInvoice).filter(
        SalesInvoice.id == invoice_id,
        SalesInvoice.tenant_id == tenant_id
    ).first()

    if not invoice:
        raise HTTPException(status_code=404, detail="Invoice not found")

    # Get items
    items = db.query(SalesInvoiceItem).filter(
        SalesInvoiceItem.sales_invoice_id == invoice_id
    ).all()

    # Get customer
    customer = db.query(Customer).filter(Customer.id == invoice.customer_id).first()

    return {
        "id": invoice.id,
        "invoice_number": invoice.invoice_number,
        "customer": {
            "id": customer.id,
            "name": customer.name,
            "email": customer.email,
            "phone": customer.phone,
            "address": customer.address
        } if customer else None,
        "invoice_date": invoice.invoice_date.isoformat(),
        "due_date": invoice.due_date.isoformat() if invoice.due_date else None,
        "items": [{
            "id": i.id,
            "product_id": i.product_id,
            "description": i.description,
            "quantity": i.quantity,
            "unit_price": i.unit_price,
            "discount_percent": i.discount_percent,
            "vat_percent": i.vat_percent,
            "line_total": i.line_total
        } for i in items],
        "subtotal": invoice.subtotal,
        "discount_amount": invoice.discount_amount,
        "vat_amount": invoice.vat_amount,
        "total_amount": invoice.total_amount,
        "paid_amount": invoice.paid_amount,
        "balance": invoice.total_amount - invoice.paid_amount,
        "status": invoice.status.value,
        "notes": invoice.notes,
        "terms": invoice.terms,
        "is_posted": invoice.is_posted,
        "created_at": invoice.created_at.isoformat() if invoice.created_at else None
    }


@router.post("/invoices/{invoice_id}/post")
async def post_invoice(
    invoice_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Post invoice to ledger"""
    tenant_id = current_user["tenant_id"]

    invoice = db.query(SalesInvoice).filter(
        SalesInvoice.id == invoice_id,
        SalesInvoice.tenant_id == tenant_id
    ).first()

    if not invoice:
        raise HTTPException(status_code=404, detail="Invoice not found")

    if invoice.is_posted:
        raise HTTPException(status_code=400, detail="Invoice already posted")

    invoice.is_posted = True
    invoice.posted_at = datetime.utcnow()

    db.commit()

    return {"message": "Invoice posted successfully"}


@router.delete("/invoices/{invoice_id}")
async def delete_invoice(
    invoice_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Delete invoice (only if not posted)"""
    tenant_id = current_user["tenant_id"]

    invoice = db.query(SalesInvoice).filter(
        SalesInvoice.id == invoice_id,
        SalesInvoice.tenant_id == tenant_id
    ).first()

    if not invoice:
        raise HTTPException(status_code=404, detail="Invoice not found")

    if invoice.is_posted:
        raise HTTPException(status_code=400, detail="Cannot delete posted invoice")

    # Delete items first
    db.query(SalesInvoiceItem).filter(
        SalesInvoiceItem.sales_invoice_id == invoice_id
    ).delete()

    # Restore stock
    items = db.query(SalesInvoiceItem).filter(
        SalesInvoiceItem.sales_invoice_id == invoice_id
    ).all()

    for item in items:
        if item.product_id:
            product = db.query(Product).filter(Product.id == item.product_id).first()
            if product:
                product.stock_quantity += item.quantity

    db.delete(invoice)
    db.commit()

    return {"message": "Invoice deleted successfully"}


# === Credit Notes ===

@router.get("/credit-notes")
async def list_credit_notes(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, le=200),
    customer_id: Optional[int] = None,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """List credit notes"""
    tenant_id = current_user["tenant_id"]

    query = db.query(CreditNote).filter(CreditNote.tenant_id == tenant_id)

    if customer_id:
        query = query.filter(CreditNote.customer_id == customer_id)

    credit_notes = query.order_by(CreditNote.created_at.desc()).offset(skip).limit(limit).all()

    customer_ids = list(set(cn.customer_id for cn in credit_notes))
    customers = {c.id: c for c in db.query(Customer).filter(Customer.id.in_(customer_ids)).all()}

    return {
        "items": [{
            "id": cn.id,
            "credit_note_number": cn.credit_note_number,
            "customer_name": customers.get(cn.customer_id, Customer(name="Unknown")).name,
            "credit_note_date": cn.credit_note_date.isoformat(),
            "total_amount": cn.total_amount,
            "reason": cn.reason
        } for cn in credit_notes],
        "total": query.count()
    }


@router.post("/credit-notes")
async def create_credit_note(
    credit_note_data: CreditNoteCreate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Create credit note"""
    tenant_id = current_user["tenant_id"]

    # Generate credit note number
    last_cn = db.query(CreditNote).filter(
        CreditNote.tenant_id == tenant_id
    ).order_by(CreditNote.id.desc()).first()

    cn_num = f"CN-{datetime.now().year}-{(last_cn.id + 1) if last_cn else 1:05d}"

    # Calculate total
    total_amount = sum(
        item.quantity * item.unit_price for item in credit_note_data.items
    )

    credit_note = CreditNote(
        tenant_id=tenant_id,
        branch_id=credit_note_data.branch_id,
        customer_id=credit_note_data.customer_id,
        sales_invoice_id=credit_note_data.sales_invoice_id,
        credit_note_number=cn_num,
        credit_note_date=credit_note_data.credit_note_date,
        total_amount=total_amount,
        reason=credit_note_data.reason
    )

    db.add(credit_note)
    db.flush()

    for item_data in credit_note_data.items:
        item = CreditNoteItem(
            credit_note_id=credit_note.id,
            product_id=item_data.product_id,
            description=item_data.description,
            quantity=item_data.quantity,
            unit_price=item_data.unit_price,
            line_total=item_data.quantity * item_data.unit_price
        )
        db.add(item)

        # Restore stock
        if item_data.product_id:
            product = db.query(Product).filter(Product.id == item_data.product_id).first()
            if product and product.track_inventory:
                product.stock_quantity += item_data.quantity

    db.commit()

    return {
        "id": credit_note.id,
        "credit_note_number": cn_num,
        "message": "Credit note created successfully"
    }


# === Dashboard Stats ===

@router.get("/dashboard")
async def get_sales_dashboard(
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Get sales dashboard statistics"""
    tenant_id = current_user["tenant_id"]

    # Total sales this month
    from datetime import datetime
    first_day = datetime.now().replace(day=1, hour=0, minute=0, second=0, microsecond=0)

    total_sales = db.query(db.func.sum(SalesInvoice.total_amount)).filter(
        SalesInvoice.tenant_id == tenant_id,
        SalesInvoice.invoice_date >= first_day
    ).scalar() or 0

    # Outstanding receivables
    outstanding = db.query(db.func.sum(SalesInvoice.total_amount - SalesInvoice.paid_amount)).filter(
        SalesInvoice.tenant_id == tenant_id,
        SalesInvoice.status != InvoicePaymentStatus.PAID
    ).scalar() or 0

    # Overdue invoices
    overdue_count = db.query(SalesInvoice).filter(
        SalesInvoice.tenant_id == tenant_id,
        SalesInvoice.due_date < datetime.now(),
        SalesInvoice.status != InvoicePaymentStatus.PAID
    ).count()

    return {
        "total_sales_month": total_sales,
        "outstanding_receivables": outstanding,
        "overdue_invoices": overdue_count
    }
