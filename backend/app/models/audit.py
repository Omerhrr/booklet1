"""
Audit Log Model
"""

from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, Text, JSON, BigInteger
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from ..database import Base


class AuditLog(Base):
    """Comprehensive audit trail"""
    __tablename__ = "audit_logs"
    
    
    id = Column(BigInteger, primary_key=True, index=True)
    timestamp = Column(DateTime(timezone=True), server_default=func.now(), index=True)
    
    # Who
    tenant_id = Column(Integer, ForeignKey("tenants.id"), index=True, nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), index=True, nullable=True)
    user_email = Column(String(255), nullable=True)
    user_role = Column(String(100), nullable=True)
    
    # What
    action = Column(String(100), index=True, nullable=False)  # login, create, update, delete, export
    resource_type = Column(String(100), nullable=True)  # Customer, Invoice, etc.
    resource_id = Column(Integer, index=True, nullable=True)
    
    # Where
    ip_address = Column(String(45), nullable=True)  # IPv6 compatible
    user_agent = Column(String(500), nullable=True)
    geo_location = Column(JSON, nullable=True)  # {country, city, lat, lon}
    
    # Details
    changes = Column(JSON, nullable=True)  # Before/after values
    request_id = Column(String(100), nullable=True)
    status = Column(String(50), nullable=False)  # success, failure
    
    # Metadata
    tags = Column(JSON, nullable=True)
    
    # Relationships
    user = relationship("User", back_populates="audit_logs")
