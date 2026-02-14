"""
Budget Models
"""

from sqlalchemy import Column, Integer, String, Boolean, DateTime, Float, ForeignKey, Text, UniqueConstraint
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from ..database import Base


class Budget(Base):
    """Budget definition"""
    __tablename__ = "budgets"
    
    id = Column(Integer, primary_key=True, index=True)
    tenant_id = Column(Integer, ForeignKey("tenants.id"), nullable=False)
    branch_id = Column(Integer, ForeignKey("branches.id"), nullable=False)
    
    name = Column(String(100), nullable=False)
    description = Column(Text, nullable=True)
    
    start_date = Column(DateTime(timezone=True), nullable=False)
    end_date = Column(DateTime(timezone=True), nullable=False)
    
    is_active = Column(Boolean, default=True)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    budget_lines = relationship("BudgetLine", back_populates="budget", cascade="all, delete-orphan")
    
    __table_args__ = (
        # UniqueConstraint('branch_id', 'name', name='uq_budget_name'),
        ()
    )


class BudgetLine(Base):
    """Budget line item per account"""
    __tablename__ = "budget_lines"
    
    id = Column(Integer, primary_key=True, index=True)
    budget_id = Column(Integer, ForeignKey("budgets.id", ondelete="CASCADE"), nullable=False)
    
    account_id = Column(Integer, ForeignKey("accounts.id"), nullable=False)
    
    budget_amount = Column(Float, default=0)
    actual_amount = Column(Float, default=0)
    variance = Column(Float, default=0)
    
    # Relationships
    budget = relationship("Budget", back_populates="budget_lines")
    account = relationship("Account")
    
    __table_args__ = (
        # UniqueConstraint('budget_id', 'account_id', name='uq_budget_line_account'),
        ()
    )
