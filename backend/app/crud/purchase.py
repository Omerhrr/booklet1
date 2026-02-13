"""
Purchase Bill CRUD Operations
"""

from typing import Optional, List
from sqlalchemy.orm import Session
from sqlalchemy import or_, func
from datetime import date

from ..models.purchase import PurchaseBill, PurchaseBillItem, DebitNote, DebitNoteItem
from ..models.vendor import Vendor


class CRUDPurchaseBill:
    
    def get(self, db: Session, bill_id: int) -> Optional[PurchaseBill]:
        return db.query(PurchaseBill).filter(PurchaseBill.id == bill_id).first()
    
    def get_multi(
        self,
        db: Session,
        tenant_id: int,
        branch_id: int = None,
        vendor_id: int = None,
        skip: int = 0,
        limit: int = 50,
        status: str = None,
        start_date: date = None,
        end_date: date = None,
        search: str = None
    ) -> List[PurchaseBill]:
        query = db.query(PurchaseBill).filter(PurchaseBill.tenant_id == tenant_id)
        
        if branch_id:
            query = query.filter(PurchaseBill.branch_id == branch_id)
        
        if vendor_id:
            query = query.filter(PurchaseBill.vendor_id == vendor_id)
        
        if status:
            query = query.filter(PurchaseBill.status == status)
        
        if start_date:
            query = query.filter(PurchaseBill.bill_date >= start_date)
        
        if end_date:
            query = query.filter(PurchaseBill.bill_date <= end_date)
        
        if search:
            search_term = f"%{search}%"
            query = query.filter(
                or_(
                    PurchaseBill.bill_number.ilike(search_term),
                    PurchaseBill.vendor.has(Vendor.name.ilike(search_term))
                )
            )
        
        return query.order_by(PurchaseBill.bill_date.desc()).offset(skip).limit(limit).all()
    
    def create(
        self,
        db: Session,
        *,
        tenant_id: int,
        branch_id: int,
        vendor_id: int,
        bill_date: date,
        due_date: date = None,
        items: List[dict],
        notes: str = None,
        vat_rate: float = 7.5
    ) -> PurchaseBill:
        """Create purchase bill with items"""
        bill_number = self._generate_bill_number(db, tenant_id, bill_date)
        
        subtotal = sum(item['quantity'] * item['unit_price'] for item in items)
        vat_amount = sum(
            item['quantity'] * item['unit_price'] * (item.get('vat_percent', vat_rate) / 100)
            for item in items
        )
        total_amount = subtotal + vat_amount
        
        bill = PurchaseBill(
            tenant_id=tenant_id,
            branch_id=branch_id,
            vendor_id=vendor_id,
            bill_number=bill_number,
            bill_date=bill_date,
            due_date=due_date,
            subtotal=subtotal,
            vat_amount=vat_amount,
            total_amount=total_amount,
            notes=notes
        )
        db.add(bill)
        db.flush()
        
        for item_data in items:
            item = PurchaseBillItem(
                purchase_bill_id=bill.id,
                product_id=item_data.get('product_id'),
                description=item_data['description'],
                quantity=item_data['quantity'],
                unit_price=item_data['unit_price'],
                vat_percent=item_data.get('vat_percent', vat_rate),
                line_total=item_data['quantity'] * item_data['unit_price']
            )
            db.add(item)
        
        db.commit()
        db.refresh(bill)
        return bill
    
    def _generate_bill_number(self, db: Session, tenant_id: int, bill_date: date) -> str:
        year = bill_date.year
        month = bill_date.month
        
        last_bill = db.query(PurchaseBill).filter(
            PurchaseBill.tenant_id == tenant_id,
            PurchaseBill.bill_number.like(f"PO-{year}{month:02d}-%")
        ).order_by(PurchaseBill.bill_number.desc()).first()
        
        if last_bill:
            last_num = int(last_bill.bill_number.split('-')[-1])
            new_num = last_num + 1
        else:
            new_num = 1
        
        return f"PO-{year}{month:02d}-{new_num:05d}"
    
    def record_payment(
        self,
        db: Session,
        bill_id: int,
        amount: float
    ) -> PurchaseBill:
        """Record payment against bill"""
        bill = self.get(db, bill_id)
        if not bill:
            raise ValueError("Bill not found")
        
        bill.paid_amount += amount
        
        if bill.paid_amount >= bill.total_amount:
            bill.status = 'paid'
        elif bill.paid_amount > 0:
            bill.status = 'partially_paid'
        
        db.commit()
        db.refresh(bill)
        return bill


class CRUDDebitNote:
    
    def get(self, db: Session, debit_note_id: int) -> Optional[DebitNote]:
        return db.query(DebitNote).filter(DebitNote.id == debit_note_id).first()
    
    def get_multi(
        self,
        db: Session,
        tenant_id: int,
        branch_id: int = None,
        skip: int = 0,
        limit: int = 50
    ) -> List[DebitNote]:
        query = db.query(DebitNote).filter(DebitNote.tenant_id == tenant_id)
        
        if branch_id:
            query = query.filter(DebitNote.branch_id == branch_id)
        
        return query.order_by(DebitNote.debit_note_date.desc()).offset(skip).limit(limit).all()
    
    def create(
        self,
        db: Session,
        *,
        tenant_id: int,
        branch_id: int,
        vendor_id: int,
        debit_note_date: date,
        items: List[dict],
        reason: str = None,
        purchase_bill_id: int = None
    ) -> DebitNote:
        """Create debit note"""
        debit_note_number = self._generate_debit_note_number(db, tenant_id, debit_note_date)
        total_amount = sum(item['quantity'] * item['unit_price'] for item in items)
        
        debit_note = DebitNote(
            tenant_id=tenant_id,
            branch_id=branch_id,
            vendor_id=vendor_id,
            purchase_bill_id=purchase_bill_id,
            debit_note_number=debit_note_number,
            debit_note_date=debit_note_date,
            total_amount=total_amount,
            reason=reason
        )
        db.add(debit_note)
        db.flush()
        
        for item_data in items:
            item = DebitNoteItem(
                debit_note_id=debit_note.id,
                product_id=item_data.get('product_id'),
                description=item_data['description'],
                quantity=item_data['quantity'],
                unit_price=item_data['unit_price'],
                line_total=item_data['quantity'] * item_data['unit_price']
            )
            db.add(item)
        
        db.commit()
        db.refresh(debit_note)
        return debit_note
    
    def _generate_debit_note_number(self, db: Session, tenant_id: int, dn_date: date) -> str:
        year = dn_date.year
        month = dn_date.month
        
        last_dn = db.query(DebitNote).filter(
            DebitNote.tenant_id == tenant_id,
            DebitNote.debit_note_number.like(f"DN-{year}{month:02d}-%")
        ).order_by(DebitNote.debit_note_number.desc()).first()
        
        if last_dn:
            last_num = int(last_dn.debit_note_number.split('-')[-1])
            new_num = last_num + 1
        else:
            new_num = 1
        
        return f"DN-{year}{month:02d}-{new_num:05d}"


purchase_bill = CRUDPurchaseBill()
debit_note = CRUDDebitNote()
