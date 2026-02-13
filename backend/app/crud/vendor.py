"""
Vendor CRUD Operations
"""

from typing import Optional, List
from sqlalchemy.orm import Session
from sqlalchemy import or_, func
from datetime import datetime

from ..models.vendor import Vendor
from ..models.purchase import PurchaseBill


class CRUDVendor:
    
    def get(self, db: Session, vendor_id: int) -> Optional[Vendor]:
        """Get vendor by ID"""
        return db.query(Vendor).filter(Vendor.id == vendor_id).first()
    
    def get_multi(
        self,
        db: Session,
        tenant_id: int,
        branch_id: int = None,
        skip: int = 0,
        limit: int = 50,
        search: str = None,
        is_active: bool = None
    ) -> List[Vendor]:
        """Get multiple vendors with filters"""
        query = db.query(Vendor).filter(Vendor.tenant_id == tenant_id)
        
        if branch_id:
            query = query.filter(Vendor.branch_id == branch_id)
        
        if search:
            search_term = f"%{search}%"
            query = query.filter(
                or_(
                    Vendor.name.ilike(search_term),
                    Vendor.email.ilike(search_term),
                    Vendor.phone.ilike(search_term)
                )
            )
        
        if is_active is not None:
            query = query.filter(Vendor.is_active == is_active)
        
        return query.order_by(Vendor.name).offset(skip).limit(limit).all()
    
    def count(
        self,
        db: Session,
        tenant_id: int,
        branch_id: int = None,
        search: str = None,
        is_active: bool = None
    ) -> int:
        """Count vendors with filters"""
        query = db.query(func.count(Vendor.id)).filter(Vendor.tenant_id == tenant_id)
        
        if branch_id:
            query = query.filter(Vendor.branch_id == branch_id)
        
        if search:
            search_term = f"%{search}%"
            query = query.filter(
                or_(
                    Vendor.name.ilike(search_term),
                    Vendor.email.ilike(search_term)
                )
            )
        
        if is_active is not None:
            query = query.filter(Vendor.is_active == is_active)
        
        return query.scalar() or 0
    
    def create(
        self,
        db: Session,
        *,
        tenant_id: int,
        branch_id: int,
        name: str,
        email: str = None,
        phone: str = None,
        address: str = None,
        city: str = None,
        state: str = None,
        country: str = "Nigeria",
        credit_limit: float = None,
        payment_terms: int = None,
        tax_id: str = None,
        bank_name: str = None,
        bank_account_number: str = None
    ) -> Vendor:
        """Create new vendor"""
        vendor_number = self._generate_vendor_number(db, tenant_id)
        
        vendor = Vendor(
            tenant_id=tenant_id,
            branch_id=branch_id,
            vendor_number=vendor_number,
            name=name,
            email=email,
            phone=phone,
            address=address,
            city=city,
            state=state,
            country=country,
            credit_limit=credit_limit,
            payment_terms=payment_terms,
            tax_id=tax_id,
            bank_name=bank_name,
            bank_account_number=bank_account_number
        )
        db.add(vendor)
        db.commit()
        db.refresh(vendor)
        return vendor
    
    def _generate_vendor_number(self, db: Session, tenant_id: int) -> str:
        """Generate sequential vendor number"""
        year = datetime.now().year
        
        last_vendor = db.query(Vendor).filter(
            Vendor.tenant_id == tenant_id,
            Vendor.vendor_number.like(f"VEND-{year}-%")
        ).order_by(Vendor.vendor_number.desc()).first()
        
        if last_vendor:
            last_num = int(last_vendor.vendor_number.split('-')[-1])
            new_num = last_num + 1
        else:
            new_num = 1
        
        return f"VEND-{year}-{new_num:05d}"
    
    def update(
        self,
        db: Session,
        *,
        vendor: Vendor,
        **kwargs
    ) -> Vendor:
        """Update vendor"""
        for key, value in kwargs.items():
            if hasattr(vendor, key) and value is not None:
                setattr(vendor, key, value)
        db.commit()
        db.refresh(vendor)
        return vendor
    
    def delete(self, db: Session, vendor_id: int) -> bool:
        """Soft delete vendor"""
        vendor = self.get(db, vendor_id)
        if vendor:
            vendor.is_active = False
            db.commit()
            return True
        return False
    
    def get_balance(self, db: Session, vendor_id: int) -> float:
        """Get vendor's outstanding balance"""
        result = db.query(
            func.sum(PurchaseBill.total_amount - PurchaseBill.paid_amount)
        ).filter(
            PurchaseBill.vendor_id == vendor_id,
            PurchaseBill.status.in_(['unpaid', 'partially_paid'])
        ).scalar()
        
        return float(result or 0)


vendor = CRUDVendor()
