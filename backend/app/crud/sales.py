"""
Sales Invoice CRUD Operations
"""

from typing import Optional, List
from sqlalchemy.orm import Session
from sqlalchemy import or_, func
from datetime import datetime, date

from ..models.sales import SalesInvoice, SalesInvoiceItem, CreditNote, CreditNoteItem
from ..models.customer import Customer


class CRUDSalesInvoice:
    
    def get(self, db: Session, invoice_id: int) -> Optional[SalesInvoice]:
        """Get invoice by ID with items"""
        return db.query(SalesInvoice).filter(SalesInvoice.id == invoice_id).first()
    
    def get_multi(
        self,
        db: Session,
        tenant_id: int,
        branch_id: int = None,
        customer_id: int = None,
        skip: int = 0,
        limit: int = 50,
        status: str = None,
        start_date: date = None,
        end_date: date = None,
        search: str = None
    ) -> List[SalesInvoice]:
        """Get multiple invoices with filters"""
        query = db.query(SalesInvoice).filter(SalesInvoice.tenant_id == tenant_id)
        
        if branch_id:
            query = query.filter(SalesInvoice.branch_id == branch_id)
        
        if customer_id:
            query = query.filter(SalesInvoice.customer_id == customer_id)
        
        if status:
            query = query.filter(SalesInvoice.status == status)
        
        if start_date:
            query = query.filter(SalesInvoice.invoice_date >= start_date)
        
        if end_date:
            query = query.filter(SalesInvoice.invoice_date <= end_date)
        
        if search:
            search_term = f"%{search}%"
            query = query.filter(
                or_(
                    SalesInvoice.invoice_number.ilike(search_term),
                    SalesInvoice.customer.has(Customer.name.ilike(search_term))
                )
            )
        
        return query.order_by(SalesInvoice.invoice_date.desc()).offset(skip).limit(limit).all()
    
    def count(
        self,
        db: Session,
        tenant_id: int,
        branch_id: int = None,
        status: str = None
    ) -> int:
        """Count invoices"""
        query = db.query(func.count(SalesInvoice.id)).filter(
            SalesInvoice.tenant_id == tenant_id
        )
        
        if branch_id:
            query = query.filter(SalesInvoice.branch_id == branch_id)
        
        if status:
            query = query.filter(SalesInvoice.status == status)
        
        return query.scalar() or 0
    
    def create(
        self,
        db: Session,
        *,
        tenant_id: int,
        branch_id: int,
        customer_id: int,
        invoice_date: date,
        due_date: date = None,
        items: List[dict],
        discount_amount: float = 0,
        notes: str = None,
        terms: str = None,
        vat_rate: float = 7.5
    ) -> SalesInvoice:
        """Create sales invoice with items"""
        # Generate invoice number
        invoice_number = self._generate_invoice_number(db, tenant_id, invoice_date)
        
        # Calculate totals
        subtotal = sum(item['quantity'] * item['unit_price'] for item in items)
        vat_amount = sum(
            item['quantity'] * item['unit_price'] * (item.get('vat_percent', vat_rate) / 100)
            for item in items
        )
        total_amount = subtotal + vat_amount - discount_amount
        
        # Create invoice
        invoice = SalesInvoice(
            tenant_id=tenant_id,
            branch_id=branch_id,
            customer_id=customer_id,
            invoice_number=invoice_number,
            invoice_date=invoice_date,
            due_date=due_date,
            subtotal=subtotal,
            discount_amount=discount_amount,
            vat_amount=vat_amount,
            total_amount=total_amount,
            notes=notes,
            terms=terms
        )
        db.add(invoice)
        db.flush()  # Get ID
        
        # Create items
        for item_data in items:
            item = SalesInvoiceItem(
                sales_invoice_id=invoice.id,
                product_id=item_data.get('product_id'),
                description=item_data['description'],
                quantity=item_data['quantity'],
                unit_price=item_data['unit_price'],
                discount_percent=item_data.get('discount_percent', 0),
                vat_percent=item_data.get('vat_percent', vat_rate),
                line_total=item_data['quantity'] * item_data['unit_price']
            )
            db.add(item)
        
        db.commit()
        db.refresh(invoice)
        return invoice
    
    def _generate_invoice_number(self, db: Session, tenant_id: int, inv_date: date) -> str:
        """Generate sequential invoice number"""
        year = inv_date.year
        month = inv_date.month
        
        last_invoice = db.query(SalesInvoice).filter(
            SalesInvoice.tenant_id == tenant_id,
            SalesInvoice.invoice_number.like(f"INV-{year}{month:02d}-%")
        ).order_by(SalesInvoice.invoice_number.desc()).first()
        
        if last_invoice:
            last_num = int(last_invoice.invoice_number.split('-')[-1])
            new_num = last_num + 1
        else:
            new_num = 1
        
        return f"INV-{year}{month:02d}-{new_num:05d}"
    
    def update(
        self,
        db: Session,
        *,
        invoice: SalesInvoice,
        **kwargs
    ) -> SalesInvoice:
        """Update invoice"""
        for key, value in kwargs.items():
            if hasattr(invoice, key):
                setattr(invoice, key, value)
        db.commit()
        db.refresh(invoice)
        return invoice
    
    def record_payment(
        self,
        db: Session,
        invoice_id: int,
        amount: float
    ) -> SalesInvoice:
        """Record payment against invoice"""
        invoice = self.get(db, invoice_id)
        if not invoice:
            raise ValueError("Invoice not found")
        
        invoice.paid_amount += amount
        
        # Update status
        if invoice.paid_amount >= invoice.total_amount:
            invoice.status = 'paid'
        elif invoice.paid_amount > 0:
            invoice.status = 'partially_paid'
        
        db.commit()
        db.refresh(invoice)
        return invoice
    
    def delete(self, db: Session, invoice_id: int) -> bool:
        """Delete invoice (only if not posted)"""
        invoice = self.get(db, invoice_id)
        if invoice and not invoice.is_posted:
            db.delete(invoice)
            db.commit()
            return True
        return False


