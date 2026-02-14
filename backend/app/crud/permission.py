"""
Permission CRUD Operations
"""

from typing import List, Optional
from sqlalchemy.orm import Session
from ..models.permission import Permission, RolePermission, Role
# from ..models.role import Role


# Default permissions to seed
DEFAULT_PERMISSIONS = [
    # Users & Team
    {"name": "users:view", "display_name": "View Users", "category": "Users & Team", "description": "View team members list"},
    {"name": "users:create", "display_name": "Create Users", "category": "Users & Team", "description": "Invite new team members"},
    {"name": "users:edit", "display_name": "Edit Users", "category": "Users & Team", "description": "Edit team member details"},
    {"name": "users:delete", "display_name": "Delete Users", "category": "Users & Team", "description": "Remove team members"},
    {"name": "users:assign-roles", "display_name": "Assign Roles", "category": "Users & Team", "description": "Assign roles to users"},
    
    # Roles
    {"name": "roles:view", "display_name": "View Roles", "category": "Roles & Permissions", "description": "View roles list"},
    {"name": "roles:create", "display_name": "Create Roles", "category": "Roles & Permissions", "description": "Create new roles"},
    {"name": "roles:edit", "display_name": "Edit Roles", "category": "Roles & Permissions", "description": "Edit role permissions"},
    {"name": "roles:delete", "display_name": "Delete Roles", "category": "Roles & Permissions", "description": "Delete custom roles"},
    
    # Branches
    {"name": "branches:view", "display_name": "View Branches", "category": "Branches", "description": "View branches list"},
    {"name": "branches:create", "display_name": "Create Branches", "category": "Branches", "description": "Create new branches"},
    {"name": "branches:edit", "display_name": "Edit Branches", "category": "Branches", "description": "Edit branch details"},
    {"name": "branches:delete", "display_name": "Delete Branches", "category": "Branches", "description": "Delete branches"},
    
    # Banking
    {"name": "bank:view", "display_name": "View Bank Accounts", "category": "Banking", "description": "View bank accounts"},
    {"name": "bank:create", "display_name": "Manage Bank Accounts", "category": "Banking", "description": "Create and manage bank accounts"},
    {"name": "bank:reconcile", "display_name": "Reconcile Bank", "category": "Banking", "description": "Perform bank reconciliation"},
    
    # Customers
    {"name": "customers:view", "display_name": "View Customers", "category": "Customers", "description": "View customers list"},
    {"name": "customers:create", "display_name": "Create Customers", "category": "Customers", "description": "Add new customers"},
    {"name": "customers:edit", "display_name": "Edit Customers", "category": "Customers", "description": "Edit customer details"},
    {"name": "customers:delete", "display_name": "Delete Customers", "category": "Customers", "description": "Delete customers"},
    
    # Vendors
    {"name": "vendors:view", "display_name": "View Vendors", "category": "Vendors", "description": "View vendors list"},
    {"name": "vendors:create", "display_name": "Create Vendors", "category": "Vendors", "description": "Add new vendors"},
    {"name": "vendors:edit", "display_name": "Edit Vendors", "category": "Vendors", "description": "Edit vendor details"},
    {"name": "vendors:delete", "display_name": "Delete Vendors", "category": "Vendors", "description": "Delete vendors"},
    
    # Inventory
    {"name": "inventory:view", "display_name": "View Inventory", "category": "Inventory", "description": "View products and stock"},
    {"name": "inventory:create", "display_name": "Create Products", "category": "Inventory", "description": "Add new products"},
    {"name": "inventory:edit", "display_name": "Edit Products", "category": "Inventory", "description": "Edit product details"},
    {"name": "inventory:delete", "display_name": "Delete Products", "category": "Inventory", "description": "Delete products"},
    {"name": "inventory:adjust-stock", "display_name": "Adjust Stock", "category": "Inventory", "description": "Adjust stock quantities"},
    
    # Purchases
    {"name": "purchases:view", "display_name": "View Purchases", "category": "Purchases", "description": "View purchase bills"},
    {"name": "purchases:create", "display_name": "Create Purchases", "category": "Purchases", "description": "Create purchase bills"},
    {"name": "purchases:edit", "display_name": "Edit Purchases", "category": "Purchases", "description": "Edit purchase bills"},
    {"name": "purchases:delete", "display_name": "Delete Purchases", "category": "Purchases", "description": "Delete purchase bills"},
    {"name": "purchases:create-debit-note", "display_name": "Create Debit Notes", "category": "Purchases", "description": "Create debit notes"},
    
    # Sales
    {"name": "sales:view", "display_name": "View Sales", "category": "Sales", "description": "View sales invoices"},
    {"name": "sales:create", "display_name": "Create Sales", "category": "Sales", "description": "Create sales invoices"},
    {"name": "sales:edit", "display_name": "Edit Sales", "category": "Sales", "description": "Edit sales invoices"},
    {"name": "sales:delete", "display_name": "Delete Sales", "category": "Sales", "description": "Delete sales invoices"},
    {"name": "sales:create-credit-note", "display_name": "Create Credit Notes", "category": "Sales", "description": "Create credit notes"},
    
    # Expenses
    {"name": "expenses:view", "display_name": "View Expenses", "category": "Expenses", "description": "View expenses"},
    {"name": "expenses:create", "display_name": "Create Expenses", "category": "Expenses", "description": "Record expenses"},
    {"name": "expenses:edit", "display_name": "Edit Expenses", "category": "Expenses", "description": "Edit expenses"},
    {"name": "expenses:delete", "display_name": "Delete Expenses", "category": "Expenses", "description": "Delete expenses"},
    
    # Accounting
    {"name": "accounting:view", "display_name": "View Accounting", "category": "Accounting", "description": "View chart of accounts and ledgers"},
    {"name": "accounting:create", "display_name": "Create Entries", "category": "Accounting", "description": "Create journal entries"},
    {"name": "accounting:edit", "display_name": "Edit Accounts", "category": "Accounting", "description": "Edit chart of accounts"},
    {"name": "accounting:delete", "display_name": "Delete Accounts", "category": "Accounting", "description": "Delete accounts"},
    
    # HR
    {"name": "hr:view", "display_name": "View HR", "category": "HR & Payroll", "description": "View employees"},
    {"name": "hr:create", "display_name": "Create Employees", "category": "HR & Payroll", "description": "Add employees"},
    {"name": "hr:edit", "display_name": "Edit Employees", "category": "HR & Payroll", "description": "Edit employee details"},
    {"name": "hr:delete", "display_name": "Delete Employees", "category": "HR & Payroll", "description": "Remove employees"},
    {"name": "hr:run-payroll", "display_name": "Run Payroll", "category": "HR & Payroll", "description": "Process payroll"},
    
    # Budgeting
    {"name": "budgeting:view", "display_name": "View Budgets", "category": "Budgeting", "description": "View budgets"},
    {"name": "budgeting:create", "display_name": "Create Budgets", "category": "Budgeting", "description": "Create budgets"},
    {"name": "budgeting:edit", "display_name": "Edit Budgets", "category": "Budgeting", "description": "Edit budgets"},
    {"name": "budgeting:delete", "display_name": "Delete Budgets", "category": "Budgeting", "description": "Delete budgets"},
    
    # Reports
    {"name": "report:view", "display_name": "View Reports", "category": "Reports", "description": "View financial reports"},
    {"name": "report:export", "display_name": "Export Reports", "category": "Reports", "description": "Export reports to PDF/Excel"},
    
    # AI
    {"name": "jarvis:ask", "display_name": "Use AI Analyst", "category": "AI Analyst", "description": "Ask Jarvis questions"},
    
    # Settings
    {"name": "settings:view", "display_name": "View Settings", "category": "Settings", "description": "View settings"},
    {"name": "settings:edit", "display_name": "Edit Settings", "category": "Settings", "description": "Edit settings"},
    
    # Fixed Assets
    {"name": "fixed-assets:view", "display_name": "View Fixed Assets", "category": "Fixed Assets", "description": "View fixed assets"},
    {"name": "fixed-assets:create", "display_name": "Create Fixed Assets", "category": "Fixed Assets", "description": "Add fixed assets"},
    {"name": "fixed-assets:edit", "display_name": "Edit Fixed Assets", "category": "Fixed Assets", "description": "Edit fixed assets"},
    {"name": "fixed-assets:delete", "display_name": "Delete Fixed Assets", "category": "Fixed Assets", "description": "Delete fixed assets"},
    {"name": "fixed-assets:depreciate", "display_name": "Run Depreciation", "category": "Fixed Assets", "description": "Run depreciation"},
]


