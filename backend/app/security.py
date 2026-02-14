"""
Security Module - Authentication, JWT, Encryption
"""

from datetime import datetime, timedelta
from typing import Optional, Dict, Any
from jose import JWTError, jwt
from passlib.context import CryptContext
from cryptography.fernet import Fernet
from fastapi import Depends, HTTPException, Request, status
from sqlalchemy.orm import Session
import secrets
import os

# Configuration
SECRET_KEY = os.getenv("SECRET_KEY", secrets.token_urlsafe(32))
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30
REFRESH_TOKEN_EXPIRE_DAYS = 7

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Encryption key for sensitive data (Fernet requires 32 url-safe base64-encoded bytes)
ENCRYPTION_KEY = os.getenv("ENCRYPTION_KEY", Fernet.generate_key().decode())
fernet = Fernet(ENCRYPTION_KEY.encode() if isinstance(ENCRYPTION_KEY, str) else ENCRYPTION_KEY)


# ============================================
# PASSWORD UTILITIES
# ============================================

def hash_password(password: str) -> str:
    """Hash a password using bcrypt"""
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a password against a hash"""
    return pwd_context.verify(plain_password, hashed_password)


# ============================================
# JWT TOKEN UTILITIES
# ============================================

def create_access_token(
    data: Dict[str, Any],
    expires_delta: Optional[timedelta] = None
) -> str:
    """Create JWT access token"""
    to_encode = data.copy()
    
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode.update({
        "exp": expire,
        "iat": datetime.utcnow(),
        "type": "access"
    })
    
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def create_refresh_token(
    data: Dict[str, Any],
    expires_delta: Optional[timedelta] = None
) -> str:
    """Create JWT refresh token"""
    to_encode = data.copy()
    
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
    
    to_encode.update({
        "exp": expire,
        "iat": datetime.utcnow(),
        "type": "refresh"
    })
    
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def decode_token(token: str) -> Optional[Dict[str, Any]]:
    """Decode and validate JWT token"""
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except JWTError:
        return None


def verify_token(token: str, token_type: str = "access") -> Optional[Dict[str, Any]]:
    """Verify token type and validity"""
    payload = decode_token(token)
    if payload and payload.get("type") == token_type:
        return payload
    return None


# ============================================
# ENCRYPTION UTILITIES
# ============================================

def encrypt_data(data: str) -> str:
    """Encrypt sensitive data using Fernet symmetric encryption"""
    if not data:
        return ""
    encrypted = fernet.encrypt(data.encode())
    return encrypted.decode()


def decrypt_data(encrypted_data: str) -> str:
    """Decrypt sensitive data"""
    if not encrypted_data:
        return ""
    try:
        decrypted = fernet.decrypt(encrypted_data.encode())
        return decrypted.decode()
    except Exception:
        return ""


# ============================================
# API KEY GENERATION
# ============================================

def generate_api_key() -> str:
    """Generate a secure API key"""
    return secrets.token_urlsafe(32)


def generate_password_reset_token(email: str) -> str:
    """Generate password reset token"""
    expires = datetime.utcnow() + timedelta(hours=24)
    return create_access_token(
        data={"sub": email, "purpose": "password_reset"},
        expires_delta=timedelta(hours=24)
    )


def verify_password_reset_token(token: str) -> Optional[str]:
    """Verify password reset token and return email"""
    payload = verify_token(token)
    if payload and payload.get("purpose") == "password_reset":
        return payload.get("sub")
    return None


# ============================================
# PERMISSION CHECKER
# ============================================

class PermissionChecker:
    """Check user permissions"""
    
    def __init__(self, required_permissions: list[str]):
        self.required_permissions = set(required_permissions)
    
    def __call__(self, user, db) -> bool:
        """Check if user has required permissions"""
        # Superusers bypass all checks
        if user.is_superuser:
            return True
        
        # Get user's permissions from roles
        user_permissions = self._get_user_permissions(user, db)
        
        # Check all required permissions present
        if not self.required_permissions.issubset(user_permissions):
            from fastapi import HTTPException
            raise HTTPException(
                status_code=403,
                detail=f"Missing required permissions: {', '.join(self.required_permissions - user_permissions)}"
            )
        
        return True
    
    def _get_user_permissions(self, user, db) -> set:
        """Get all permissions for a user from their roles"""
        permissions = set()
        for assignment in user.branch_roles:
            for rp in assignment.role.permissions:
                permissions.add(rp.permission.name)
        return permissions


def get_user_permissions(user, db) -> set:
    """Get all permissions for a user"""
    if user.is_superuser:
        # Return all permissions for superuser
        from .models.permission import Permission
        all_perms = db.query(Permission).all()
        return {p.name for p in all_perms}

    permissions = set()
    for assignment in user.branch_roles:
        for rp in assignment.role.permissions:
            permissions.add(rp.permission.name)
    return permissions


# ============================================
# FASTAPI DEPENDENCIES
# ============================================

async def get_current_user(
    request: Request,
    db: Session = Depends(lambda: None)
) -> Any:
    """Get current user from JWT token in cookie or header"""

    from .database import get_db
    from . import crud

    db = next(get_db())

    try:
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

        user = crud.user.get_with_relations(db, int(user_id))
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
    finally:
        db.close()


# Alias for backward compatibility
get_password_hash = hash_password
