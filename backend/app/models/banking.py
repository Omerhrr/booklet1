"""
Banking Models - Bank Accounts, Transfers, Reconciliation
"""

from sqlalchemy import Column, Integer, String, Boolean, DateTime, Float, ForeignKey, Text, UniqueConstraint
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from ..database import Base


class BankAccount(Base):
    """Bank account linked to chart of accounts"""
    __tablename__ = "bank_accounts"
    
    id = Column(Integer, primary_key=True, index=True)
    tenant_id = Column(Integer, ForeignKey("tenants.id"), nullable=False)
    branch_id = Column(Integer, ForeignKey("branches.id"), nullable=False)
    
    account_name = Column(String(100), nullable=False)
    bank_name = Column(String(100), nullable=True)
    account_number = Column(String(50), nullable=True)
    currency = Column(String(3), default="NGN")
    
    chart_of_account_id = Column(Integer, ForeignKey("accounts.id"), unique=True, nullable=False)
    
    last_reconciliation_date = Column(DateTime(timezone=True), nullable=True)
    last_reconciliation_balance = Column(Float, nullable=True)
    
    is_active = Column(Boolean, default=True)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    chart_of_account = relationship("Account")


class FundTransfer(Base):
    """Fund transfer between accounts"""
    __tablename__ = "fund_transfers"
    
    id = Column(Integer, primary_key=True, index=True)
    tenant_id = Column(Integer, ForeignKey("tenants.id"), nullable=False)
    branch_id = Column(Integer, ForeignKey("branches.id"), nullable=False)
    
    transfer_date = Column(DateTime(timezone=True), nullable=False)
    description = Column(Text, nullable=True)
    
    amount = Column(Float, default=0)
    
    from_account_id = Column(Integer, ForeignKey("accounts.id"), nullable=False)
    to_account_id = Column(Integer, ForeignKey("accounts.id"), nullable=False)
    
    is_posted = Column(Boolean, default=False)
    posted_at = Column(DateTime(timezone=True), nullable=True)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    from_account = relationship("Account", foreign_keys=[from_account_id])
    to_account = relationship("Account", foreign_keys=[to_account_id])


class BankReconciliation(Base):
    """Bank reconciliation record"""
    __tablename__ = "bank_reconciliations"
    
    id = Column(Integer, primary_key=True, index=True)
    tenant_id = Column(Integer, ForeignKey("tenants.id"), nullable=False)
    branch_id = Column(Integer, ForeignKey("branches.id"), nullable=False)
    
    account_id = Column(Integer, ForeignKey("accounts.id"), nullable=False)
    statement_date = Column(DateTime(timezone=True), nullable=False)
    statement_balance = Column(Float, default=0)
    
    reconciled_at = Column(DateTime(timezone=True), nullable=False)

    created_at = Column(DateTime(timezone=True), server_default=func.now())

