"""
Authentication Router - Login, Signup, Logout
"""

from fastapi import APIRouter, Depends, HTTPException, status, Request, Response
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime, timedelta
import re

from ..database import get_db
from .. import crud
from ..models.tenant import Tenant
from ..models.user import User
from ..models.branch import Branch
from ..models.permission import Role, Permission, RolePermission
from ..security import (
    create_access_token,
    create_refresh_token,
    verify_token,
    hash_password,
    verify_password
)

router = APIRouter()

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login", auto_error=False)


# ============================================
# SCHEMAS
# ============================================

class LoginRequest(BaseModel):
    email: EmailStr
    password: str
    tenant_subdomain: Optional[str] = None


class SignupRequest(BaseModel):
    business_name: str
    email: EmailStr
    username: str
    password: str
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    subdomain: str


class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int


class UserResponse(BaseModel):
    id: int
    email: str
    username: str
    first_name: Optional[str]
    last_name: Optional[str]
    tenant_id: int
    tenant_name: str
    is_superuser: bool
    
    class Config:
        from_attributes = True


# ============================================
# DEPENDENCIES
# ============================================

async def get_current_user(
    request: Request,
    db: Session = Depends(get_db)
) -> User:
    """Get current user from JWT token in cookie or header"""
    
    # Try to get token from cookie first
    token = request.cookies.get("access_token")
    
    # Fall back to Authorization header
    if not token:
        auth_header = request.headers.get("Authorization")
        if auth_header and auth_header.startswith("Bearer "):
            token = auth_header.split(" ")[1]
    
    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated"
        )
    
    payload = verify_token(token)
    if not payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token"
        )
    
    user_id = payload.get("sub")
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token payload"
        )
    
    user = crud.user.get_user_with_relations(db, int(user_id))
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found"
        )
    
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Account is inactive"
        )
    
    if not user.tenant.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Tenant account is suspended"
        )
    
    return user


async def get_current_active_user(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> dict:
    """Get current user with branch and permissions"""
    
    # Get accessible branches
    accessible_branches = []
    for assignment in current_user.branch_roles:
        branch = assignment.branch
        accessible_branches.append({
            "id": branch.id,
            "name": branch.name,
            "is_default": branch.is_default
        })
    
    # If superuser, get all branches
    if current_user.is_superuser:
        all_branches = db.query(Branch).filter(
            Branch.tenant_id == current_user.tenant_id,
            Branch.is_active == True
        ).all()
        accessible_branches = [{"id": b.id, "name": b.name, "is_default": b.is_default} for b in all_branches]
    
    # Get selected branch from cookie or use default
    # For now, use the first accessible branch
    selected_branch = next(
        (b for b in accessible_branches if b.get("is_default")),
        accessible_branches[0] if accessible_branches else None
    )
    
    # Get permissions
    permissions = []
    if current_user.is_superuser:
        all_perms = db.query(Permission).all()
        permissions = [p.name for p in all_perms]
    else:
        for assignment in current_user.branch_roles:
            for rp in assignment.role.permissions:
                if rp.permission.name not in permissions:
                    permissions.append(rp.permission.name)
    
    return {
        "user": current_user,
        "tenant": current_user.tenant,
        "selected_branch": selected_branch,
        "accessible_branches": accessible_branches,
        "permissions": permissions
    }


# ============================================
# ROUTES
# ============================================

@router.post("/signup", response_model=TokenResponse, status_code=status.HTTP_201_CREATED)
async def signup(
    request: SignupRequest,
    db: Session = Depends(get_db)
):
    """Create new tenant, user, and authenticate"""
    
    # Validate subdomain
    if not re.match(r'^[a-z0-9-]+$', request.subdomain.lower()):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Subdomain can only contain lowercase letters, numbers, and hyphens"
        )
    
    # Check if subdomain exists
    existing_tenant = crud.tenant.get_by_subdomain(db, request.subdomain.lower())
    if existing_tenant:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Subdomain already taken"
        )
    
    # Check if email exists
    existing_user = crud.user.get_by_email(db, request.email)
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    
    # Check if username exists
    existing_username = crud.user.get_by_username(db, request.username)
    if existing_username:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already taken"
        )
    
    # Create tenant
    tenant = crud.tenant.create(
        db,
        business_name=request.business_name,
        subdomain=request.subdomain.lower(),
        base_currency="NGN"  # Default to Nigerian Naira
    )
    
    # Create default branch
    branch = Branch(
        tenant_id=tenant.id,
        name="Main Branch",
        is_default=True,
        currency="NGN"
    )
    db.add(branch)
    db.commit()
    db.refresh(branch)
    
    # Create admin role with all permissions
    admin_role = Role(
        tenant_id=tenant.id,
        name="Admin",
        description="Full access to all features",
        is_system=True
    )
    db.add(admin_role)
    db.commit()
    db.refresh(admin_role)
    
    # Assign all permissions to admin role
    all_permissions = db.query(Permission).all()
    for perm in all_permissions:
        role_perm = RolePermission(
            role_id=admin_role.id,
            permission_id=perm.id
        )
        db.add(role_perm)
    db.commit()
    
    # Create superuser
    user = crud.user.create(
        db,
        email=request.email,
        username=request.username,
        password=request.password,
        tenant_id=tenant.id,
        first_name=request.first_name,
        last_name=request.last_name,
        is_superuser=True
    )
    
    # Assign admin role to user for the branch
    from ..models.branch import UserBranchRole
    user_branch_role = UserBranchRole(
        user_id=user.id,
        branch_id=branch.id,
        role_id=admin_role.id
    )
    db.add(user_branch_role)
    db.commit()
    
    # Create trial subscription
    starter_plan = crud.subscription.get_plan(db, "starter")
    if starter_plan:
        crud.subscription.create(
            db,
            tenant_id=tenant.id,
            plan_id=starter_plan.id,
            is_trial=True,
            trial_days=14
        )
    
    # Create default chart of accounts
    await _create_default_accounts(db, tenant.id, branch.id)
    
    # Create tokens
    access_token = create_access_token(
        data={"sub": str(user.id), "tenant_id": tenant.id}
    )
    refresh_token = create_refresh_token(
        data={"sub": str(user.id), "tenant_id": tenant.id}
    )
    
    # Update last login
    user.last_login = datetime.utcnow()
    db.commit()
    
    return TokenResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        expires_in=1800
    )


