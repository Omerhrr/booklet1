"""
Fixed Assets and Depreciation Models
"""

from sqlalchemy import Column, Integer, String, Boolean, DateTime, Float, ForeignKey, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from ..database import Base


class FixedAsset(Base):
    """Fixed asset with depreciation tracking"""
    __tablename__ = "fixed_assets"
    
    id = Column(Integer, primary_key=True, index=True)
    tenant_id = Column(Integer, ForeignKey("tenants.id"), nullable=False)
    branch_id = Column(Integer, ForeignKey("branches.id"), nullable=False)
    
    asset_number = Column(String(50), nullable=True)
    name = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    
    purchase_date = Column(DateTime(timezone=True), nullable=False)
    purchase_cost = Column(Float, default=0)
    salvage_value = Column(Float, default=0)
    
    depreciation_method = Column(String(50), default="straight_line")
    useful_life_years = Column(Integer, default=5)
    
    asset_account_id = Column(Integer, ForeignKey("accounts.id"), nullable=False)
    accumulated_depreciation_account_id = Column(Integer, ForeignKey("accounts.id"), nullable=False)
    
    accumulated_depreciation = Column(Float, default=0)
    net_book_value = Column(Float, default=0)
    
    is_active = Column(Boolean, default=True)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    asset_account = relationship("Account", foreign_keys=[asset_account_id])
    accumulated_depreciation_account = relationship("Account", foreign_keys=[accumulated_depreciation_account_id])
    depreciation_entries = relationship("DepreciationEntry", back_populates="asset", cascade="all, delete-orphan")
    
    __table_args__ = (
        ()
    )


class DepreciationEntry(Base):
    """Depreciation entry history"""
    __tablename__ = "depreciation_entries"
    
    id = Column(Integer, primary_key=True, index=True)
    asset_id = Column(Integer, ForeignKey("fixed_assets.id"), nullable=False)
    
    entry_date = Column(DateTime(timezone=True), nullable=False)
    amount = Column(Float, default=0)
    accumulated_amount = Column(Float, default=0)
    
    journal_voucher_id = Column(Integer, ForeignKey("journal_vouchers.id"), nullable=True)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    asset = relationship("FixedAsset", back_populates="depreciation_entries")
    
    __table_args__ = (
        ()
    )
