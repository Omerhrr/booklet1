"""
Role CRUD Operations
"""

from typing import Optional, List
from sqlalchemy.orm import Session
from sqlalchemy import func

from ..models.permission import Role, Permission, RolePermission


class CRUDRole:
    
    def get(self, db: Session, role_id: int) -> Optional[Role]:
        return db.query(Role).filter(Role.id == role_id).first()
    
    def get_by_name(self, db: Session, tenant_id: int, name: str) -> Optional[Role]:
        return db.query(Role).filter(
            Role.tenant_id == tenant_id,
            Role.name == name
        ).first()
    
    def get_multi(
        self,
        db: Session,
        tenant_id: int,
        skip: int = 0,
        limit: int = 50
    ) -> List[Role]:
        return db.query(Role).filter(
            Role.tenant_id == tenant_id
        ).order_by(Role.name).offset(skip).limit(limit).all()
    
    def create(
        self,
        db: Session,
        *,
        tenant_id: int,
        name: str,
        description: str = None,
        permission_ids: List[int] = None,
        is_system: bool = False
    ) -> Role:
        role = Role(
            tenant_id=tenant_id,
            name=name,
            description=description,
            is_system=is_system
        )
        db.add(role)
        db.flush()
        
        if permission_ids:
            for perm_id in permission_ids:
                role_perm = RolePermission(
                    role_id=role.id,
                    permission_id=perm_id
                )
                db.add(role_perm)
        
        db.commit()
        db.refresh(role)
        return role
    
    def update(
        self,
        db: Session,
        *,
        role: Role,
        name: str = None,
        description: str = None,
        permission_ids: List[int] = None
    ) -> Role:
        if name:
            role.name = name
        if description:
            role.description = description
        
        if permission_ids is not None:
            # Remove existing permissions
            db.query(RolePermission).filter(
                RolePermission.role_id == role.id
            ).delete()
            
            # Add new permissions
            for perm_id in permission_ids:
                role_perm = RolePermission(
                    role_id=role.id,
                    permission_id=perm_id
                )
                db.add(role_perm)
        
        db.commit()
        db.refresh(role)
        return role
    
    def delete(self, db: Session, role_id: int) -> bool:
        role = self.get(db, role_id)
        if role and not role.is_system:
            db.delete(role)
            db.commit()
            return True
        return False
    
    def get_permissions(self, db: Session, role_id: int) -> List[Permission]:
        return db.query(Permission).join(RolePermission).filter(
            RolePermission.role_id == role_id
        ).all()


role = CRUDRole()