class CRUDPermission:
    
    def get(self, db: Session, permission_id: int) -> Optional[Permission]:
        return db.query(Permission).filter(Permission.id == permission_id).first()
    
    def get_by_name(self, db: Session, name: str) -> Optional[Permission]:
        return db.query(Permission).filter(Permission.name == name).first()
    
    def get_multi(self, db: Session, skip: int = 0, limit: int = 100) -> List[Permission]:
        return db.query(Permission).offset(skip).limit(limit).all()
    
    def get_by_category(self, db: Session, category: str) -> List[Permission]:
        return db.query(Permission).filter(Permission.category == category).all()
    
    def get_all_categories(self, db: Session) -> List[str]:
        """Get all unique categories"""
        from sqlalchemy import distinct
        return [c[0] for c in db.query(distinct(Permission.category)).all()]
    
    def create(self, db: Session, *, name: str, display_name: str, category: str, description: str = None) -> Permission:
        permission = Permission(
            name=name,
            display_name=display_name,
            category=category,
            description=description
        )
        db.add(permission)
        db.commit()
        db.refresh(permission)
        return permission
    
    def seed_permissions(self, db: Session) -> List[Permission]:
        """Seed all default permissions"""
        permissions = []
        for perm_data in DEFAULT_PERMISSIONS:
            existing = self.get_by_name(db, perm_data["name"])
            if not existing:
                permission = self.create(db, **perm_data)
                permissions.append(permission)
        return permissions


permission = CRUDPermission()
