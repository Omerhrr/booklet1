"""
Tenant and Subscription Models
Public schema - Shared across all tenants
"""

from sqlalchemy import Column, Integer, String, Boolean, DateTime, Float, Text, ForeignKey, Enum, JSON
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import enum

from ..database import Base


class SubscriptionTier(str, enum.Enum):
    STARTER = "starter"
    PROFESSIONAL = "professional"
    ENTERPRISE = "enterprise"


class SubscriptionStatus(str, enum.Enum):
    ACTIVE = "active"
    TRIAL = "trial"
    PAST_DUE = "past_due"
    CANCELLED = "cancelled"
    SUSPENDED = "suspended"


class BillingCycle(str, enum.Enum):
    MONTHLY = "monthly"
    YEARLY = "yearly"


class InvoiceStatus(str, enum.Enum):
    DRAFT = "draft"
    SENT = "sent"
    PAID = "paid"
    PAST_DUE = "past_due"
    VOID = "void"


class PaymentStatus(str, enum.Enum):
    PENDING = "pending"
    COMPLETED = "completed"
    FAILED = "failed"
    REFUNDED = "refunded"


class LineItemType(str, enum.Enum):
    BASE_PLAN = "base_plan"
    ADDON = "addon"
    USAGE_OVERAGE = "usage_overage"
    DISCOUNT = "discount"
    SETUP_FEE = "setup_fee"


class Tenant(Base):
    """Tenant/Business record - stored in public schema"""
    __tablename__ = "tenants"
    
    
    id = Column(Integer, primary_key=True, index=True)
    subdomain = Column(String(50), unique=True, index=True, nullable=False)
    business_name = Column(String(255), nullable=False)
    logo_url = Column(String(500), nullable=True)
    primary_color = Column(String(7), default="#3B82F6")
    custom_domain = Column(String(100), unique=True, nullable=True)
    
    # Subscription details
    subscription_tier = Column(Enum(SubscriptionTier), default=SubscriptionTier.STARTER)
    subscription_status = Column(Enum(SubscriptionStatus), default=SubscriptionStatus.TRIAL)
    trial_end_date = Column(DateTime(timezone=True), nullable=True)
    subscription_end_date = Column(DateTime(timezone=True), nullable=True)
    
    # Resource limits (enforce at application level)
    max_users = Column(Integer, default=3)
    max_branches = Column(Integer, default=1)
    max_transactions_per_month = Column(Integer, default=500)
    max_storage_gb = Column(Integer, default=5)
    
    # Usage tracking
    current_users = Column(Integer, default=0)
    current_branches = Column(Integer, default=0)
    current_month_transactions = Column(Integer, default=0)
    current_storage_gb = Column(Float, default=0.0)
    
    # Configuration - Default currency is Nigerian Naira
    base_currency = Column(String(3), default="NGN")
    is_vat_registered = Column(Boolean, default=False)
    vat_rate = Column(Float, default=7.5)  # Nigerian VAT rate
    fiscal_year_start = Column(Integer, default=1)  # January
    
    # Automation settings
    depreciation_day = Column(Integer, default=1)
    auto_depreciate = Column(Boolean, default=False)
    auto_write_off_bad_debts = Column(Boolean, default=False)
    bad_debt_age_days = Column(Integer, default=90)
    
    # AI configuration
    ai_provider = Column(String(20), nullable=True)  # "gemini" or "zai"
    encrypted_api_key = Column(Text, nullable=True)
    
    # Status
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    users = relationship("User", back_populates="tenant", cascade="all, delete-orphan")
    branches = relationship("Branch", back_populates="tenant", cascade="all, delete-orphan")
    roles = relationship("Role", back_populates="tenant", cascade="all, delete-orphan")
    subscription = relationship("Subscription", back_populates="tenant", uselist=False, cascade="all, delete-orphan")


