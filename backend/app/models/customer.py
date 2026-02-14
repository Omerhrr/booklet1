"""
Customer Model (CRM)
"""

from sqlalchemy import Column, Integer, String, Boolean, DateTime, Float, ForeignKey, Text, UniqueConstraint
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from ..database import Base


class Customer(Base):
    """Customer model"""
    __tablename__ = "customers"
    
    id = Column(Integer, primary_key=True, index=True)
    tenant_id = Column(Integer, ForeignKey("tenants.id"), nullable=False)
    branch_id = Column(Integer, ForeignKey("branches.id"), nullable=False)
    
    customer_number = Column(String(50), nullable=True)  # Auto-generated
    name = Column(String(255), nullable=False, index=True)
    email = Column(String(255), nullable=True)
    phone = Column(String(50), nullable=True)
    
    address = Column(Text, nullable=True)
    city = Column(String(100), nullable=True)
    state = Column(String(100), nullable=True)
    country = Column(String(100), default="Nigeria")
    
    # Financial
    credit_limit = Column(Float, nullable=True)
    payment_terms = Column(Integer, nullable=True)  # Days
    tax_id = Column(String(50), nullable=True)  # VAT/TIN number
    
    # Status
    is_active = Column(Boolean, default=True)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    sales_invoices = relationship("SalesInvoice", back_populates="customer")
    credit_notes = relationship("CreditNote", back_populates="customer")
    
    __table_args__ = (
        # UniqueConstraint('tenant_id', 'customer_number', name='uq_customer_number'),
        ()
    )
    
    @property
    def balance(self) -> float:
        """Calculate customer balance from invoices"""
        # This will be computed in queries
        return 0.0