class CRUDCreditNote:
    
    def get(self, db: Session, credit_note_id: int) -> Optional[CreditNote]:
        return db.query(CreditNote).filter(CreditNote.id == credit_note_id).first()
    
    def get_multi(
        self,
        db: Session,
        tenant_id: int,
        branch_id: int = None,
        skip: int = 0,
        limit: int = 50
    ) -> List[CreditNote]:
        query = db.query(CreditNote).filter(CreditNote.tenant_id == tenant_id)
        
        if branch_id:
            query = query.filter(CreditNote.branch_id == branch_id)
        
        return query.order_by(CreditNote.credit_note_date.desc()).offset(skip).limit(limit).all()
    
    def create(
        self,
        db: Session,
        *,
        tenant_id: int,
        branch_id: int,
        customer_id: int,
        credit_note_date: date,
        items: List[dict],
        reason: str = None,
        sales_invoice_id: int = None
    ) -> CreditNote:
        """Create credit note"""
        credit_note_number = self._generate_credit_note_number(db, tenant_id, credit_note_date)
        total_amount = sum(item['quantity'] * item['unit_price'] for item in items)
        
        credit_note = CreditNote(
            tenant_id=tenant_id,
            branch_id=branch_id,
            customer_id=customer_id,
            sales_invoice_id=sales_invoice_id,
            credit_note_number=credit_note_number,
            credit_note_date=credit_note_date,
            total_amount=total_amount,
            reason=reason
        )
        db.add(credit_note)
        db.flush()
        
        for item_data in items:
            item = CreditNoteItem(
                credit_note_id=credit_note.id,
                product_id=item_data.get('product_id'),
                description=item_data['description'],
                quantity=item_data['quantity'],
                unit_price=item_data['unit_price'],
                line_total=item_data['quantity'] * item_data['unit_price']
            )
            db.add(item)
        
        db.commit()
        db.refresh(credit_note)
        return credit_note
    
    def _generate_credit_note_number(self, db: Session, tenant_id: int, cn_date: date) -> str:
        year = cn_date.year
        month = cn_date.month
        
        last_cn = db.query(CreditNote).filter(
            CreditNote.tenant_id == tenant_id,
            CreditNote.credit_note_number.like(f"CN-{year}{month:02d}-%")
        ).order_by(CreditNote.credit_note_number.desc()).first()
        
        if last_cn:
            last_num = int(last_cn.credit_note_number.split('-')[-1])
            new_num = last_num + 1
        else:
            new_num = 1
        
        return f"CN-{year}{month:02d}-{new_num:05d}"


sales_invoice = CRUDSalesInvoice()
credit_note = CRUDCreditNote()
