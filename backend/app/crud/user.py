"""
User CRUD Operations
"""

from typing import Optional, List
from sqlalchemy.orm import Session
from sqlalchemy import select
from ..models.user import User
from ..models.branch import UserBranchRole, Branch
from ..models.permission import Role, RolePermission
from ..models.permission import Permission
from ..security import hash_password, verify_password


class CRUDUser:
    
    def get(self, db: Session, user_id: int) -> Optional[User]:
        """Get user by ID"""
        return db.query(User).filter(User.id == user_id).first()
    
    def get_by_email(self, db: Session, email: str) -> Optional[User]:
        """Get user by email"""
        return db.query(User).filter(User.email == email).first()
    
    def get_by_username(self, db: Session, username: str) -> Optional[User]:
        """Get user by username"""
        return db.query(User).filter(User.username == username).first()
    
    def get_multi(
        self,
        db: Session,
        tenant_id: int,
        skip: int = 0,
        limit: int = 100
    ) -> List[User]:
        """Get all users for tenant"""
        return db.query(User).filter(
            User.tenant_id == tenant_id
        ).offset(skip).limit(limit).all()
    
    def create(
        self,
        db: Session,
        *,
        email: str,
        username: str,
        password: str,
        tenant_id: int,
        first_name: str = None,
        last_name: str = None,
        is_superuser: bool = False
    ) -> User:
        """Create new user"""
        hashed_password = hash_password(password)
        
        user = User(
            email=email,
            username=username,
            hashed_password=hashed_password,
            tenant_id=tenant_id,
            first_name=first_name,
            last_name=last_name,
            is_superuser=is_superuser,
            is_active=True
        )
        db.add(user)
        db.commit()
        db.refresh(user)
        return user
    
    def authenticate(
        self,
        db: Session,
        email: str,
        password: str
    ) -> Optional[User]:
        """Authenticate user"""
        user = self.get_by_email(db, email=email)
        if not user:
            return None
        if not verify_password(password, user.hashed_password):
            return None
        return user
    
    def update(
        self,
        db: Session,
        *,
        user: User,
        **kwargs
    ) -> User:
        """Update user"""
        for key, value in kwargs.items():
            if hasattr(user, key):
                setattr(user, key, value)
        db.commit()
        db.refresh(user)
        return user
    
    def update_password(
        self,
        db: Session,
        user: User,
        new_password: str
    ) -> User:
        """Update user password"""
        user.hashed_password = hash_password(new_password)
        db.commit()
        db.refresh(user)
        return user
    
    def delete(self, db: Session, user_id: int) -> bool:
        """Delete user"""
        user = self.get(db, user_id)
        if user:
            db.delete(user)
            db.commit()
            return True
        return False
    
    def get_with_roles(
        self,
        db: Session,
        user_id: int
    ) -> Optional[User]:
        """Get user with roles and permissions"""
        return db.query(User).filter(
            User.id == user_id
        ).first()
    
    def get_user_with_relations(
        self,
        db: Session,
        user_id: int
    ) -> Optional[User]:
        """Get user with all relations for session"""
        from sqlalchemy.orm import joinedload
        
        return db.query(User).options(
            joinedload(User.tenant),
            joinedload(User.branch_roles).joinedload(UserBranchRole.branch),
            joinedload(User.branch_roles).joinedload(UserBranchRole.role)
                .joinedload(Role.permissions).joinedload(RolePermission.permission)
        ).filter(User.id == user_id).first()
    
    def assign_role(
        self,
        db: Session,
        user_id: int,
        branch_id: int,
        role_id: int
    ) -> UserBranchRole:
        """Assign role to user for branch"""
        assignment = UserBranchRole(
            user_id=user_id,
            branch_id=branch_id,
            role_id=role_id
        )
        db.add(assignment)
        db.commit()
        db.refresh(assignment)
        return assignment
    
    def remove_role(
        self,
        db: Session,
        user_id: int,
        branch_id: int,
        role_id: int
    ) -> bool:
        """Remove role from user for branch"""
        assignment = db.query(UserBranchRole).filter(
            UserBranchRole.user_id == user_id,
            UserBranchRole.branch_id == branch_id,
            UserBranchRole.role_id == role_id
        ).first()
        
        if assignment:
            db.delete(assignment)
            db.commit()
            return True
        return False


user = CRUDUser()
