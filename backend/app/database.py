"""
Database Configuration with Multi-Tenancy Support
Schema-based isolation for tenant data
"""

from sqlalchemy import create_engine, Column, Integer, String, Boolean, DateTime, Float, Text, ForeignKey, Enum, JSON, BigInteger, UniqueConstraint, event
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session, relationship
from sqlalchemy.sql import func
from contextlib import contextmanager, asynccontextmanager
from typing import Generator, Optional, AsyncGenerator
import os
import logging

logger = logging.getLogger(__name__)

# Database URL from environment
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./booklet.db")

# For PostgreSQL with async support
if DATABASE_URL.startswith("postgresql"):
    # Synchronous engine for most operations
    engine = create_engine(
        DATABASE_URL,
        pool_size=int(os.getenv("DATABASE_POOL_SIZE", 10)),
        max_overflow=int(os.getenv("DATABASE_MAX_OVERFLOW", 20)),
        pool_pre_ping=True,
        echo=os.getenv("DEBUG") == "true"
    )
else:
    # SQLite for development
    engine = create_engine(
        DATABASE_URL,
        connect_args={"check_same_thread": False},
        echo=os.getenv("DEBUG") == "true"
    )

# Session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base class for models
Base = declarative_base()


# ============================================
# MULTI-TENANCY SUPPORT
# ============================================

def get_tenant_schema_name(tenant_id: int) -> str:
    """Generate schema name for tenant"""
    return f"tenant_{tenant_id}"


def create_tenant_schema(tenant_id: int, db: Session):
    """Create isolated schema for new tenant"""
    schema_name = get_tenant_schema_name(tenant_id)
    db.execute(f"CREATE SCHEMA IF NOT EXISTS {schema_name}")
    db.commit()
    logger.info(f"Created schema: {schema_name}")


def set_tenant_schema(tenant_id: int, db: Session):
    """Set search_path to tenant schema"""
    schema_name = get_tenant_schema_name(tenant_id)
    db.execute(f"SET search_path TO {schema_name}, public")


# ============================================
# SESSION MANAGEMENT
# ============================================

def get_db() -> Generator[Session, None, None]:
    """Dependency to get database session"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@contextmanager
def get_db_context() -> Generator[Session, None, None]:
    """Context manager for database session"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


async def init_db():
    """Initialize database - create all tables"""
    from .models import tenant, user, permission, account, branch, customer, vendor, product, sales, purchase, expense, hr, fixed_assets, budget, banking, audit
    
    # Create public schema tables
    Base.metadata.create_all(bind=engine)
    logger.info("Database tables created")
    
    # Seed default data
    await seed_default_data()


async def seed_default_data():
    """Seed default permissions and subscription plans"""
    from .models.permission import Permission
    from .models.tenant import SubscriptionPlan
    from . import crud

    db = SessionLocal()
    try:
        # Check if permissions exist
        existing_permissions = db.query(Permission).first()
        if not existing_permissions:
            # Create default permissions
            permissions_data = crud.DEFAULT_PERMISSIONS
            for perm in permissions_data:
                permission = Permission(**perm)
                db.add(permission)
            db.commit()
            logger.info("Default permissions seeded")

        # Check if subscription plans exist
        existing_plans = db.query(SubscriptionPlan).first()
        if not existing_plans:
            # Create default subscription plans
            plans_data = crud.DEFAULT_PLANS
            for plan in plans_data:
                subscription_plan = SubscriptionPlan(**plan)
                db.add(subscription_plan)
            db.commit()
            logger.info("Default subscription plans seeded")
    finally:
        db.close()


# ============================================
# TENANT-AWARE SESSION
# ============================================

class TenantSession:
    """Session that automatically sets tenant context"""
    
    def __init__(self, db: Session, tenant_id: int):
        self.db = db
        self.tenant_id = tenant_id
    
    def __enter__(self):
        set_tenant_schema(self.tenant_id, self.db)
        return self.db
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.db.execute("SET search_path TO public")
        if exc_type:
            self.db.rollback()
        return False


def get_tenant_db(tenant_id: int) -> Generator[Session, None, None]:
    """Get database session with tenant schema set"""
    db = SessionLocal()
    try:
        set_tenant_schema(tenant_id, db)
        yield db
    finally:
        db.execute("SET search_path TO public")
        db.close()
