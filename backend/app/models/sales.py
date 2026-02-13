"""
Sales Models - Invoices and Credit Notes
"""

from sqlalchemy import Column, Integer, String, Boolean, DateTime, Float, ForeignKey, Text, Enum, UniqueConstraint
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import enum

from ..database import Base


class InvoicePaymentStatus(str, enum.Enum):
    UNPAID = "unpaid"
    PARTIALLY_PAID = "partially_paid"
    PAID = "paid"
    WRITTEN_OFF = "written_off"


class SalesInvoice(Base):
    """Sales Invoice"""
    __tablename__ = "sales_invoices"
    
    id = Column(Integer, primary_key=True, index=True)
    tenant_id = Column(Integer, ForeignKey("tenants.id"), nullable=False)
    branch_id = Column(Integer, ForeignKey("branches.id"), nullable=False)
    
    customer_id = Column(Integer, ForeignKey("customers.id"), nullable=False)
    
    invoice_number = Column(String(50), nullable=False)
    invoice_date = Column(DateTime(timezone=True), nullable=False)
    due_date = Column(DateTime(timezone=True), nullable=True)
    
    subtotal = Column(Float, default=0)
    discount_amount = Column(Float, default=0)
    vat_amount = Column(Float, default=0)
    total_amount = Column(Float, default=0)
    
    paid_amount = Column(Float, default=0)
    status = Column(Enum(InvoicePaymentStatus), default=InvoicePaymentStatus.UNPAID)
    
    notes = Column(Text, nullable=True)
    terms = Column(Text, nullable=True)
    
    is_posted = Column(Boolean, default=False)
    posted_at = Column(DateTime(timezone=True), nullable=True)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    customer = relationship("Customer", back_populates="sales_invoices")
    items = relationship("SalesInvoiceItem", back_populates="sales_invoice", cascade="all, delete-orphan")
    
    __table_args__ = (
        # UniqueConstraint('tenant_id', 'invoice_number', name='uq_sales_invoice_number'),
        ()
    )


class SalesInvoiceItem(Base):
    """Sales Invoice Line Item"""
    __tablename__ = "sales_invoice_items"
    
    id = Column(Integer, primary_key=True, index=True)
    sales_invoice_id = Column(Integer, ForeignKey("sales_invoices.id", ondelete="CASCADE"), nullable=False)
    
    product_id = Column(Integer, ForeignKey("products.id"), nullable=True)
    
    description = Column(String(255), nullable=False)
    quantity = Column(Float, default=0)
    unit_price = Column(Float, default=0)
    discount_percent = Column(Float, default=0)
    vat_percent = Column(Float, default=0)
    line_total = Column(Float, default=0)
    
    returned_quantity = Column(Float, default=0)
    
    # Relationships
    sales_invoice = relationship("SalesInvoice", back_populates="items")
    product = relationship("Product", back_populates="sales_invoice_items")
    
    __table_args__ = (
        ()
    )


class CreditNote(Base):
    """Credit Note for returns/cancellations"""
    __tablename__ = "credit_notes"
    
    id = Column(Integer, primary_key=True, index=True)
    tenant_id = Column(Integer, ForeignKey("tenants.id"), nullable=False)
    branch_id = Column(Integer, ForeignKey("branches.id"), nullable=False)
    
    customer_id = Column(Integer, ForeignKey("customers.id"), nullable=False)
    sales_invoice_id = Column(Integer, ForeignKey("sales_invoices.id"), nullable=True)
    
    credit_note_number = Column(String(50), nullable=False)
    credit_note_date = Column(DateTime(timezone=True), nullable=False)
    total_amount = Column(Float, default=0)
    
    reason = Column(Text, nullable=True)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    customer = relationship("Customer", back_populates="credit_notes")
    items = relationship("CreditNoteItem", back_populates="credit_note", cascade="all, delete-orphan")
    
    __table_args__ = (
        # UniqueConstraint('tenant_id', 'credit_note_number', name='uq_credit_note_number'),
        ()
    )


class CreditNoteItem(Base):
    """Credit Note Line Item"""
    __tablename__ = "credit_note_items"
    
    id = Column(Integer, primary_key=True, index=True)
    credit_note_id = Column(Integer, ForeignKey("credit_notes.id", ondelete="CASCADE"), nullable=False)
    
    product_id = Column(Integer, ForeignKey("products.id"), nullable=True)
    
    description = Column(String(255), nullable=False)
    quantity = Column(Float, default=0)
    unit_price = Column(Float, default=0)
    line_total = Column(Float, default=0)
    
    # Relationships
    credit_note = relationship("CreditNote", back_populates="items")
    
    __table_args__ = (
        ()
    )
