"""
Pytest Configuration and Fixtures
"""

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from ..database import Base
from ..models.tenant import Tenant, SubscriptionPlan
from ..models.user import User
from ..models.role import Role, Permission, RolePermission
from ..models.branch import Branch, UserBranchRole
from ..security import hash_password


# Test database URL (in-memory SQLite)
SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"


@pytest.fixture(scope="function")
def db():
    """Create a fresh database for each test"""
    engine = create_engine(
        SQLALCHEMY_DATABASE_URL,
        connect_args={"check_same_thread": False},
        poolclass=StaticPool
    )
    
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    
    # Create tables
    Base.metadata.create_all(bind=engine)
    
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


@pytest.fixture(scope="function")
def tenant(db):
    """Create a test tenant"""
    tenant = Tenant(
        business_name="Test Company",
        subdomain="testcompany",
        base_currency="NGN",
        is_vat_registered=True,
        vat_rate=7.5
    )
    db.add(tenant)
    db.commit()
    db.refresh(tenant)
    return tenant


@pytest.fixture(scope="function")
def branch(db, tenant):
    """Create a test branch"""
    branch = Branch(
        tenant_id=tenant.id,
        name="Main Branch",
        is_default=True,
        currency="NGN"
    )
    db.add(branch)
    db.commit()
    db.refresh(branch)
    return branch


@pytest.fixture(scope="function")
def permissions(db):
    """Seed test permissions"""
    perms = [
        Permission(name="sales:view", display_name="View Sales", category="Sales"),
        Permission(name="sales:create", display_name="Create Sales", category="Sales"),
        Permission(name="customers:view", display_name="View Customers", category="Customers"),
    ]
    for perm in perms:
        db.add(perm)
    db.commit()
    return perms


@pytest.fixture(scope="function")
def admin_role(db, tenant, permissions):
    """Create admin role with all permissions"""
    role = Role(
        tenant_id=tenant.id,
        name="Admin",
        description="Administrator role",
        is_system=True
    )
    db.add(role)
    db.commit()
    db.refresh(role)
    
    for perm in permissions:
        role_perm = RolePermission(
            role_id=role.id,
            permission_id=perm.id
        )
        db.add(role_perm)
    
    db.commit()
    return role


@pytest.fixture(scope="function")
def user(db, tenant, branch, admin_role):
    """Create a test user"""
    user = User(
        tenant_id=tenant.id,
        email="test@test.com",
        username="testuser",
        hashed_password=hash_password("password123"),
        first_name="Test",
        last_name="User",
        is_superuser=False
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    
    # Assign role
    user_branch_role = UserBranchRole(
        user_id=user.id,
        branch_id=branch.id,
        role_id=admin_role.id
    )
    db.add(user_branch_role)
    db.commit()
    
    return user


@pytest.fixture(scope="function")
def superuser(db, tenant, branch):
    """Create a superuser"""
    user = User(
        tenant_id=tenant.id,
        email="admin@test.com",
        username="admin",
        hashed_password=hash_password("admin123"),
        is_superuser=True
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user
