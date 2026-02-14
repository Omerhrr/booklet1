"""
Permission and Role Models for RBAC
"""

from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from ..database import Base


class Permission(Base):
    """Granular permissions"""
    __tablename__ = "permissions"
    
    
    id = Column(Integer, primary_key=True)
    name = Column(String(100), unique=True, nullable=False)  # e.g., "sales:create"
    display_name = Column(String(255), nullable=False)
    category = Column(String(50), nullable=False)  # Sales, Accounting, HR, etc.
    description = Column(Text, nullable=True)
    
    # Relationships
    roles = relationship("RolePermission", back_populates="permission")


class Role(Base):
    """Roles aggregate permissions"""
    __tablename__ = "roles"
    
    
    id = Column(Integer, primary_key=True, index=True)
    tenant_id = Column(Integer, ForeignKey("tenants.id"), nullable=False)
    
    name = Column(String(100), nullable=False)
    description = Column(Text, nullable=True)
    is_system = Column(Boolean, default=False)  # System roles cannot be deleted
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    tenant = relationship("Tenant", back_populates="roles")
    users = relationship("User", back_populates="role")
    permissions = relationship("RolePermission", back_populates="role", cascade="all, delete-orphan")
    user_branch_roles = relationship("UserBranchRole", back_populates="role", cascade="all, delete-orphan")


class RolePermission(Base):
    """Role-Permission junction table"""
    __tablename__ = "role_permissions"
    
    
    role_id = Column(Integer, ForeignKey("roles.id", ondelete="CASCADE"), primary_key=True)
    permission_id = Column(Integer, ForeignKey("permissions.id", ondelete="CASCADE"), primary_key=True)
    
    # Relationships
    role = relationship("Role", back_populates="permissions")
    permission = relationship("Permission", back_populates="roles")
