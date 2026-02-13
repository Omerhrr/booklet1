"""
Customer CRUD Operations
"""

from typing import Optional, List
from sqlalchemy.orm import Session
from sqlalchemy import or_, func
from datetime import datetime
import uuid

from ..models.customer import Customer
from ..models.sales import SalesInvoice


class CRUDCustomer:
    
    def get(self, db: Session, customer_id: int) -> Optional[Customer]:
        """Get customer by ID"""
        return db.query(Customer).filter(Customer.id == customer_id).first()
    
    def get_multi(
        self,
        db: Session,
        tenant_id: int,
        branch_id: int = None,
        skip: int = 0,
        limit: int = 50,
        search: str = None,
        is_active: bool = None
    ) -> List[Customer]:
        """Get multiple customers with filters"""
        query = db.query(Customer).filter(Customer.tenant_id == tenant_id)
        
        if branch_id:
            query = query.filter(Customer.branch_id == branch_id)
        
        if search:
            search_term = f"%{search}%"
            query = query.filter(
                or_(
                    Customer.name.ilike(search_term),
                    Customer.email.ilike(search_term),
                    Customer.phone.ilike(search_term)
                )
            )
        
        if is_active is not None:
            query = query.filter(Customer.is_active == is_active)
        
        return query.order_by(Customer.name).offset(skip).limit(limit).all()
    
    def count(
        self,
        db: Session,
        tenant_id: int,
        branch_id: int = None,
        search: str = None,
        is_active: bool = None
    ) -> int:
        """Count customers with filters"""
        query = db.query(func.count(Customer.id)).filter(Customer.tenant_id == tenant_id)
        
        if branch_id:
            query = query.filter(Customer.branch_id == branch_id)
        
        if search:
            search_term = f"%{search}%"
            query = query.filter(
                or_(
                    Customer.name.ilike(search_term),
                    Customer.email.ilike(search_term)
                )
            )
        
        if is_active is not None:
            query = query.filter(Customer.is_active == is_active)
        
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
        tax_id: str = None
    ) -> Customer:
        """Create new customer"""
        # Generate customer number
        customer_number = self._generate_customer_number(db, tenant_id)
        
        customer = Customer(
            tenant_id=tenant_id,
            branch_id=branch_id,
            customer_number=customer_number,
            name=name,
            email=email,
            phone=phone,
            address=address,
            city=city,
            state=state,
            country=country,
            credit_limit=credit_limit,
            payment_terms=payment_terms,
            tax_id=tax_id
        )
        db.add(customer)
        db.commit()
        db.refresh(customer)
        return customer
    
    def _generate_customer_number(self, db: Session, tenant_id: int) -> str:
        """Generate sequential customer number"""
        year = datetime.now().year
        
        last_customer = db.query(Customer).filter(
            Customer.tenant_id == tenant_id,
            Customer.customer_number.like(f"CUST-{year}-%")
        ).order_by(Customer.customer_number.desc()).first()
        
        if last_customer:
            last_num = int(last_customer.customer_number.split('-')[-1])
            new_num = last_num + 1
        else:
            new_num = 1
        
        return f"CUST-{year}-{new_num:05d}"
    
    def update(
        self,
        db: Session,
        *,
        customer: Customer,
        **kwargs
    ) -> Customer:
        """Update customer"""
        for key, value in kwargs.items():
            if hasattr(customer, key) and value is not None:
                setattr(customer, key, value)
        db.commit()
        db.refresh(customer)
        return customer
    
    def delete(self, db: Session, customer_id: int) -> bool:
        """Soft delete customer (set is_active = False)"""
        customer = self.get(db, customer_id)
        if customer:
            customer.is_active = False
            db.commit()
            return True
        return False
    
    def get_balance(self, db: Session, customer_id: int) -> float:
        """Get customer's outstanding balance"""
        result = db.query(
            func.sum(SalesInvoice.total_amount - SalesInvoice.paid_amount)
        ).filter(
            SalesInvoice.customer_id == customer_id,
            SalesInvoice.status.in_(['unpaid', 'partially_paid'])
        ).scalar()
        
        return float(result or 0)
    
    def get_sales_history(
        self,
        db: Session,
        customer_id: int,
        limit: int = 10
    ) -> List[SalesInvoice]:
        """Get customer's sales history"""
        return db.query(SalesInvoice).filter(
            SalesInvoice.customer_id == customer_id
        ).order_by(SalesInvoice.invoice_date.desc()).limit(limit).all()


customer = CRUDCustomer()
