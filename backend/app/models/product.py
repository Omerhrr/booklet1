"""
Product and Inventory Models
"""

from sqlalchemy import Column, Integer, String, Boolean, DateTime, Float, ForeignKey, Text, UniqueConstraint
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from ..database import Base


class Category(Base):
    """Product categories"""
    __tablename__ = "categories"
    
    id = Column(Integer, primary_key=True, index=True)
    tenant_id = Column(Integer, ForeignKey("tenants.id"), nullable=False)
    
    name = Column(String(100), nullable=False)
    description = Column(Text, nullable=True)
    parent_id = Column(Integer, ForeignKey("categories.id"), nullable=True)
    
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    products = relationship("Product", back_populates="category")
    parent = relationship("Category", remote_side=[id], backref="subcategories")
    
    __table_args__ = (
        # UniqueConstraint('tenant_id', 'name', name='uq_category_name'),
        ()
    )


class Product(Base):
    """Product model"""
    __tablename__ = "products"
    
    id = Column(Integer, primary_key=True, index=True)
    tenant_id = Column(Integer, ForeignKey("tenants.id"), nullable=False)
    branch_id = Column(Integer, ForeignKey("branches.id"), nullable=False)
    
    category_id = Column(Integer, ForeignKey("categories.id"), nullable=True)
    
    product_number = Column(String(50), nullable=True)
    name = Column(String(255), nullable=False, index=True)
    sku = Column(String(100), nullable=True, unique=True)
    barcode = Column(String(100), nullable=True)
    description = Column(Text, nullable=True)
    
    unit = Column(String(20), default="pcs")  # pcs, kg, liters, etc.
    
    purchase_price = Column(Float, default=0)
    sales_price = Column(Float, default=0)
    
    # Inventory
    opening_stock = Column(Float, default=0)
    stock_quantity = Column(Float, default=0)
    reorder_point = Column(Float, nullable=True)
    max_stock = Column(Float, nullable=True)
    
    # Tracking
    track_inventory = Column(Boolean, default=True)
    is_inventory_item = Column(Boolean, default=True)
    
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    category = relationship("Category", back_populates="products")
    sales_invoice_items = relationship("SalesInvoiceItem", back_populates="product")
    purchase_bill_items = relationship("PurchaseBillItem", back_populates="product")
    stock_adjustments = relationship("StockAdjustment", back_populates="product")
    
    __table_args__ = (
        ()
    )


class StockAdjustment(Base):
    """Stock adjustment history"""
    __tablename__ = "stock_adjustments"
    
    id = Column(Integer, primary_key=True, index=True)
    tenant_id = Column(Integer, ForeignKey("tenants.id"), nullable=False)
    
    product_id = Column(Integer, ForeignKey("products.id"), nullable=False)
    
    quantity_change = Column(Float, nullable=False)  # Positive or negative
    previous_quantity = Column(Float, nullable=False)
    new_quantity = Column(Float, nullable=False)
    reason = Column(Text, nullable=True)
    
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    product = relationship("Product", back_populates="stock_adjustments")
    
    __table_args__ = (
        ()
    )
