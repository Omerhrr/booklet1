"""
Tenant and Subscription CRUD Operations
"""

from typing import Optional, List
from sqlalchemy.orm import Session
from sqlalchemy import select
from datetime import datetime, timedelta
from ..models.tenant import Tenant, SubscriptionPlan, Subscription
from ..security import encrypt_data, decrypt_data


# Default subscription plans
DEFAULT_PLANS = [
    {
        "name": "starter",
        "display_name": "Starter",
        "description": "Perfect for small businesses starting out",
        "monthly_price": 4500.00,  # Nigerian Naira (~$5)
        "yearly_price": 45000.00,
        "max_users": 3,
        "max_branches": 1,
        "max_transactions_per_month": 500,
        "max_storage_gb": 5,
        "max_api_calls_per_month": 1000,
        "features": ["Basic Accounting", "Invoicing", "Expense Tracking", "Reports"],
        "included_modules": []
    },
    {
        "name": "professional",
        "display_name": "Professional",
        "description": "For growing businesses with multiple branches",
        "monthly_price": 15000.00,  # Nigerian Naira (~$15)
        "yearly_price": 150000.00,
        "max_users": 15,
        "max_branches": 5,
        "max_transactions_per_month": 5000,
        "max_storage_gb": 50,
        "max_api_calls_per_month": 10000,
        "features": ["Advanced Accounting", "Multi-Branch", "Inventory", "HR & Payroll", "AI Analyst", "API Access"],
        "included_modules": ["payroll", "inventory_pro"]
    },
    {
        "name": "enterprise",
        "display_name": "Enterprise",
        "description": "For large organizations with complex needs",
        "monthly_price": 45000.00,  # Nigerian Naira (~$45)
        "yearly_price": 450000.00,
        "max_users": 999999,  # Unlimited
        "max_branches": 999999,
        "max_transactions_per_month": 999999,
        "max_storage_gb": 500,
        "max_api_calls_per_month": 999999,
        "features": ["Full ERP Suite", "Unlimited Users", "White-Label", "Priority Support", "Custom Integrations"],
        "included_modules": ["payroll_plus", "inventory_pro", "crm", "ecommerce", "pos"]
    }
]


class CRUDTenant:
    
    def get(self, db: Session, tenant_id: int) -> Optional[Tenant]:
        return db.query(Tenant).filter(Tenant.id == tenant_id).first()
    
    def get_by_subdomain(self, db: Session, subdomain: str) -> Optional[Tenant]:
        return db.query(Tenant).filter(Tenant.subdomain == subdomain).first()
    
    def get_multi(self, db: Session, skip: int = 0, limit: int = 100) -> List[Tenant]:
        return db.query(Tenant).offset(skip).limit(limit).all()
    
    def create(
        self,
        db: Session,
        *,
        business_name: str,
        subdomain: str,
        base_currency: str = "NGN",
        is_vat_registered: bool = False,
        vat_rate: float = 7.5
    ) -> Tenant:
        tenant = Tenant(
            business_name=business_name,
            subdomain=subdomain,
            base_currency=base_currency,
            is_vat_registered=is_vat_registered,
            vat_rate=vat_rate,
            subscription_status="trial"
        )
        db.add(tenant)
        db.commit()
        db.refresh(tenant)
        return tenant
    
    def update(self, db: Session, tenant: Tenant, **kwargs) -> Tenant:
        for key, value in kwargs.items():
            if hasattr(tenant, key):
                setattr(tenant, key, value)
        db.commit()
        db.refresh(tenant)
        return tenant
    
    def set_ai_config(
        self,
        db: Session,
        tenant: Tenant,
        provider: str,
        api_key: str
    ) -> Tenant:
        """Set AI provider configuration with encrypted API key"""
        tenant.ai_provider = provider
        tenant.encrypted_api_key = encrypt_data(api_key)
        db.commit()
        db.refresh(tenant)
        return tenant
    
    def get_decrypted_api_key(self, tenant: Tenant) -> Optional[str]:
        """Get decrypted AI API key"""
        if tenant.encrypted_api_key:
            return decrypt_data(tenant.encrypted_api_key)
        return None
    
    def increment_usage(
        self,
        db: Session,
        tenant: Tenant,
        metric: str,
        count: int = 1
    ) -> Tenant:
        """Increment usage metrics"""
        current = getattr(tenant, f"current_{metric}", 0) or 0
        setattr(tenant, f"current_{metric}", current + count)
        db.commit()
        db.refresh(tenant)
        return tenant
    
    def check_limits(
        self,
        db: Session,
        tenant: Tenant,
        metric: str
    ) -> bool:
        """Check if tenant is within limits for a metric"""
        current = getattr(tenant, f"current_{metric}", 0) or 0
        maximum = getattr(tenant, f"max_{metric}", 0) or 0
        return current < maximum


class CRUDSubscription:
    
    def get(self, db: Session, subscription_id: int) -> Optional[Subscription]:
        return db.query(Subscription).filter(Subscription.id == subscription_id).first()
    
    def get_by_tenant(self, db: Session, tenant_id: int) -> Optional[Subscription]:
        return db.query(Subscription).filter(Subscription.tenant_id == tenant_id).first()
    
    def get_plan(self, db: Session, plan_name: str) -> Optional[SubscriptionPlan]:
        return db.query(SubscriptionPlan).filter(SubscriptionPlan.name == plan_name).first()
    
    def get_plans(self, db: Session) -> List[SubscriptionPlan]:
        return db.query(SubscriptionPlan).filter(SubscriptionPlan.is_active == True).all()
    
    def create(
        self,
        db: Session,
        *,
        tenant_id: int,
        plan_id: int,
        is_trial: bool = True,
        trial_days: int = 14
    ) -> Subscription:
        now = datetime.utcnow()
        if is_trial:
            trial_end = now + timedelta(days=trial_days)
            subscription = Subscription(
                tenant_id=tenant_id,
                plan_id=plan_id,
                status="trial",
                is_trial=True,
                trial_end_date=trial_end,
                current_period_start=now,
                current_period_end=trial_end
            )
        else:
            subscription = Subscription(
                tenant_id=tenant_id,
                plan_id=plan_id,
                status="active",
                is_trial=False,
                current_period_start=now,
                current_period_end=now + timedelta(days=30)
            )
        
        db.add(subscription)
        db.commit()
        db.refresh(subscription)
        return subscription
    
    def seed_plans(self, db: Session) -> List[SubscriptionPlan]:
        """Seed default subscription plans"""
        plans = []
        for plan_data in DEFAULT_PLANS:
            existing = self.get_plan(db, plan_data["name"])
            if not existing:
                plan = SubscriptionPlan(**plan_data)
                db.add(plan)
                plans.append(plan)
        db.commit()
        return plans


tenant = CRUDTenant()
subscription = CRUDSubscription()
