"""
Expense and Other Income Models
"""

from sqlalchemy import Column, Integer, String, Boolean, DateTime, Float, ForeignKey, Text, UniqueConstraint
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from ..database import Base


class Expense(Base):
    """Expense tracking"""
    __tablename__ = "expenses"
    
    id = Column(Integer, primary_key=True, index=True)
    tenant_id = Column(Integer, ForeignKey("tenants.id"), nullable=False)
    branch_id = Column(Integer, ForeignKey("branches.id"), nullable=False)
    
    expense_number = Column(String(50), nullable=False)
    expense_date = Column(DateTime(timezone=True), nullable=False)
    
    vendor_id = Column(Integer, ForeignKey("vendors.id"), nullable=True)
    
    category = Column(String(100), nullable=False)  # Rent, Utilities, Travel, etc.
    description = Column(Text, nullable=True)
    
    subtotal = Column(Float, default=0)
    vat_amount = Column(Float, default=0)
    total_amount = Column(Float, default=0)
    
    expense_account_id = Column(Integer, ForeignKey("accounts.id"), nullable=False)
    paid_from_account_id = Column(Integer, ForeignKey("accounts.id"), nullable=False)
    
    is_posted = Column(Boolean, default=False)
    posted_at = Column(DateTime(timezone=True), nullable=True)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    vendor = relationship("Vendor", back_populates="expenses")
    expense_account = relationship("Account", foreign_keys=[expense_account_id])
    paid_from_account = relationship("Account", foreign_keys=[paid_from_account_id])
    
    __table_args__ = (
        # UniqueConstraint('tenant_id', 'expense_number', name='uq_expense_number'),
        ()
    )


class OtherIncome(Base):
    """Other income tracking"""
    __tablename__ = "other_incomes"
    
    id = Column(Integer, primary_key=True, index=True)
    tenant_id = Column(Integer, ForeignKey("tenants.id"), nullable=False)
    branch_id = Column(Integer, ForeignKey("branches.id"), nullable=False)
    
    income_number = Column(String(50), unique=True, nullable=False)
    income_date = Column(DateTime(timezone=True), nullable=False)
    
    description = Column(Text, nullable=True)
    amount = Column(Float, default=0)
    
    income_account_id = Column(Integer, ForeignKey("accounts.id"), nullable=False)  # Revenue account
    deposited_to_account_id = Column(Integer, ForeignKey("accounts.id"), nullable=False)  # Asset account
    
    is_posted = Column(Boolean, default=False)
    posted_at = Column(DateTime(timezone=True), nullable=True)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    income_account = relationship("Account", foreign_keys=[income_account_id])
    deposited_to_account = relationship("Account", foreign_keys=[deposited_to_account_id])
    
    __table_args__ = (
        ()
    )
