"""
Vendor Model (Supplier Management)
"""

from sqlalchemy import Column, Integer, String, Boolean, DateTime, Float, ForeignKey, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from ..database import Base


class Vendor(Base):
    """Vendor/Supplier model"""
    __tablename__ = "vendors"
    
    id = Column(Integer, primary_key=True, index=True)
    tenant_id = Column(Integer, ForeignKey("tenants.id"), nullable=False)
    branch_id = Column(Integer, ForeignKey("branches.id"), nullable=False)
    
    vendor_number = Column(String(50), nullable=True)
    name = Column(String(255), nullable=False, index=True)
    email = Column(String(255), nullable=True)
    phone = Column(String(50), nullable=True)
    
    address = Column(Text, nullable=True)
    city = Column(String(100), nullable=True)
    state = Column(String(100), nullable=True)
    country = Column(String(100), default="Nigeria")
    
    # Financial
    credit_limit = Column(Float, nullable=True)
    payment_terms = Column(Integer, nullable=True)
    tax_id = Column(String(50), nullable=True)
    bank_name = Column(String(100), nullable=True)
    bank_account_number = Column(String(50), nullable=True)
    
    is_active = Column(Boolean, default=True)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    purchase_bills = relationship("PurchaseBill", back_populates="vendor")
    debit_notes = relationship("DebitNote", back_populates="vendor")
    expenses = relationship("Expense", back_populates="vendor")
    
    __table_args__ = (
        ()
    )