@router.post("/login", response_model=TokenResponse)
async def login(
    request: LoginRequest,
    response: Response,
    db: Session = Depends(get_db)
):
    """Authenticate user and return tokens"""
    
    # Find user
    user = crud.user.get_by_email(db, request.email)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials"
        )
    
    # Verify password
    if not verify_password(request.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials"
        )
    
    # Check if user is active
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Account is inactive"
        )
    
    # Check tenant status
    if not user.tenant.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Tenant account is suspended"
        )
    
    # Create tokens
    access_token = create_access_token(
        data={"sub": str(user.id), "tenant_id": user.tenant_id}
    )
    refresh_token = create_refresh_token(
        data={"sub": str(user.id), "tenant_id": user.tenant_id}
    )
    
    # Set HTTP-only cookie
    response.set_cookie(
        key="access_token",
        value=access_token,
        httponly=True,
        max_age=1800,
        samesite="lax"
    )
    
    # Update last login
    user.last_login = datetime.utcnow()
    db.commit()
    
    return TokenResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        expires_in=1800
    )


@router.post("/logout")
async def logout(response: Response):
    """Logout user by clearing cookie"""
    response.delete_cookie("access_token")
    return {"message": "Logged out successfully"}


@router.post("/refresh", response_model=TokenResponse)
async def refresh_token(
    request: Request,
    db: Session = Depends(get_db)
):
    """Refresh access token using refresh token"""
    
    # Get refresh token from body or cookie
    refresh_token = request.cookies.get("refresh_token")
    
    if not refresh_token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="No refresh token provided"
        )
    
    payload = verify_token(refresh_token, "refresh")
    if not payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh token"
        )
    
    user_id = payload.get("sub")
    user = crud.user.get(db, int(user_id))
    
    if not user or not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found or inactive"
        )
    
    access_token = create_access_token(
        data={"sub": str(user.id), "tenant_id": user.tenant_id}
    )
    new_refresh_token = create_refresh_token(
        data={"sub": str(user.id), "tenant_id": user.tenant_id}
    )
    
    return TokenResponse(
        access_token=access_token,
        refresh_token=new_refresh_token,
        expires_in=1800
    )


