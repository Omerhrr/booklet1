"""
Chart of Accounts and Ledger Models
Core accounting - Double-entry bookkeeping
"""

from sqlalchemy import Column, Integer, String, Boolean, DateTime, Float, ForeignKey, Text, Enum, BigInteger
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import enum

from ..database import Base


class AccountType(str, enum.Enum):
    ASSET = "asset"
    LIABILITY = "liability"
    EQUITY = "equity"
    REVENUE = "revenue"
    EXPENSE = "expense"


class Account(Base):
    """Chart of Accounts"""
    __tablename__ = "accounts"
    
    id = Column(Integer, primary_key=True, index=True)
    tenant_id = Column(Integer, ForeignKey("tenants.id"), nullable=False)
    branch_id = Column(Integer, ForeignKey("branches.id"), nullable=False)
    
    code = Column(String(20), nullable=False)  # Account code e.g., "1000"
    name = Column(String(255), nullable=False)
    type = Column(Enum(AccountType), nullable=False)
    description = Column(Text, nullable=True)
    
    # Hierarchy
    parent_id = Column(Integer, ForeignKey("accounts.id"), nullable=True)
    
    is_system_account = Column(Boolean, default=False)
    is_active = Column(Boolean, default=True)
    
    # Balance tracking
    opening_balance = Column(Float, default=0)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    parent = relationship("Account", remote_side=[id], backref="children")
    ledger_entries = relationship("LedgerEntry", back_populates="account")


class LedgerEntry(Base):
    """General Ledger Entry - Central transaction table"""
    __tablename__ = "ledger_entries"
    
    id = Column(BigInteger, primary_key=True, index=True)
    
    tenant_id = Column(Integer, ForeignKey("tenants.id"), nullable=False)
    branch_id = Column(Integer, ForeignKey("branches.id"), nullable=False)
    
    account_id = Column(Integer, ForeignKey("accounts.id"), nullable=False)
    
    transaction_date = Column(DateTime(timezone=True), nullable=False, index=True)
    description = Column(Text, nullable=True)
    reference = Column(String(100), nullable=True)
    
    debit = Column(Float, default=0)
    credit = Column(Float, default=0)
    running_balance = Column(Float, default=0)
    
    # Source document references
    journal_voucher_id = Column(Integer, ForeignKey("journal_vouchers.id"), nullable=True)
    sales_invoice_id = Column(Integer, ForeignKey("sales_invoices.id"), nullable=True)
    credit_note_id = Column(Integer, ForeignKey("credit_notes.id"), nullable=True)
    purchase_bill_id = Column(Integer, ForeignKey("purchase_bills.id"), nullable=True)
    debit_note_id = Column(Integer, ForeignKey("debit_notes.id"), nullable=True)
    expense_id = Column(Integer, ForeignKey("expenses.id"), nullable=True)
    other_income_id = Column(Integer, ForeignKey("other_incomes.id"), nullable=True)
    payslip_id = Column(Integer, ForeignKey("payslips.id"), nullable=True)
    fund_transfer_id = Column(Integer, ForeignKey("fund_transfers.id"), nullable=True)
    bank_reconciliation_id = Column(Integer, ForeignKey("bank_reconciliations.id"), nullable=True)
    
    # Reconciliation
    is_reconciled = Column(Boolean, default=False)
    reconciled_at = Column(DateTime(timezone=True), nullable=True)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    account = relationship("Account", back_populates="ledger_entries")
    journal_voucher = relationship("JournalVoucher", back_populates="ledger_entries")


class JournalVoucher(Base):
    """Journal Voucher for manual entries"""
    __tablename__ = "journal_vouchers"
    
    id = Column(Integer, primary_key=True, index=True)
    tenant_id = Column(Integer, ForeignKey("tenants.id"), nullable=False)
    branch_id = Column(Integer, ForeignKey("branches.id"), nullable=False)
    
    voucher_number = Column(String(50), nullable=False)
    transaction_date = Column(DateTime(timezone=True), nullable=False)
    description = Column(Text, nullable=True)
    reference = Column(String(100), nullable=True)
    
    is_posted = Column(Boolean, default=False)
    posted_at = Column(DateTime(timezone=True), nullable=True)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    ledger_entries = relationship("LedgerEntry", back_populates="journal_voucher")
