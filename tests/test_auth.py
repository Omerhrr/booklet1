"""
Test Authentication and Security
"""

import pytest
from jose import jwt

from ..app.security import (
    hash_password,
    verify_password,
    create_access_token,
    verify_token,
    encrypt_data,
    decrypt_data
)
from ..app.crud import user


class TestPasswordHashing:
    """Tests for password hashing"""
    
    def test_hash_password(self):
        """Test password hashing"""
        password = "mysecretpassword"
        hashed = hash_password(password)
        
        assert hashed != password
        assert hashed.startswith("$2b$")
    
    def test_verify_password(self):
        """Test password verification"""
        password = "mysecretpassword"
        hashed = hash_password(password)
        
        assert verify_password(password, hashed) == True
        assert verify_password("wrongpassword", hashed) == False


class TestJWTTokens:
    """Tests for JWT token operations"""
    
    def test_create_access_token(self):
        """Test creating access token"""
        data = {"sub": "123", "email": "test@test.com"}
        token = create_access_token(data)
        
        assert token is not None
        assert isinstance(token, str)
    
    def test_verify_token(self):
        """Test token verification"""
        data = {"sub": "123"}
        token = create_access_token(data)
        
        payload = verify_token(token)
        
        assert payload is not None
        assert payload["sub"] == "123"
    
    def test_invalid_token_fails(self):
        """Test invalid token fails verification"""
        payload = verify_token("invalid.token.here")
        assert payload is None


class TestEncryption:
    """Tests for data encryption"""
    
    def test_encrypt_decrypt(self):
        """Test encryption and decryption"""
        original = "my-api-key-12345"
        
        encrypted = encrypt_data(original)
        decrypted = decrypt_data(encrypted)
        
        assert encrypted != original
        assert decrypted == original
    
    def test_encrypt_empty_string(self):
        """Test encrypting empty string"""
        assert encrypt_data("") == ""
        assert encrypt_data(None) == ""


class TestUserAuthentication:
    """Tests for user authentication"""
    
    def test_authenticate_user(self, db, tenant, branch):
        """Test user authentication"""
        # Create user
        test_user = user.create(
            db,
            email="auth@test.com",
            username="authuser",
            password="password123",
            tenant_id=tenant.id
        )
        
        # Authenticate
        auth_user = user.authenticate(
            db,
            email="auth@test.com",
            password="password123"
        )
        
        assert auth_user is not None
        assert auth_user.email == "auth@test.com"
    
    def test_wrong_password_fails(self, db, tenant):
        """Test wrong password fails"""
        user.create(
            db,
            email="wrong@test.com",
            username="wronguser",
            password="correctpass",
            tenant_id=tenant.id
        )
        
        auth_user = user.authenticate(
            db,
            email="wrong@test.com",
            password="wrongpass"
        )
        
        assert auth_user is None
    
    def test_nonexistent_user_fails(self, db):
        """Test non-existent user fails"""
        auth_user = user.authenticate(
            db,
            email="nonexistent@test.com",
            password="password"
        )
        
        assert auth_user is None