@router.get("/me", response_model=UserResponse)
async def get_me(
    session: dict = Depends(get_current_active_user)
):
    """Get current user info"""
    user = session["user"]
    return UserResponse(
        id=user.id,
        email=user.email,
        username=user.username,
        first_name=user.first_name,
        last_name=user.last_name,
        tenant_id=user.tenant_id,
        tenant_name=user.tenant.business_name,
        is_superuser=user.is_superuser
    )


# ============================================
# HELPERS
# ============================================

async def _create_default_accounts(db: Session, tenant_id: int, branch_id: int):
    """Create default chart of accounts for new tenant"""
    from ..models.account import Account, AccountType
    
    default_accounts = [
        # Assets
        {"code": "1000", "name": "Cash", "type": AccountType.ASSET, "is_system_account": True},
        {"code": "1100", "name": "Bank", "type": AccountType.ASSET, "is_system_account": True},
        {"code": "1200", "name": "Accounts Receivable", "type": AccountType.ASSET, "is_system_account": True},
        {"code": "1300", "name": "Inventory", "type": AccountType.ASSET, "is_system_account": True},
        {"code": "1400", "name": "VAT Refundable", "type": AccountType.ASSET, "is_system_account": True},
        {"code": "1500", "name": "Fixed Assets", "type": AccountType.ASSET, "is_system_account": True},
        {"code": "1510", "name": "Accumulated Depreciation", "type": AccountType.ASSET, "is_system_account": True},
        
        # Liabilities
        {"code": "2000", "name": "Accounts Payable", "type": AccountType.LIABILITY, "is_system_account": True},
        {"code": "2100", "name": "VAT Payable", "type": AccountType.LIABILITY, "is_system_account": True},
        {"code": "2200", "name": "PAYE Payable", "type": AccountType.LIABILITY, "is_system_account": True},
        {"code": "2210", "name": "Pension Payable", "type": AccountType.LIABILITY, "is_system_account": True},
        {"code": "2300", "name": "Payroll Liabilities", "type": AccountType.LIABILITY, "is_system_account": True},
        {"code": "2400", "name": "Loans", "type": AccountType.LIABILITY, "is_system_account": True},
        
        # Equity
        {"code": "3000", "name": "Owner's Capital", "type": AccountType.EQUITY, "is_system_account": True},
        {"code": "3100", "name": "Retained Earnings", "type": AccountType.EQUITY, "is_system_account": True},
        
        # Revenue
        {"code": "4000", "name": "Sales Revenue", "type": AccountType.REVENUE, "is_system_account": True},
        {"code": "4100", "name": "Other Income", "type": AccountType.REVENUE, "is_system_account": True},
        {"code": "4200", "name": "Interest Income", "type": AccountType.REVENUE, "is_system_account": True},
        {"code": "4300", "name": "Discount Received", "type": AccountType.REVENUE, "is_system_account": True},
        
        # Expenses
        {"code": "5000", "name": "Cost of Goods Sold", "type": AccountType.EXPENSE, "is_system_account": True},
        {"code": "5100", "name": "Salaries & Wages", "type": AccountType.EXPENSE, "is_system_account": True},
        {"code": "5200", "name": "Rent", "type": AccountType.EXPENSE, "is_system_account": True},
        {"code": "5300", "name": "Utilities", "type": AccountType.EXPENSE, "is_system_account": True},
        {"code": "5400", "name": "Office Expenses", "type": AccountType.EXPENSE, "is_system_account": True},
        {"code": "5500", "name": "Travel & Vehicle", "type": AccountType.EXPENSE, "is_system_account": True},
        {"code": "5600", "name": "Marketing", "type": AccountType.EXPENSE, "is_system_account": True},
        {"code": "5700", "name": "Bank Charges", "type": AccountType.EXPENSE, "is_system_account": True},
        {"code": "5800", "name": "Bad Debts", "type": AccountType.EXPENSE, "is_system_account": True},
        {"code": "5900", "name": "Depreciation Expense", "type": AccountType.EXPENSE, "is_system_account": True},
    ]
    
    for acc in default_accounts:
        account = Account(
            tenant_id=tenant_id,
            branch_id=branch_id,
            code=acc["code"],
            name=acc["name"],
            type=acc["type"],
            is_system_account=acc["is_system_account"]
        )
        db.add(account)
    
    db.commit()
