"""
Purchase Models - Bills and Debit Notes
"""

from sqlalchemy import Column, Integer, String, Boolean, DateTime, Float, ForeignKey, Text, Enum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from ..database import Base
from .sales import InvoicePaymentStatus  # Reuse the same enum


class PurchaseBill(Base):
    """Purchase Bill"""
    __tablename__ = "purchase_bills"
    
    id = Column(Integer, primary_key=True, index=True)
    tenant_id = Column(Integer, ForeignKey("tenants.id"), nullable=False)
    branch_id = Column(Integer, ForeignKey("branches.id"), nullable=False)
    
    vendor_id = Column(Integer, ForeignKey("vendors.id"), nullable=False)
    
    bill_number = Column(String(50), nullable=False)
    bill_date = Column(DateTime(timezone=True), nullable=False)
    due_date = Column(DateTime(timezone=True), nullable=True)
    
    subtotal = Column(Float, default=0)
    vat_amount = Column(Float, default=0)
    total_amount = Column(Float, default=0)
    
    paid_amount = Column(Float, default=0)
    status = Column(Enum(InvoicePaymentStatus), default=InvoicePaymentStatus.UNPAID)
    
    notes = Column(Text, nullable=True)
    
    is_posted = Column(Boolean, default=False)
    posted_at = Column(DateTime(timezone=True), nullable=True)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    vendor = relationship("Vendor", back_populates="purchase_bills")
    items = relationship("PurchaseBillItem", back_populates="purchase_bill", cascade="all, delete-orphan")
    
    __table_args__ = (
        ()
    )


class PurchaseBillItem(Base):
    """Purchase Bill Line Item"""
    __tablename__ = "purchase_bill_items"
    
    id = Column(Integer, primary_key=True, index=True)
    purchase_bill_id = Column(Integer, ForeignKey("purchase_bills.id", ondelete="CASCADE"), nullable=False)
    
    product_id = Column(Integer, ForeignKey("products.id"), nullable=True)
    
    description = Column(String(255), nullable=False)
    quantity = Column(Float, default=0)
    unit_price = Column(Float, default=0)
    vat_percent = Column(Float, default=0)
    line_total = Column(Float, default=0)
    
    returned_quantity = Column(Float, default=0)
    
    # Relationships
    purchase_bill = relationship("PurchaseBill", back_populates="items")
    product = relationship("Product", back_populates="purchase_bill_items")
    
    __table_args__ = (
        ()
    )


class DebitNote(Base):
    """Debit Note for returns/cancellations"""
    __tablename__ = "debit_notes"
    
    id = Column(Integer, primary_key=True, index=True)
    tenant_id = Column(Integer, ForeignKey("tenants.id"), nullable=False)
    branch_id = Column(Integer, ForeignKey("branches.id"), nullable=False)
    
    vendor_id = Column(Integer, ForeignKey("vendors.id"), nullable=False)
    purchase_bill_id = Column(Integer, ForeignKey("purchase_bills.id"), nullable=True)
    
    debit_note_number = Column(String(50), nullable=False)
    debit_note_date = Column(DateTime(timezone=True), nullable=False)
    total_amount = Column(Float, default=0)
    
    reason = Column(Text, nullable=True)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    vendor = relationship("Vendor", back_populates="debit_notes")
    items = relationship("DebitNoteItem", back_populates="debit_note", cascade="all, delete-orphan")
    
    __table_args__ = (
        ()
    )


class DebitNoteItem(Base):
    """Debit Note Line Item"""
    __tablename__ = "debit_note_items"
    
    id = Column(Integer, primary_key=True, index=True)
    debit_note_id = Column(Integer, ForeignKey("debit_notes.id", ondelete="CASCADE"), nullable=False)
    
    product_id = Column(Integer, ForeignKey("products.id"), nullable=True)
    
    description = Column(String(255), nullable=False)
    quantity = Column(Float, default=0)
    unit_price = Column(Float, default=0)
    line_total = Column(Float, default=0)
    
    # Relationships
    debit_note = relationship("DebitNote", back_populates="items")
    
    __table_args__ = (
        ()
    )