class SubscriptionPlan(Base):
    """Subscription plan definitions"""
    __tablename__ = "subscription_plans"
    
    
    id = Column(Integer, primary_key=True)
    name = Column(String(50), unique=True)  # starter, professional, enterprise
    display_name = Column(String(100))
    description = Column(Text)
    
    # Pricing - Default in Nigerian Naira
    monthly_price = Column(Float)
    yearly_price = Column(Float)
    currency = Column(String(3), default="NGN")
    
    # Limits
    max_users = Column(Integer)
    max_branches = Column(Integer)
    max_transactions_per_month = Column(Integer)
    max_storage_gb = Column(Integer)
    max_api_calls_per_month = Column(Integer)
    
    # Features (JSON array)
    features = Column(JSON)
    included_modules = Column(JSON)
    
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    subscriptions = relationship("Subscription", back_populates="plan")


class Subscription(Base):
    """Tenant's current subscription"""
    __tablename__ = "subscriptions"
    
    
    id = Column(Integer, primary_key=True)
    tenant_id = Column(Integer, ForeignKey("tenants.id"), unique=True, nullable=False)
    
    plan_id = Column(Integer, ForeignKey("subscription_plans.id"))
    status = Column(Enum(SubscriptionStatus), default=SubscriptionStatus.TRIAL)
    billing_cycle = Column(Enum(BillingCycle), default=BillingCycle.MONTHLY)
    
    current_period_start = Column(DateTime(timezone=True))
    current_period_end = Column(DateTime(timezone=True))
    
    is_trial = Column(Boolean, default=True)
    trial_end_date = Column(DateTime(timezone=True), nullable=True)
    
    # Payment integration
    stripe_customer_id = Column(String(100), nullable=True)
    stripe_subscription_id = Column(String(100), nullable=True)
    paga_customer_id = Column(String(100), nullable=True)  # Paga for Nigeria
    default_payment_method = Column(String(50))
    
    cancel_at_period_end = Column(Boolean, default=False)
    canceled_at = Column(DateTime(timezone=True), nullable=True)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    tenant = relationship("Tenant", back_populates="subscription")
    plan = relationship("SubscriptionPlan", back_populates="subscriptions")


class Invoice(Base):
    """Billing invoices"""
    __tablename__ = "billing_invoices"
    
    
    id = Column(Integer, primary_key=True)
    tenant_id = Column(Integer, ForeignKey("tenants.id"), nullable=False)
    
    invoice_number = Column(String(50), unique=True)
    invoice_date = Column(DateTime(timezone=True))
    due_date = Column(DateTime(timezone=True))
    
    status = Column(Enum(InvoiceStatus), default=InvoiceStatus.DRAFT)
    
    subtotal = Column(Float)
    tax_amount = Column(Float, default=0)
    discount_amount = Column(Float, default=0)
    total_amount = Column(Float)
    currency = Column(String(3), default="NGN")
    
    paid_date = Column(DateTime(timezone=True), nullable=True)
    payment_method = Column(String(50), nullable=True)
    transaction_id = Column(String(100), nullable=True)
    
    stripe_invoice_id = Column(String(100), nullable=True)
    paga_transaction_id = Column(String(100), nullable=True)
    
    pdf_url = Column(String(500), nullable=True)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    line_items = relationship("InvoiceLineItem", back_populates="invoice", cascade="all, delete-orphan")
    payments = relationship("Payment", back_populates="invoice")


class InvoiceLineItem(Base):
    """Invoice line items"""
    __tablename__ = "invoice_line_items"
    
    
    id = Column(Integer, primary_key=True)
    invoice_id = Column(Integer, ForeignKey("billing_invoices.id"), nullable=False)
    
    description = Column(String(255))
    quantity = Column(Integer, default=1)
    unit_price = Column(Float)
    amount = Column(Float)
    
    item_type = Column(Enum(LineItemType))
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    invoice = relationship("Invoice", back_populates="line_items")


class Payment(Base):
    """Payment records"""
    __tablename__ = "payments"
    
    
    id = Column(Integer, primary_key=True)
    tenant_id = Column(Integer, ForeignKey("tenants.id"), nullable=False)
    invoice_id = Column(Integer, ForeignKey("billing_invoices.id"), nullable=True)
    
    amount = Column(Float)
    currency = Column(String(3), default="NGN")
    payment_method = Column(String(50))  # stripe, paga, bank_transfer
    transaction_id = Column(String(100), nullable=True)
    status = Column(Enum(PaymentStatus), default=PaymentStatus.PENDING)
    
    paid_at = Column(DateTime(timezone=True), nullable=True)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    invoice = relationship("Invoice", back_populates="payments")
