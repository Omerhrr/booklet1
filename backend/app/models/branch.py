"""
Branch and UserBranchRole Models
"""

from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, Text, UniqueConstraint
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from ..database import Base


class Branch(Base):
    """Branch model for multi-branch support"""
    __tablename__ = "branches"
    __table_args__ = (
        UniqueConstraint('tenant_id', 'name', name='uq_branch_tenant_name'),
    )
    
    id = Column(Integer, primary_key=True, index=True)
    tenant_id = Column(Integer, ForeignKey("tenants.id"), nullable=False)
    
    name = Column(String(100), nullable=False)
    code = Column(String(20), nullable=True)
    address = Column(Text, nullable=True)
    city = Column(String(100), nullable=True)
    state = Column(String(100), nullable=True)
    country = Column(String(100), default="Nigeria")
    phone = Column(String(20), nullable=True)
    email = Column(String(255), nullable=True)
    
    # Default currency is Nigerian Naira
    currency = Column(String(3), default="NGN")
    is_default = Column(Boolean, default=False)
    is_active = Column(Boolean, default=True)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    tenant = relationship("Tenant", back_populates="branches")
    user_branch_roles = relationship("UserBranchRole", back_populates="branch", cascade="all, delete-orphan")


class UserBranchRole(Base):
    """User-Branch-Role junction table for scoped permissions"""
    __tablename__ = "user_branch_roles"
    __table_args__ = (
        UniqueConstraint('user_id', 'branch_id', 'role_id', name='uq_user_branch_role'),
    )
    
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), primary_key=True)
    branch_id = Column(Integer, ForeignKey("branches.id", ondelete="CASCADE"), primary_key=True)
    role_id = Column(Integer, ForeignKey("roles.id", ondelete="CASCADE"), primary_key=True)
    
    assigned_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    user = relationship("User", back_populates="branch_roles")
    branch = relationship("Branch", back_populates="user_branch_roles")
    role = relationship("Role", back_populates="user_branch_roles")
