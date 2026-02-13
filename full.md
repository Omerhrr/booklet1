# Booklet - Multi-Tenant SaaS ERP Platform
## Comprehensive Production-Ready Architecture & Implementation Plan

**Product Name:** Booklet
**Company:** Planex (Planexis) Solutions
**Version:** 2.0 - Production Ready Specification
**Last Updated:** 2026-02-13
**Status:** Planning Phase

---

## Executive Summary

Booklet is a comprehensive, multi-tenant SaaS ERP platform designed to serve businesses of all sizes with enterprise-grade accounting, inventory, HR, and business intelligence capabilities. This document outlines the complete architecture, features, and implementation roadmap for transforming Booklet into a production-ready, commercially viable SaaS product.

### Key Differentiators
- **True Multi-Tenancy:** Isolated data with scalable architecture
- **AI-Powered Insights:** Built-in business intelligence with natural language queries
- **Modular Design:** Pay for what you need pricing model
- **Enterprise Ready:** SOC 2, GDPR compliant architecture
- **Seamless Integration:** RESTful API with webhooks and third-party connectors

---

## Table of Contents

1. [Product Overview](#product-overview)
2. [Technology Stack](#technology-stack)
3. [Multi-Tenancy Architecture](#multi-tenancy-architecture)
4. [Subscription & Billing Management](#subscription--billing-management)
5. [Core ERP Modules](#core-erp-modules)
6. [Security & Compliance](#security--compliance)
7. [Infrastructure & DevOps](#infrastructure--devops)
8. [API & Integrations](#api--integrations)
9. [Missing Features - Production Checklist](#missing-features---production-checklist)
10. [Implementation Roadmap](#implementation-roadmap)
11. [Monitoring & Analytics](#monitoring--analytics)
12. [Support & Maintenance](#support--maintenance)

---

## Product Overview

### Target Customers
- **Small Business (1-10 employees):** Basic accounting, invoicing, inventory
- **Medium Business (11-50 employees):** Multi-branch, advanced HR, reporting
- **Enterprise (50+ employees):** Multi-entity, custom workflows, API access

### Subscription Tiers

| Feature | Starter | Professional | Enterprise |
|---------|---------|--------------|------------|
| **Price** | $29/month | $99/month | $299/month |
| **Users** | 3 | 15 | Unlimited |
| **Branches** | 1 | 5 | Unlimited |
| **Transactions** | 500/month | 5,000/month | Unlimited |
| **AI Queries** | 50/month | 500/month | Unlimited |
| **Storage** | 5 GB | 50 GB | 500 GB |
| **Support** | Email | Priority Email | 24/7 Phone + Dedicated CSM |
| **Custom Branding** | - | Logo | Full white-label |
| **API Access** | - | Read-only | Full API + Webhooks |
| **SSO** | - | - | Included |
| **SLA** | 99.5% | 99.9% | 99.99% |

### Additional Modules (Add-ons)

| Module | Price | Description |
|--------|--------|-------------|
| **Payroll Plus** | $49/mo | Automatic tax filing, benefits administration |
| **Inventory Pro** | $39/mo | Batch tracking, warehouses, BOM, forecasting |
| **CRM Integration** | $29/mo | Sales pipeline, lead tracking, email automation |
| **E-commerce** | $79/mo | Online store, shopping cart, payment processing |
| **POS** | $59/mo | Point of Sale, barcode scanning, receipts |
| **Mobile Apps** | $9/user/mo | iOS/Android apps with offline mode |
| **Advanced Reporting** | $49/mo | Custom reports, scheduled exports, dashboards |
| **API Plus** | $99/mo | Higher rate limits, webhooks, premium support |

---

## Technology Stack

### Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────────┐
│                         CLIENT LAYER                                 │
├─────────────────────────────────────────────────────────────────────┤
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐  ┌───────────┐ │
│  │   Desktop   │  │   Mobile    │  │   Tablet    │  │   API     │ │
│  │   Browser   │  │   iOS/And   │  │   Browser   │  │  Clients  │ │
│  └──────┬──────┘  └──────┬──────┘  └──────┬──────┘  └─────┬─────┘ │
│         │                │                │                │       │
└─────────┼────────────────┼────────────────┼────────────────┼───────┘
          │                │                │                │
          ▼                ▼                ▼                ▼
┌─────────────────────────────────────────────────────────────────────┐
│                      FRONTEND LAYER                                 │
├─────────────────────────────────────────────────────────────────────┤
│  ┌──────────────────────────────────────────────────────────────┐  │
│  │  Flask + Jinja2 Templates                                     │  │
│  │  ┌──────────────────────────────────────────────────────┐    │  │
│  │  │ HTMX + Alpine.js for Dynamic Interactivity           │    │  │
│  │  │ Flowbite Components + Tailwind CSS                  │    │  │
│  │  │ ECharts for Data Visualization                      │    │  │
│  │  └──────────────────────────────────────────────────────┘    │  │
│  └──────────────────────────────────────────────────────────────┘  │
│  ┌──────────────────────────────────────────────────────────────┐  │
│  │  Static Assets (CDN)                                         │  │
│  │  - Tailwind CSS                                              │  │
│  │  - Alpine.js                                                 │  │
│  │  - HTMX                                                      │  │
│  │  - ECharts                                                   │  │
│  │  - Flowbite                                                  │  │
│  │  - Custom JS/CSS                                             │  │
│  └──────────────────────────────────────────────────────────────┘  │
└───────────────────────────┬─────────────────────────────────────────┘
                            │ REST API Calls
                            ▼
┌─────────────────────────────────────────────────────────────────────┐
│                      API GATEWAY LAYER                              │
├─────────────────────────────────────────────────────────────────────┤
│  ┌──────────────────────────────────────────────────────────────┐  │
│  │  FastAPI Backend Service                                    │  │
│  │  - RESTful API Endpoints                                     │  │
│  │  - WebSocket Support (real-time)                             │  │
│  │  - Request Validation & Rate Limiting                        │  │
│  │  - Authentication & Authorization                           │  │
│  └──────────────────────────────────────────────────────────────┘  │
└───────────────────────────┬─────────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────────────┐
│                      BUSINESS LOGIC LAYER                            │
├─────────────────────────────────────────────────────────────────────┤
│  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌─────────┐ │
│  │Accounting│ │ Inventory│ │   HR     │ │  Sales   │ │  AI/ML  │ │
│  │  Engine  │ │ Engine   │ │ & Payroll│ │ & CRM    │ │ Services│ │
│  └──────────┘ └──────────┘ └──────────┘ └──────────┘ └─────────┘ │
└───────────────────────────┬─────────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────────────┐
│                      DATA LAYER                                      │
├─────────────────────────────────────────────────────────────────────┤
│  ┌──────────────────────────────────────────────────────────────┐  │
│  │  PostgreSQL (Primary Database)                               │  │
│  │  - Multi-tenant schema isolation                             │  │
│  │  - Row-level security (RLS)                                  │  │
│  │  - Connection pooling                                        │  │
│  └──────────────────────────────────────────────────────────────┘  │
│  ┌───────────┐ ┌───────────┐ ┌───────────┐ ┌───────────┐          │
│  │  Redis    │ │ Elasticsearch│ │ ClickHouse │ │  S3/MinIO │          │
│  │  Cache    │ │  Search    │ │ Analytics  │ │  Storage  │          │
│  └───────────┘ └───────────┘ └───────────┘ └───────────┘          │
└─────────────────────────────────────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────────────┐
│                      INFRASTRUCTURE LAYER                             │
├─────────────────────────────────────────────────────────────────────┤
│  ┌──────────────────────────────────────────────────────────────┐  │
│  │  Container Orchestration (Kubernetes)                        │  │
│  │  - Auto-scaling                                               │  │
│  │  - Health checks & self-healing                               │  │
│  │  - Rolling deployments with zero downtime                     │  │
│  └──────────────────────────────────────────────────────────────┘  │
│  ┌──────────────────────────────────────────────────────────────┐  │
│  │  CI/CD Pipeline (GitHub Actions/GitLab CI)                   │  │
│  │  - Automated testing                                         │  │
│  │  - Security scanning                                         │  │
│  │  - Blue-green deployments                                    │  │
│  └──────────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────────┘
```

### Backend Stack

| Component | Technology | Purpose |
|-----------|-----------|---------|
| **API Framework** | FastAPI 0.110+ | High-performance async API |
| **Database ORM** | SQLAlchemy 2.0+ | Database abstraction, migrations |
| **Database Driver** | asyncpg (PostgreSQL) | Async database connectivity |
| **Authentication** | JWT + OAuth2 | Token-based auth, social login |
| **Password Hashing** | bcrypt/argon2 | Secure password storage |
| **API Documentation** | OpenAPI 3.1 (Swagger UI) | Auto-generated API docs | Redoc
| **Task Queue** | Celery + Redis | Background jobs, scheduled tasks |
| **Email** | FastAPI-Mail | Transactional emails |
| **File Storage** | MinIO/S3 | Document uploads, invoices |
| **Search** | Elasticsearch | Full-text search, analytics |
| **Caching** | Redis | Session cache, query cache |
| **Message Queue** | Redis/RabbitMQ | Async communication, webhooks |
| **Web Server** | Gunicorn + Uvicorn | Production WSGI/ASGI server |
| **Rate Limiting** | slowapi | API rate limiting |
| **Validation** | Pydantic v2 | Request/response validation |
| **AI/ML** | scikit-learn, NumPy | Analytics, forecasting |

### Frontend Stack

| Component | Technology | Purpose |
|-----------|-----------|---------|
| **Template Engine** | Flask + Jinja2 | Server-side rendering |
| **CSS Framework** | Tailwind CSS (CDN) | Utility-first styling |
| **UI Components** | Flowbite (CDN) | Pre-built UI components |
| **JavaScript Framework** | Alpine.js (CDN) | Reactive interactions |
| **Dynamic Updates** | HTMX (CDN) | AJAX without JavaScript |
| **Charts** | Apache ECharts (CDN) | Data visualization |
| **Icons** | Heroicons (SVG) | Icon set |
| **Form Validation** | HTMX + Alpine | Client-side validation |
| **PDF Generation** | WeasyPrint | Server-side PDF |
| **Excel Export** | openpyxl | Spreadsheet generation |
| **Rich Text Editor** | Trix/Quill | WYSIWYG editing |

### DevOps & Infrastructure

| Component | Technology | Purpose |
|-----------|-----------|---------|
| **Containerization** | Docker | Application containers |
| **Orchestration** | Kubernetes | Container management |
| **CI/CD** | GitHub Actions | Automated deployment |
| **Monitoring** | Prometheus + Grafana | Metrics, dashboards |
| **Logging** | ELK Stack (Elasticsearch, Logstash, Kibana) | Log aggregation |
| **APM** | Sentry | Error tracking, performance |
| **SSL/Termination** | NGINX/Traefik | Reverse proxy |
| **Load Balancing** | NGINX/HAProxy | Traffic distribution |
| **Database Backup** | WAL-G | PostgreSQL backups |
| **Secrets Management** | HashiCorp Vault | Secure secrets |
| **Infrastructure as Code** | Terraform | Cloud resource management |

---

## Multi-Tenancy Architecture

### Multi-Tenancy Strategy: Hybrid Approach

Booklet implements a **hybrid multi-tenancy** model balancing data isolation, performance, and cost efficiency:

```
┌─────────────────────────────────────────────────────────────────────┐
│                        APPLICATION LAYER                             │
│                    (Shared across all tenants)                       │
└─────────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────────┐
│                         DATABASE LAYER                                │
│  ┌──────────────────────────────────────────────────────────────┐  │
│  │  SHARED DATABASE (PostgreSQL)                                │  │
│  │  ┌────────────────────────────────────────────────────────┐ │  │
│  │  │ SCHEMA: public (shared metadata)                        │ │  │
│  │  │  - Tenants table                                        │ │  │
│  │  │  - Subscription plans                                  │ │  │
│  │  │  - System configuration                                │ │  │
│  │  └────────────────────────────────────────────────────────┘ │  │
│  │  ┌────────────────────────────────────────────────────────┐ │  │
│  │  │ SCHEMA: tenant_{tenant_id} (isolated per tenant)        │ │  │
│  │  │  - accounts, customers, products, etc.                  │ │  │
│  │  │  - Each tenant gets dedicated schema                    │ │  │
│  │  │  ┌─────────┐ ┌─────────┐ ┌─────────┐ ┌─────────┐       │ │  │
│  │  │  │Tenant 1 │ │Tenant 2 │ │Tenant 3 │ │Tenant N │       │ │  │
│  │  │  │ Schema  │ │ Schema  │ │ Schema  │ │ Schema  │       │ │  │
│  │  │  └─────────┘ └─────────┘ └─────────┘ └─────────┘       │ │  │
│  │  └────────────────────────────────────────────────────────┘ │  │
│  └──────────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────────┘
```

### Tenant Isolation Implementation

#### 1. Database Schema Design

```python
# SQL: Create tenant schema
CREATE SCHEMA tenant_{tenant_id};

# Each tenant schema contains identical table structure
# but completely isolated data

# Example: Query with tenant isolation
# Automatic schema injection via middleware
SET search_path TO tenant_{tenant_id}, public;
SELECT * FROM customers;
```

#### 2. Tenant Resolution Middleware

```python
# app/middleware/tenant.py

from fastapi import Request, HTTPException
from sqlalchemy.orm import Session

class TenantMiddleware:
    async def __call__(self, request: Request, call_next):
        # Extract tenant from subdomain or header
        tenant_id = self._extract_tenant(request)

        # Validate tenant exists and is active
        if not await self._validate_tenant(tenant_id):
            raise HTTPException(status_code=404, detail="Tenant not found")

        # Attach tenant to request state
        request.state.tenant_id = tenant_id

        # Set database schema for this request
        db: Session = request.state.db
        db.execute(f"SET search_path TO tenant_{tenant_id}, public")

        response = await call_next(request)
        return response

    def _extract_tenant(self, request: Request) -> str:
        # Subdomain approach: tenant.booklet.com
        host = request.headers.get("host", "")
        subdomain = host.split(".")[0]

        # OR Custom header approach
        # tenant_id = request.headers.get("X-Tenant-ID")

        return subdomain

    async def _validate_tenant(self, tenant_id: str) -> bool:
        # Check public.tenants table
        # Validate subscription is active
        # Check if subscription is not expired
        return True
```

#### 3. Tenant-Aware Database Session

```python
# app/database/tenant_aware.py

from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, scoped_session

class TenantAwareSessionFactory:
    def __init__(self, engine):
        self.engine = engine
        self.session_factory = sessionmaker(bind=engine)

    def get_session(self, tenant_id: str):
        session = self.session_factory()
        # Set schema path for this session
        session.execute(f"SET search_path TO tenant_{tenant_id}, public")
        return session

# Usage in route handlers
@app.get("/customers")
async def get_customers(request: Request, db: Session = Depends(get_db)):
    tenant_id = request.state.tenant_id
    # Query automatically uses tenant schema
    customers = db.query(Customer).all()
    return customers
```

#### 4. Tenant Model (public schema)

```python
# app/models/tenant.py

from sqlalchemy import Column, Integer, String, Boolean, DateTime, Enum
from sqlalchemy.sql import func
from datetime import datetime

class Tenant(Base):
    """Tenant/Business record (stored in public schema)"""
    __tablename__ = "tenants"
    __table_args__ = {"schema": "public"}

    id = Column(Integer, primary_key=True, index=True)
    subdomain = Column(String(50), unique=True, index=True, nullable=False)
    business_name = Column(String(255), nullable=False)

    # Subscription details
    subscription_tier = Column(Enum("starter", "professional", "enterprise",
                                     name="subscription_tier"),
                               default="starter")
    subscription_status = Column(Enum("active", "trial", "suspended", "cancelled",
                                      name="subscription_status"),
                                default="trial")
    trial_end_date = Column(DateTime, nullable=True)
    subscription_end_date = Column(DateTime, nullable=True)

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

    # Configuration
    is_vat_registered = Column(Boolean, default=False)
    vat_rate = Column(Float, default=0.0)
    base_currency = Column(String(3), default="USD")

    # Branding
    logo_url = Column(String(500), nullable=True)
    primary_color = Column(String(7), default="#3B82F6")  # Hex
    custom_domain = Column(String(100), unique=True, nullable=True)

    # Status
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships (to tenant-specific schema)
    # users, branches, customers, etc. in tenant_{id} schema
```

#### 5. Tenant Creation Workflow

```python
# app/services/tenant_service.py

class TenantCreationService:
    async def create_tenant(self, tenant_data: TenantCreate) -> Tenant:
        """Create new tenant with isolated schema"""

        # 1. Create tenant record in public schema
        tenant = Tenant(**tenant_data.dict())
        db.add(tenant)
        db.commit()
        db.refresh(tenant)

        # 2. Create dedicated schema for tenant
        db.execute(f"CREATE SCHEMA tenant_{tenant.id}")

        # 3. Create all tables in tenant schema
        # (using migration script or metadata.create_all)
        self._create_tenant_schema(tenant.id)

        # 4. Seed default data (accounts, roles, admin user)
        self._seed_tenant_data(tenant.id)

        # 5. Set up storage bucket
        self._create_storage_bucket(tenant.id)

        # 6. Configure DNS for custom subdomain
        self._configure_subdomain(tenant.subdomain)

        return tenant

    def _create_tenant_schema(self, tenant_id: int):
        """Create all tables in tenant-specific schema"""
        # Run Alembic migrations with schema override
        # or use Base.metadata.create_all() with schema param
        Base.metadata.create_all(
            bind=engine,
            tables=[Customer.__table__, Invoice.__table__, ...],
            schema=f"tenant_{tenant_id}"
        )
```

### Onboarding Flow

```
┌─────────────────────────────────────────────────────────────────┐
│  1. SIGN UP                                                      │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │  - Business Name                                          │   │
│  │  - Email                                                  │   │
│  │  - Password                                               │   │
│  │  - Subdomain (e.g., mycompany.booklet.com)                │   │
│  └─────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────┘
                          │
                          ▼
┌─────────────────────────────────────────────────────────────────┐
│  2. TIER SELECTION                                               │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │  ○ Starter ($29/mo) - 3 users, 1 branch                 │   │
│  │  ○ Professional ($99/mo) - 15 users, 5 branches         │   │
│  │  ○ Enterprise ($299/mo) - Unlimited users/branches      │   │
│  │  ○ Start 14-day free trial                               │   │
│  └─────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────┘
                          │
                          ▼
┌─────────────────────────────────────────────────────────────────┐
│  3. PAYMENT METHOD (if not trial)                               │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │  - Credit Card (Stripe)                                  │   │
│  │  - PayPal                                               │   │
│  │  - Bank Transfer (Enterprise)                           │   │
│  └─────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────┘
                          │
                          ▼
┌─────────────────────────────────────────────────────────────────┐
│  4. BUSINESS SETUP                                               │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │  - Industry                                              │   │
│  │  - Base Currency                                         │   │
│  │  - Fiscal Year Start                                    │   │
│  │  - VAT Registration                                     │   │
│  └─────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────┘
                          │
                          ▼
┌─────────────────────────────────────────────────────────────────┐
│  5. TENANT PROVISIONING (automated)                              │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │  ✓ Create tenant record                                  │   │
│  │  ✓ Create database schema                                │   │
│  │  ✓ Seed chart of accounts                                │   │
│  │  ✓ Create admin user                                     │   │
│  │  ✓ Configure DNS                                         │   │
│  │  ✓ Send welcome email                                    │   │
│  └─────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────┘
                          │
                          ▼
┌─────────────────────────────────────────────────────────────────┐
│  6. DATA IMPORT (Optional)                                      │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │  - Upload Excel/CSV                                      │   │
│  │  - Connect previous accounting software                  │   │
│  │  - AI-powered data mapping (Jarvis)                      │   │
│  └─────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────┘
                          │
                          ▼
┌─────────────────────────────────────────────────────────────────┐
│  7. WELCOME TO BOOKLET                                          │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │  [Access Dashboard]                                       │   │
│  │  [Watch Tutorial]                                         │   │
│  │  [Import Data]                                            │   │
│  │  [Invite Team]                                            │   │
│  └─────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────┘
```

---

## Subscription & Billing Management

### Billing System Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                      BILLING ENGINE                              │
├─────────────────────────────────────────────────────────────────┤
│  ┌───────────────────────────────────────────────────────────┐ │
│  │  Subscription Manager                                       │ │
│  │  - Plan tier management                                    │ │
│  │  - Trial period handling                                   │ │
│  │  - Plan changes (upgrade/downgrade)                        │ │
│  │  - Proration calculation                                   │ │
│  └───────────────────────────────────────────────────────────┘ │
│  ┌───────────────────────────────────────────────────────────┐ │
│  │  Usage Meter                                               │ │
│  │  - API call counting                                       │ │
│  │  - Transaction counting                                    │ │
│  │  - Storage usage tracking                                  │ │
│  │  - User counting                                           │ │
│  └───────────────────────────────────────────────────────────┘ │
│  ┌───────────────────────────────────────────────────────────┐ │
│  │  Invoice Generator                                         │ │
│  │  - Recurring invoices                                      │ │
│  │  - Usage-based charges                                    │ │
│  │  - PDF generation                                          │ │
│  │  - Payment reminders                                       │ │
│  └───────────────────────────────────────────────────────────┘ │
│  ┌───────────────────────────────────────────────────────────┐ │
│  │  Payment Gateway Integration                              │ │
│  │  - Stripe (Cards)                                         │ │
│  │  - PayPal                                                 │ │
│  │  - Bank Transfer (SEPA, ACH)                               │ │
│  │  - Multi-currency support                                 │ │
│  └───────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────────┘
```

### Database Models for Billing

```python
# app/models/billing.py (public schema)

class SubscriptionPlan(Base):
    """Subscription plan definitions"""
    __tablename__ = "subscription_plans"
    __table_args__ = {"schema": "public"}

    id = Column(Integer, primary_key=True)
    name = Column(String(50), unique=True)  # starter, professional, enterprise
    display_name = Column(String(100))
    description = Column(Text)
    monthly_price = Column(Decimal(10, 2))
    yearly_price = Column(Decimal(10, 2))  # with discount
    currency = Column(String(3), default="USD")

    # Limits
    max_users = Column(Integer)
    max_branches = Column(Integer)
    max_transactions_per_month = Column(Integer)
    max_storage_gb = Column(Integer)
    max_api_calls_per_month = Column(Integer)

    # Features (JSON array of feature strings)
    features = Column(JSON)

    # Add-on modules included
    included_modules = Column(JSON)

    is_active = Column(Boolean, default=True)


class TenantSubscription(Base):
    """Tenant's current subscription"""
    __tablename__ = "tenant_subscriptions"
    __table_args__ = {"schema": "public"}

    id = Column(Integer, primary_key=True)
    tenant_id = Column(Integer, ForeignKey("public.tenants.id"))

    plan_id = Column(Integer, ForeignKey("public.subscription_plans.id"))
    plan = relationship("SubscriptionPlan")

    status = Column(Enum("active", "trial", "past_due", "cancelled",
                         name="subscription_status"))

    # Billing cycle
    billing_cycle = Column(Enum("monthly", "yearly", name="billing_cycle"))
    current_period_start = Column(Date)
    current_period_end = Column(Date)

    # Trial
    is_trial = Column(Boolean, default=True)
    trial_end_date = Column(Date)

    # Payment method
    stripe_customer_id = Column(String(100), nullable=True)
    paypal_agreement_id = Column(String(100), nullable=True)
    default_payment_method = Column(String(50))  # stripe, paypal, bank_transfer

    # Cancelation
    cancel_at_period_end = Column(Boolean, default=False)
    canceled_at = Column(DateTime, nullable=True)


class UsageRecord(Base):
    """Usage tracking for billing"""
    __tablename__ = "usage_records"
    __table_args__ = {"schema": "public"}

    id = Column(Integer, primary_key=True)
    tenant_id = Column(Integer, ForeignKey("public.tenants.id"))
    record_date = Column(Date, index=True)

    # Usage metrics
    transaction_count = Column(Integer, default=0)
    api_call_count = Column(Integer, default=0)
    storage_used_gb = Column(Float, default=0.0)
    user_count = Column(Integer, default=0)
    ai_query_count = Column(Integer, default=0)

    # Computed at end of month
    has_exceeded_limits = Column(Boolean, default=False)


class Invoice(Base):
    """Billing invoices"""
    __tablename__ = "invoices"
    __table_args__ = {"schema": "public"}

    id = Column(Integer, primary_key=True)
    tenant_id = Column(Integer, ForeignKey("public.tenants.id"))
    invoice_number = Column(String(50), unique=True)
    invoice_date = Column(Date)
    due_date = Column(Date)

    status = Column(Enum("draft", "sent", "paid", "past_due", "void",
                         name="invoice_status"))

    # Amounts
    subtotal = Column(Decimal(10, 2))
    tax_amount = Column(Decimal(10, 2), default=0)
    discount_amount = Column(Decimal(10, 2), default=0)
    total_amount = Column(Decimal(10, 2))
    currency = Column(String(3), default="USD")

    # Payment
    paid_date = Column(Date, nullable=True)
    payment_method = Column(String(50), nullable=True)
    transaction_id = Column(String(100), nullable=True)

    # External references
    stripe_invoice_id = Column(String(100), nullable=True)
    paypal_invoice_id = Column(String(100), nullable=True)

    # PDF
    pdf_url = Column(String(500), nullable=True)


class InvoiceLineItem(Base):
    """Invoice line items"""
    __tablename__ = "invoice_line_items"
    __table_args__ = {"schema": "public"}

    id = Column(Integer, primary_key=True)
    invoice_id = Column(Integer, ForeignKey("public.invoices.id"))

    description = Column(String(255))
    quantity = Column(Integer, default=1)
    unit_price = Column(Decimal(10, 2))
    amount = Column(Decimal(10, 2))

    # Type of charge
    item_type = Column(Enum("base_plan", "addon", "usage_overage",
                             "discount", "setup_fee", name="line_item_type"))

    # Reference to specific resource
    resource_id = Column(Integer, nullable=True)


class PaymentMethod(Base):
    """Stored payment methods"""
    __tablename__ = "payment_methods"
    __table_args__ = {"schema": "public"}

    id = Column(Integer, primary_key=True)
    tenant_id = Column(Integer, ForeignKey("public.tenants.id"))

    method_type = Column(Enum("credit_card", "debit_card", "paypal",
                             "bank_transfer", name="payment_method_type"))

    # For cards
    last_four = Column(String(4))
    card_brand = Column(String(20))  # visa, mastercard, amex
    expiry_month = Column(Integer)
    expiry_year = Column(Integer)

    # For Stripe/PayPal tokens
    stripe_payment_method_id = Column(String(100), nullable=True)
    paypal_token_id = Column(String(100), nullable=True)

    is_default = Column(Boolean, default=False)
    is_valid = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())


class AddOnSubscription(Base):
    """Add-on module subscriptions"""
    __tablename__ = "addon_subscriptions"
    __table_args__ = {"schema": "public"}

    id = Column(Integer, primary_key=True)
    tenant_id = Column(Integer, ForeignKey("public.tenants.id"))
    addon_id = Column(Integer, ForeignKey("public.addons.id"))

    status = Column(Enum("active", "inactive", "cancelled",
                         name="addon_status"))

    quantity = Column(Integer, default=1)  # For per-user addons

    monthly_price = Column(Decimal(10, 2))
    billing_cycle = Column(Enum("monthly", "yearly", name="billing_cycle"))

    current_period_start = Column(Date)
    current_period_end = Column(Date)
```

### Billing Workflows

#### 1. Subscription Creation (New Tenant)

```python
# app/services/billing/subscription_service.py

class SubscriptionService:
    async def create_subscription(
        self,
        tenant_id: int,
        plan_id: int,
        billing_cycle: str,
        payment_method_details: dict,
        trial_days: int = 14
    ) -> TenantSubscription:
        """Create new subscription with trial"""

        # Get plan
        plan = db.query(SubscriptionPlan).get(plan_id)

        # Calculate trial end date
        trial_end = datetime.now() + timedelta(days=trial_days)

        # Create payment method in Stripe
        stripe_customer = self._create_stripe_customer(
            tenant_id, payment_method_details
        )

        # Create subscription record
        subscription = TenantSubscription(
            tenant_id=tenant_id,
            plan_id=plan_id,
            status="trial",
            billing_cycle=billing_cycle,
            is_trial=True,
            trial_end_date=trial_end,
            current_period_start=datetime.now(),
            current_period_end=trial_end,
            stripe_customer_id=stripe_customer.id
        )
        db.add(subscription)
        db.commit()

        # Schedule trial-end notification
        await self._schedule_trial_end_notification(tenant_id, trial_end)

        return subscription
```

#### 2. Usage Metering & Enforcement

```python
# app/services/billing/usage_middleware.py

class UsageEnforcementMiddleware:
    """Enforce usage limits at API level"""

    async def check_transaction_limit(self, request: Request, tenant_id: int):
        """Check if tenant has exceeded transaction limit"""

        tenant = db.query(Tenant).get(tenant_id)
        subscription = tenant.subscription

        # Get plan limits
        plan = subscription.plan
        max_transactions = plan.max_transactions_per_month

        # Get current month usage
        now = datetime.now()
        current_month_usage = db.query(UsageRecord).filter(
            UsageRecord.tenant_id == tenant_id,
            UsageRecord.record_date >= now.replace(day=1)
        ).first()

        if current_month_usage and current_month_usage.transaction_count >= max_transactions:
            raise HTTPException(
                status_code=429,
                detail=f"Transaction limit exceeded. Upgrade plan for more."
            )

    async def record_usage(self, tenant_id: int, metric: str, count: int = 1):
        """Record usage for billing"""

        today = datetime.now().date()
        usage = db.query(UsageRecord).filter(
            UsageRecord.tenant_id == tenant_id,
            UsageRecord.record_date == today
        ).first()

        if not usage:
            usage = UsageRecord(tenant_id=tenant_id, record_date=today)
            db.add(usage)

        setattr(usage, f"{metric}_count",
               getattr(usage, f"{metric}_count") + count)

        # Check if limits exceeded
        self._check_and_notify_overages(usage)
        db.commit()
```

#### 3. Invoice Generation (Recurring)

```python
# app/services/billing/invoice_service.py

class InvoiceGenerationService:
    async def generate_monthly_invoices(self):
        """Scheduled task: Generate invoices for all active subscriptions"""

        # Get subscriptions due for billing
        today = datetime.now().date()
        due_subscriptions = db.query(TenantSubscription).filter(
            TenantSubscription.current_period_end == today,
            TenantSubscription.status.in_(["active", "trial"])
        ).all()

        for subscription in due_subscriptions:
            await self._generate_invoice(subscription)

    async def _generate_invoice(self, subscription: TenantSubscription):
        """Generate invoice for single subscription"""

        # Create invoice record
        invoice = Invoice(
            tenant_id=subscription.tenant_id,
            invoice_number=self._generate_invoice_number(),
            invoice_date=datetime.now().date(),
            due_date=datetime.now().date() + timedelta(days=7),
            status="draft",
            currency="USD"
        )

        # Add base plan line item
        plan = subscription.plan
        price = plan.monthly_price if subscription.billing_cycle == "monthly" else plan.yearly_price

        line_item = InvoiceLineItem(
            invoice=invoice,
            description=f"{plan.display_name} - {subscription.billing_cycle}",
            quantity=1,
            unit_price=price,
            amount=price,
            item_type="base_plan"
        )

        # Add add-on line items
        for addon in subscription.addons:
            InvoiceLineItem(
                invoice=invoice,
                description=addon.addon.display_name,
                quantity=addon.quantity,
                unit_price=addon.monthly_price,
                amount=addon.monthly_price * addon.quantity,
                item_type="addon"
            )

        # Add usage overage charges
        overage_charge = await self._calculate_overage(subscription)
        if overage_charge > 0:
            InvoiceLineItem(
                invoice=invoice,
                description="Usage overage",
                quantity=1,
                unit_price=overage_charge,
                amount=overage_charge,
                item_type="usage_overage"
            )

        # Calculate totals
        subtotal = sum(li.amount for li in invoice.line_items)
        invoice.subtotal = subtotal
        invoice.total_amount = subtotal  # Add tax calculation here

        # Send to Stripe for payment
        if subscription.default_payment_method == "stripe":
            stripe_invoice = await self._create_stripe_invoice(invoice, subscription)
            invoice.stripe_invoice_id = stripe_invoice.id

        invoice.status = "sent"
        db.add(invoice)
        db.commit()

        # Generate PDF
        await self._generate_invoice_pdf(invoice)

        # Send email notification
        await self._send_invoice_email(invoice)
```

#### 4. Payment Processing

```python
# app/services/billing/payment_service.py

class PaymentProcessingService:
    async def process_payment(self, invoice_id: int):
        """Process payment for invoice"""

        invoice = db.query(Invoice).get(invoice_id)

        if invoice.status == "paid":
            return {"status": "already_paid"}

        subscription = invoice.tenant.subscription

        # Process via Stripe
        if subscription.default_payment_method == "stripe":
            result = await self._process_stripe_payment(invoice, subscription)

        # Process via PayPal
        elif subscription.default_payment_method == "paypal":
            result = await self._process_paypal_payment(invoice, subscription)

        # Update invoice status
        if result["status"] == "success":
            invoice.status = "paid"
            invoice.paid_date = datetime.now().date()
            invoice.payment_method = subscription.default_payment_method
            invoice.transaction_id = result["transaction_id"]
            db.commit()

            # Extend subscription period
            await self._extend_subscription_period(subscription)

        return result

    async def _process_stripe_payment(self, invoice, subscription):
        """Process payment via Stripe"""

        try:
            # Create payment intent
            intent = stripe.PaymentIntent.create(
                amount=int(invoice.total_amount * 100),  # cents
                currency=invoice.currency.lower(),
                customer=subscription.stripe_customer_id,
                metadata={"invoice_id": invoice.id}
            )

            # Confirm payment (using saved payment method)
            intent = stripe.PaymentIntent.confirm(
                intent.id,
                payment_method=subscription.default_payment_method_id
            )

            if intent.status == "succeeded":
                return {
                    "status": "success",
                    "transaction_id": intent.id
                }
            else:
                return {"status": "failed", "error": intent.last_payment_error}

        except stripe.error.CardError as e:
            return {"status": "failed", "error": str(e)}
```

### Add-On Module System

```python
# app/models/billing/addons.py

class AddOn(Base):
    """Available add-on modules"""
    __tablename__ = "addons"
    __table_args__ = {"schema": "public"}

    id = Column(Integer, primary_key=True)
    code = Column(String(50), unique=True)  # payroll_plus, inventory_pro
    display_name = Column(String(100))
    description = Column(Text)

    monthly_price = Column(Decimal(10, 2))
    yearly_price = Column(Decimal(10, 2))

    # Pricing model
    pricing_model = Column(Enum("flat", "per_user", "per_transaction",
                               "per_storage_gb", name="pricing_model"))

    # Feature flags (enables features in tenant schema)
    feature_flags = Column(JSON)  # ["payroll_auto_tax", "benefits_admin"]

    is_active = Column(Boolean, default=True)


class TenantAddOn(Base):
    """Tenant's add-on subscriptions"""
    __tablename__ = "tenant_addons"
    __table_args__ = {"schema": "public"}

    id = Column(Integer, primary_key=True)
    tenant_id = Column(Integer, ForeignKey("public.tenants.id"))
    addon_id = Column(Integer, ForeignKey("public.addons.id"))

    status = Column(Enum("active", "cancelled", name="addon_status"))

    # Quantity (for per-user/per-unit pricing)
    quantity = Column(Integer, default=1)

    billing_cycle = Column(Enum("monthly", "yearly", name="billing_cycle"))

    current_period_start = Column(Date)
    current_period_end = Column(Date)

    # Feature activation
    activated_features = Column(JSON)  # Track which features are enabled
```

### Subscription Self-Service Portal

```
┌─────────────────────────────────────────────────────────────────┐
│  SUBSCRIPTION MANAGEMENT PORTAL                                 │
├─────────────────────────────────────────────────────────────────┤
│  ┌───────────────────────────────────────────────────────────┐  │
│  │  Current Plan                                              │  │
│  │  ┌─────────────────────────────────────────────────────┐  │  │
│  │  │  Professional Plan - $99/month                      │  │  │
│  │  │  15 users | 5 branches | 5,000 transactions          │  │  │
│  │  │  [View Details] [Change Plan]                        │  │  │
│  │  └─────────────────────────────────────────────────────┘  │  │
│  │  Next billing date: March 15, 2026                         │  │
│  └───────────────────────────────────────────────────────────┘  │
│                                                                  │
│  ┌───────────────────────────────────────────────────────────┐  │
│  │  Usage This Month                                          │  │
│  │  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐       │  │
│  │  │ Users    │ │Branches  │ │Trans.    │ │Storage   │       │  │
│  │  │ 8 / 15   │ │ 2 / 5    │ │ 1,234    │ │ 12 GB    │       │  │
│  │  │ ████████░ │ │ ████████░ │ │ █████░░░░ │ │ ██████░░░ │       │  │
│  │  └──────────┘ └──────────┘ └──────────┘ └──────────┘       │  │
│  └───────────────────────────────────────────────────────────┘  │
│                                                                  │
│  ┌───────────────────────────────────────────────────────────┐  │
│  │  Active Add-ons                                            │  │
│  │  ┌─────────────────────────────────────────────────────┐  │  │
│  │  │ ✓ Payroll Plus - $49/mo      [Manage] [Cancel]       │  │  │
│  │  │ ✓ Inventory Pro - $39/mo     [Manage] [Cancel]        │  │  │
│  │  │ + CRM Integration - $29/mo   [Add]                    │  │  │
│  │  │ + E-commerce - $79/mo        [Add]                    │  │  │
│  │  └─────────────────────────────────────────────────────┘  │  │
│  └───────────────────────────────────────────────────────────┘  │
│                                                                  │
│  ┌───────────────────────────────────────────────────────────┐  │
│  │  Payment Method                                            │  │
│  │  ┌─────────────────────────────────────────────────────┐  │  │
│  │  │ Visa ending in 4242              Expires 12/27        │  │  │
│  │  │ [Update Payment Method]                              │  │  │
│  │  └─────────────────────────────────────────────────────┘  │  │
│  └───────────────────────────────────────────────────────────┘  │
│                                                                  │
│  ┌───────────────────────────────────────────────────────────┐  │
│  │  Billing History                                           │  │
│  │  ┌─────────────────────────────────────────────────────┐  │  │
│  │  │ Invoice #INV-2026-02  | Feb 15, 2026  | $147.00  Paid│  │  │
│  │  │ Invoice #INV-2026-01  | Jan 15, 2026  | $147.00  Paid│  │  │
│  │  │ Invoice #INV-2025-12  | Dec 15, 2025  | $147.00  Paid│  │  │
│  │  │ [View All Invoices]                                   │  │  │
│  │  └─────────────────────────────────────────────────────┘  │  │
│  └───────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────┘
```

---

## Core ERP Modules

### Module Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                    BOOKLET ERP MODULES                           │
├─────────────────────────────────────────────────────────────────┤
│  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐           │
│  │ACCOUNTING│ │INVENTORY │ │    HR    │ │   SALES  │           │
│  │          │ │          │ │& PAYROLL │ │   & CRM  │           │
│  └──────────┘ └──────────┘ └──────────┘ └──────────┘           │
│  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐           │
│  │PURCHASING│ │ REPORTING│ │  BANKING │ │   FIXED  │           │
│  │          │ │ANALYTICS │ │          │ │ ASSETS   │           │
│  └──────────┘ └──────────┘ └──────────┘ └──────────┘           │
│  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐           │
│  │   AI/ML  │ │  E-COMM  │ │   POS    │ │PROJECTS  │           │
│  │ JARVIS   │ │  STORE   │ │          │ │ & TIME   │           │
│  └──────────┘ └──────────┘ └──────────┘ └──────────┘           │
└─────────────────────────────────────────────────────────────────┘
```

### 1. Accounting Module

**Features:**
- Double-entry bookkeeping with auto-balancing
- Multi-currency with real-time exchange rates
- Chart of Accounts with templates by industry
- General Ledger with drill-down to source documents
- Journal Vouchers with approval workflow
- Automatic depreciation posting
- Bank reconciliation with statement import
- Financial statements (P&L, Balance Sheet, Cash Flow)
- Trial Balance with audit trail
- Tax reports (VAT, GST, Sales Tax)
- Year-end closing with retained earnings
- Inter-company transactions (multi-entity)

**Key Tables:**
- accounts (chart of accounts)
- journal_vouchers
- ledger_entries
- bank_reconciliations
- tax_rates
- tax_filing_periods

### 2. Inventory & Warehouse Module

**Features:**
- Multi-warehouse support
- Product variants (size, color, attributes)
- Batch/Lot tracking with expiry
- Serial number tracking
- Barcoding & QR codes
- Stock transfers between warehouses
- Reorder point automation
- Purchase order suggestions
- Bin location management
- Physical inventory counting
- Stock valuation methods (FIFO, LIFO, Weighted Average)
- Bill of Materials (BOM)
- Assembly & production
- Kit sets
- Inventory forecasting with AI

**Key Tables:**
- products
- product_variants
- warehouses
- bin_locations
- stock_movements
- batches
- serial_numbers
- stock_counts
- bill_of_materials

### 3. Sales & CRM Module

**Features:**
- Lead & opportunity management
- Sales pipeline stages
- Contact management (customers, prospects)
- Quote & estimate generation
- Sales orders with backorder handling
- Invoice generation from sales orders
- Credit notes & returns
- Payment processing (Stripe, PayPal)
- Payment terms & aging
- Sales territory management
- Commission tracking
- Customer portal (order history, invoices)
- Recurring invoices
- Pro-forma invoices
- Sales analytics & forecasting

**Key Tables:**
- customers
- leads
- opportunities
- quotes
- sales_orders
- sales_invoices
- credit_notes
- payments_received
- sales_territories

### 4. Purchasing & Vendor Management

**Features:**
- Vendor/supplier management
- Purchase requisitions
- Purchase orders
- Goods received notes (GRN)
- Vendor bills & debit notes
- Vendor payment terms
- RFQ (Request for Quote)
- Vendor comparison
- Vendor rating system
- Purchase returns
- Three-way matching (PO, GRN, Invoice)
- Vendor portal
- AP aging & payment optimization
- Vendor analytics

**Key Tables:**
- vendors
- purchase_requisitions
- purchase_orders
- goods_received_notes
- purchase_bills
- debit_notes
- vendor_ratings

### 5. HR & Payroll Module

**Features:**
- Employee records with documents
- Organizational chart
- Department & job title management
- Attendance tracking
- Leave management (PTO, sick, etc.)
- Timesheet management
- Payroll processing (weekly, bi-weekly, monthly)
- Pay stubs with PDF export
- Tax calculations (PAYE, withholding)
- Benefits administration
- Pension calculations
- Deductions & additions
- Year-end tax forms (W-2, T4, P60)
- Direct deposit
- Payroll liability management
- Overtime & holiday pay
- Commission & bonus tracking

**Key Tables:**
- employees
- departments
- attendance_records
- leave_requests
- timesheets
- payroll_runs
- pay slips
- tax_codes
- benefits

### 6. Fixed Assets Module

**Features:**
- Asset register with categories
- Multiple depreciation methods (Straight-line, Declining Balance, Units of Production)
- Automatic depreciation calculation
- Asset disposal & write-off
- Asset revaluation
- Asset transfer between locations
- Maintenance tracking
- Insurance tracking
- Asset tagging
- Asset audit trail
- Impairment testing

**Key Tables:**
- fixed_assets
- depreciation_entries
- asset_disposals
- asset_categories
- asset_maintenance

### 7. Banking & Cash Management

**Features:**
- Multiple bank accounts & currencies
- Bank feeds (Open Banking API, Plaid)
- Automatic transaction import
- Bank reconciliation rules
- Fund transfers between accounts
- Cash flow forecasting
- Cash pool management
- Bank fees & interest tracking
- Check printing
- Positive pay
- Lockbox processing

**Key Tables:**
- bank_accounts
- bank_transactions
- bank_reconciliations
- fund_transfers
- checks

### 8. Reporting & Analytics Module

**Features:**
- Financial statements (P&L, BS, CF)
- Custom report builder
- Scheduled reports (email)
- Dashboard widgets
- Drill-down capabilities
- Comparison reports (period, branch)
- Aging reports (AR, AP)
- Sales analysis
- Inventory reports
- Purchase analysis
- Tax reports
- Export to Excel, PDF, CSV
- Real-time dashboards
- KPI tracking
- Trend analysis

**Key Tables:**
- saved_reports
- report_schedules
- dashboard_configs
- kpi_definitions

### 9. AI/ML Module (Jarvis)

**Features:**
- Natural language queries
- Anomaly detection in transactions
- Cash flow forecasting
- Sales prediction
- Inventory optimization
- Customer churn prediction
- Smart categorization
- Invoice OCR & data extraction
- Document understanding
- Automated bookkeeping suggestions
- Fraud detection
- Price optimization

**Key Tables:**
- ai_queries
- ai_models
- ml_predictions
- anomaly_alerts

### 10. Projects & Time Tracking Module (New)

**Features:**
- Project management
- Task tracking
- Time tracking with timer
- Billable vs non-billable hours
- Project budgets
- Resource allocation
- Gantt charts
- Milestone tracking
- Project profitability
- Progress invoicing
- Expense tracking per project
- Client project portal
- Resource utilization reports

**Key Tables:**
- projects
- tasks
- time_entries
- project_milestones
- project_budgets
- project_expenses

### 11. E-commerce Module (New)

**Features:**
- Online store builder
- Product catalog with images
- Shopping cart
- Checkout with payment processing
- Shipping calculator
- Tax calculation by jurisdiction
- Order management
- Inventory sync
- Customer accounts
- Wishlists
- Product reviews
- Coupon codes & discounts
- Abandoned cart recovery
- Multi-store support
- SEO tools
- Analytics integration

**Key Tables:**
- online_stores
- store_products
- store_orders
- shopping_carts
- coupons
- product_reviews

### 12. POS Module (New)

**Features:**
- Point of Sale interface
- Barcode scanning
- Receipt printing
- Cash drawer management
- Multiple payment methods
- Tip handling
- Refunds & returns
- Shift management
- Till reconciliation
- Customer display
- Offline mode with sync
- Table management (restaurants)
- Kitchen display
- Loyalty program integration

**Key Tables:**
- pos_registers
- pos_transactions
- pos_payments
- pos_shifts
- pos_tender_types

---

## Security & Compliance

### Security Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                    SECURITY LAYERS                              │
├─────────────────────────────────────────────────────────────────┤
│  ┌───────────────────────────────────────────────────────────┐  │
│  │  1. NETWORK SECURITY                                      │  │
│  │  - DDoS protection (Cloudflare, AWS Shield)              │  │
│  │  - Web Application Firewall (WAF)                         │  │
│  │  - TLS 1.3 encryption                                    │  │
│  │  - IP whitelisting (optional)                            │  │
│  └───────────────────────────────────────────────────────────┘  │
│  ┌───────────────────────────────────────────────────────────┐  │
│  │  2. APPLICATION SECURITY                                 │  │
│  │  - Input validation & sanitization                       │  │
│  │  - SQL injection prevention (ORM)                        │  │
│  │  - XSS protection                                        │  │
│  │  - CSRF tokens                                           │  │
│  │  - Rate limiting                                        │  │
│  │  - Secure headers (HSTS, CSP, etc.)                      │  │
│  └───────────────────────────────────────────────────────────┘  │
│  ┌───────────────────────────────────────────────────────────┐  │
│  │  3. AUTHENTICATION & AUTHORIZATION                        │  │
│  │  - Multi-factor authentication (MFA)                      │  │
│  │  - JWT with short expiration                             │  │
│  │  - Refresh tokens with rotation                          │  │
│  │  - Role-based access control (RBAC)                      │  │
│  │  - Attribute-based access control (ABAC)                 │  │
│  │  - Session management                                    │  │
│  │  - Password policies (complexity, rotation)              │  │
│  └───────────────────────────────────────────────────────────┘  │
│  ┌───────────────────────────────────────────────────────────┐  │
│  │  4. DATA SECURITY                                        │  │
│  │  - Encryption at rest (AES-256)                          │  │
│  │  - Encryption in transit (TLS)                          │  │
│  │  - Database row-level security (RLS)                     │  │
│  │  - Field-level encryption (PII)                          │  │
│  │  - Secure key management (HashiCorp Vault)              │  │
│  │  - Data masking in logs                                  │  │
│  │  - PII redaction                                        │  │
│  └───────────────────────────────────────────────────────────┘  │
│  ┌───────────────────────────────────────────────────────────┐  │
│  │  5. AUDIT & COMPLIANCE                                    │  │
│  │  - Comprehensive audit logging                           │  │
│  │  - Immutable logs (WORM storage)                         │  │
│  │  - Compliance reports (SOC 2, GDPR, HIPAA)               │  │
│  │  - Data retention policies                              │  │
│  │  - Right to be forgotten (GDPR)                          │  │
│  │  - Data export (Portability)                             │  │
│  │  - Penetration testing (quarterly)                       │  │
│  │  - Vulnerability scanning (continuous)                   │  │
│  └───────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────┘
```

### Security Features

#### 1. Multi-Factor Authentication (MFA)

```python
# app/services/auth/mfa.py

class TwoFactorAuthService:
    """Handle 2FA for user accounts"""

    async def enable_totp(self, user_id: int) -> dict:
        """Enable TOTP (Time-based One-Time Password)"""

        import pyotp

        # Generate secret
        secret = pyotp.random_base32()

        # Store encrypted secret
        encrypted_secret = encrypt_data(secret)
        mfa = UserMFA(
            user_id=user_id,
            method="totp",
            secret=encrypted_secret,
            is_enabled=False  # Not verified yet
        )
        db.add(mfa)
        db.commit()

        # Generate QR code URL
        totp = pyotp.TOTP(secret)
        qr_url = totp.provisioning_uri(
            name=user.email,
            issuer_name="Booklet"
        )

        return {"secret": secret, "qr_code_url": qr_url}

    async def verify_totp(self, user_id: int, token: str) -> bool:
        """Verify TOTP code"""

        mfa = db.query(UserMFA).filter(
            UserMFA.user_id == user_id,
            UserMFA.method == "totp"
        ).first()

        secret = decrypt_data(mfa.secret)
        totp = pyotp.TOTP(secret)

        if totp.verify(token, valid_window=1):
            mfa.is_enabled = True
            db.commit()
            return True
        return False

    async def send_sms_code(self, user_id: int, phone_number: str):
        """Send SMS verification code"""

        # Generate 6-digit code
        code = random.randint(100000, 999999)

        # Store with expiry
        mfa = UserMFA(
            user_id=user_id,
            method="sms",
            phone_number=phone_number,
            code=hash_code(code),
            expires_at=datetime.now() + timedelta(minutes=5)
        )
        db.add(mfa)
        db.commit()

        # Send SMS (Twilio, etc.)
        await sms_service.send(phone_number,
            f"Your Booklet verification code is: {code}")
```

#### 2. Audit Logging

```python
# app/models/audit.py (public schema)

class AuditLog(Base):
    """Comprehensive audit trail"""
    __tablename__ = "audit_logs"
    __table_args__ = {"schema": "public"}

    id = Column(BigInteger, primary_key=True)
    timestamp = Column(DateTime(timezone=True), server_default=func.now(), index=True)

    # Who
    tenant_id = Column(Integer, ForeignKey("public.tenants.id"), index=True)
    user_id = Column(Integer, index=True)
    user_email = Column(String(255))
    user_role = Column(String(100))

    # What
    action = Column(String(100), index=True)  # login, create, update, delete, export
    resource_type = Column(String(100))  # Customer, Invoice, etc.
    resource_id = Column(Integer, index=True)

    # Where
    ip_address = Column(String(45))  # IPv6 compatible
    user_agent = Column(String(500))
    geo_location = Column(JSON)  # {country, city, lat, lon}

    # Details
    changes = Column(JSON)  # Before/after values
    request_id = Column(String(100))  # Correlate multiple actions
    status = Column(String(50))  # success, failure

    # Metadata
    tags = Column(JSON)  # For filtering and alerts


# Middleware for automatic audit logging
@app.middleware("http")
async def audit_middleware(request: Request, call_next):
    """Log all HTTP requests"""

    # Skip static files and health checks
    if request.url.path in ["/health", "/metrics", "/static"]:
        return await call_next(request)

    user = getattr(request.state, "user", None)
    tenant_id = getattr(request.state, "tenant_id", None)

    start_time = time.time()
    response = await call_next(request)
    duration = time.time() - start_time

    # Log request
    if user and request.method in ["POST", "PUT", "DELETE", "GET"]:
        log_entry = AuditLog(
            tenant_id=tenant_id,
            user_id=user.id if user else None,
            user_email=user.email if user else None,
            action=f"{request.method.lower()}_{request.url.path.replace('/', '_')}",
            resource_type=request.url.path.split('/')[1] if len(request.url.path.split('/')) > 1 else None,
            ip_address=request.client.host,
            user_agent=request.headers.get("user-agent"),
            status="success" if response.status_code < 400 else "failure",
            tags={"status_code": response.status_code, "duration_ms": duration * 1000}
        )
        db.add(log_entry)
        db.commit()

    return response
```

#### 3. Role-Based Access Control (RBAC)

```python
# app/models/auth/permissions.py (public schema)

class Permission(Base):
    """Granular permissions"""
    __tablename__ = "permissions"
    __table_args__ = {"schema": "public"}

    id = Column(Integer, primary_key=True)
    name = Column(String(100), unique=True)  # customers:create
    display_name = Column(String(255))
    description = Column(Text)
    category = Column(String(50))  # Sales, Accounting, etc.

    # Hierarchy
    parent_id = Column(Integer, ForeignKey("permissions.id"), nullable=True)
    level = Column(Integer)  # 0=module, 1=action, 2=sub-action

    # Constraints
    requires_plan = Column(String(50))  # enterprise, pro
    is_system = Column(Boolean, default=False)


class Role(Base):
    """Roles aggregate permissions"""
    __tablename__ = "roles"
    __table_args__ = {"schema": "public"}

    id = Column(Integer, primary_key=True)
    tenant_id = Column(Integer, ForeignKey("public.tenants.id"))
    name = Column(String(100))
    description = Column(Text)

    # Type
    role_type = Column(Enum("system", "custom", "ai_generated", name="role_type"))
    is_system_role = Column(Boolean, default=False)

    # Permissions (many-to-many)
    permissions = relationship("Permission", secondary="role_permissions")


class UserRole(Base):
    """User role assignments per tenant"""
    __tablename__ = "user_roles"
    __table_args__ = {"schema": "public"}

    id = Column(Integer, primary_key=True)
    tenant_id = Column(Integer, ForeignKey("public.tenants.id"))
    user_id = Column(Integer, ForeignKey("tenant_{tenant_id}.users"))
    role_id = Column(Integer, ForeignKey("public.roles.id"))

    # Scope
    scope = Column(Enum("all", "branch", "department", "own", name="role_scope"))
    branch_id = Column(Integer, nullable=True)

    assigned_by = Column(Integer)  # user_id
    assigned_at = Column(DateTime(timezone=True), server_default=func.now())
    expires_at = Column(DateTime(timezone=True), nullable=True)


# Permission checker dependency
def require_permissions(*permissions: str):
    """Dependency factory for permission checking"""

    async def checker(
        request: Request,
        current_user: User = Depends(get_current_user),
        db: Session = Depends(get_db)
    ):
        tenant_id = request.state.tenant_id

        # Superusers bypass all checks
        if current_user.is_superuser:
            return current_user

        # Get user's permissions for this tenant
        user_permissions = await get_user_permissions(current_user.id, tenant_id, db)

        # Check all required permissions present
        required = set(permissions)
        if not required.issubset(user_permissions):
            raise HTTPException(
                status_code=403,
                detail=f"Missing required permissions: {', '.join(required - user_permissions)}"
            )

        return current_user

    return Depends(checker)


# Usage in routes
@app.post("/customers")
@require_permissions("customers:create")
async def create_customer(
    customer_data: CustomerCreate,
    db: Session = Depends(get_db),
    user: User = Depends(require_permissions("customers:create"))
):
    # Create customer
    pass
```

#### 4. Data Encryption

```python
# app/services/security/encryption.py

from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2
import os

class EncryptionService:
    """Handle encryption for sensitive data"""

    def __init__(self):
        # Master key from environment or Vault
        master_key = os.getenv("ENCRYPTION_MASTER_KEY")
        if not master_key:
            raise ValueError("ENCRYPTION_MASTER_KEY not set")

        self.cipher = Fernet(master_key.encode())

    def encrypt(self, plaintext: str) -> str:
        """Encrypt plaintext"""
        if not plaintext:
            return None
        encrypted = self.cipher.encrypt(plaintext.encode())
        return encrypted.decode()

    def decrypt(self, ciphertext: str) -> str:
        """Decrypt ciphertext"""
        if not ciphertext:
            return None
        decrypted = self.cipher.decrypt(ciphertext.encode())
        return decrypted.decode()

    def encrypt_pii_fields(self, model_dict: dict, pii_fields: list) -> dict:
        """Encrypt PII fields before saving"""
        for field in pii_fields:
            if field in model_dict and model_dict[field]:
                model_dict[field] = self.encrypt(model_dict[field])
        return model_dict


# Usage in models
class Customer(Base):
    __tablename__ = "customers"
    __table_args__ = {"schema": "tenant_{tenant_id}"}

    id = Column(Integer, primary_key=True)
    name = Column(String(255))  # Business name (not PII)
    contact_person = Column(String(255))  # PII - encrypted
    email = Column(String(255))  # PII - encrypted
    phone = Column(String(50))  # PII - encrypted
    tax_id = Column(String(50))  # PII - encrypted
    address = Column(Text)  # PII - encrypted
    credit_card_number = Column(String(100))  # PII - encrypted (PCI DSS)
```

#### 5. Rate Limiting

```python
# app/middleware/rate_limit.py

from slowapi import Limiter
from slowapi.util import get_remote_address

limiter = Limiter(
    key_func=get_remote_address,
    storage_uri="redis://localhost:6379",
    default_limits=["200/hour"]
)

# Apply to routes
@app.post("/api/auth/login")
@limiter.limit("5/minute")  # Strict limit for login
async def login(credentials: Credentials):
    pass

@app.get("/api/customers")
@limiter.limit("60/minute")  # Standard API rate
async def list_customers():
    pass

# Tenant-level rate limiting
def get_tenant_rate_limit(request: Request):
    """Get rate limit based on tenant subscription"""
    tenant_id = request.state.tenant_id
    tenant = db.query(Tenant).get(tenant_id)

    plan_limits = {
        "starter": "100/hour",
        "professional": "1000/hour",
        "enterprise": "10000/hour"
    }

    return f"tenant_{tenant_id}:{plan_limits.get(tenant.subscription_tier, '100/hour')}"
```

### Compliance Requirements

#### SOC 2 Type II Compliance

**Required Controls:**
- Access controls (authentication, authorization)
- Change management (version control, approvals)
- Data backup & recovery
- Incident response procedures
- Security monitoring & logging
- Vendor management
- Risk assessment
- Penetration testing (quarterly)
- Vulnerability scanning (continuous)

**Implementation:**
```
SOC 2 Controls
├── Access Control
│   ├── MFA for all users
│   ├── RBAC with least privilege
│   ├── Session timeout (30 min)
│   ├── Password policies (12+ chars, complexity)
│   └── Access reviews (quarterly)
├── Data Protection
│   ├── Encryption at rest (AES-256)
│   ├── Encryption in transit (TLS 1.3)
│   ├── PII encryption
│   ├── Data loss prevention (DLP)
│   └── Backup encryption
├── Monitoring
│   ├── SIEM integration (Splunk, ELK)
│   ├── Alert thresholds
│   ├── Log retention (90 days minimum)
│   ├── Intrusion detection (IDS)
│   └── UBA (User Behavior Analytics)
└── Incident Response
    ├── 24/7 security team
    ├── Incident escalation matrix
    ├── Automated containment
    ├── Forensic analysis
    └── Post-incident review
```

#### GDPR Compliance

**Required Features:**
- Lawful basis for processing
- Data minimization
- Right to access (data export)
- Right to be forgotten (data deletion)
- Right to rectification
- Right to portability
- Right to object
- Data protection by design & default
- Data breach notification (72 hours)
- Data Protection Officer (DPO) designation
- Data processing agreements (DPA)
- Privacy by design

**Implementation:**
```python
# app/services/gdpr.py

class GDPRService:
    """GDPR compliance helper"""

    async def export_user_data(self, user_id: int) -> dict:
        """Right to data portability"""

        # Collect all user data
        user = db.query(User).get(user_id)
        customers = db.query(Customer).filter(Customer.created_by == user_id).all()
        invoices = db.query(Invoice).filter(Invoice.created_by == user_id).all()
        # ... all other data

        return {
            "personal_data": user.to_dict(),
            "created_customers": [c.to_dict() for c in customers],
            "created_invoices": [i.to_dict() for i in invoices],
            "audit_logs": [log.to_dict() for log in user.audit_logs],
            "export_date": datetime.now().isoformat()
        }

    async def anonymize_user(self, user_id: int):
        """Right to be forgotten"""

        # Anonymize instead of delete (keep audit trail)
        user = db.query(User).get(user_id)
        user.email = f"deleted_{user_id}@anonymized.local"
        user.username = f"deleted_user_{user_id}"
        user.first_name = None
        user.last_name = None
        user.phone_number = None
        user.address = None
        user.is_deleted = True
        user.deleted_at = datetime.now()
        db.commit()

        # Anonymize related personal data
        await self._anonymize_customers(user_id)
        await self._anonymize_vendors(user_id)

    async def record_consent(self, user_id: int, consent_type: str):
        """Record consent for processing"""

        consent = ConsentLog(
            user_id=user_id,
            consent_type=consent_type,  # marketing, analytics, essential
            granted=True,
            granted_at=datetime.now(),
            ip_address=request.client.host,
            user_agent=request.headers.get("user-agent")
        )
        db.add(consent)
        db.commit()
```

#### HIPAA Compliance (for healthcare module)

**Requirements:**
- BAA (Business Associate Agreement) with all vendors
- PHI (Protected Health Information) encryption
- Access controls (minimum necessary)
- Audit logging (all access to PHI)
- Business continuity planning
- workforce training
- breach notification (60 days)

---

## Infrastructure & DevOps

### Production Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                     LOAD BALANCER (NGINX)                        │
│                   (SSL Termination, WAF)                         │
└──────────────────────────────┬──────────────────────────────────┘
                               │
                ┌──────────────┴──────────────┐
                │                             │
                ▼                             ▼
┌───────────────────────┐       ┌───────────────────────┐
│  WEB SERVER POD 1      │       │  WEB SERVER POD 2      │
│  ┌─────────────────┐   │       │  ┌─────────────────┐   │
│  │  Flask + HTMX   │   │       │  │  Flask + HTMX   │   │
│  │  (Frontend)     │   │       │  │  (Frontend)     │   │
│  └─────────────────┘   │       │  └─────────────────┘   │
│  ┌─────────────────┐   │       │  ┌─────────────────┐   │
│  │  FastAPI        │   │       │  │  FastAPI        │   │
│  │  (Backend API)  │   │       │  │  (Backend API)  │   │
│  └─────────────────┘   │       │  └─────────────────┘   │
└───────────┬───────────┘       └───────────┬───────────────┘
            │                               │
            └───────────────┬───────────────┘
                            │
                ┌───────────┴───────────┐
                │                       │
                ▼                       ▼
┌───────────────────────┐   ┌───────────────────────┐
│  POSTGRES PRIMARY     │   │  POSTGRES REPLICA      │
│  (Master - Write)      │   │  (Read - Scaled)       │
└───────────┬───────────┘   └───────────────────────┘
            │
            ▼
┌───────────────────────┐       ┌───────────────────────┐
│  REDIS CLUSTER        │       │  RABBITMQ / KAFKA     │
│  (Cache, Session)     │       │  (Message Queue)       │
└───────────────────────┘       └───────────────────────┘
            │
            ▼
┌─────────────────────────────────────────────────────────────────┐
│  STORAGE & SERVICES                                               │
│  ┌─────────┐ ┌─────────┐ ┌─────────┐ ┌─────────┐ ┌──────────┐   │
│  │S3/MinIO │ │   S3    │ │Elastic  │ │Prometheus│ │  Sentry  │   │
│  │(Files)  │ │(Backups)│ │Search   │ │+Grafana │ │ (Errors) │   │
│  └─────────┘ └─────────┘ └─────────┘ └─────────┘ └──────────┘   │
└─────────────────────────────────────────────────────────────────┘
```

### Docker Configuration

```dockerfile
# Dockerfile (Multi-stage build)

# Stage 1: Builder
FROM python:3.11-slim as builder

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt .
RUN pip install --user --no-cache-dir -r requirements.txt

# Stage 2: Runtime
FROM python:3.11-slim

WORKDIR /app

# Create non-root user
RUN useradd -m -u 1000 appuser

# Copy Python packages from builder
COPY --from=builder /root/.local /home/appuser/.local

# Copy application code
COPY --chown=appuser:appuser . .

# Install static files
COPY --chown=appuser:appuser app/static /app/app/static
COPY --chown=appuser:appuser app/templates /app/app/templates

# Set PATH
ENV PATH=/home/appuser/.local/bin:$PATH

# Switch to non-root user
USER appuser

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import requests; requests.get('http://localhost:8000/health')"

# Expose port
EXPOSE 8000

# Run application
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "4"]
```

```yaml
# docker-compose.yml (Development)

version: '3.8'

services:
  app:
    build:
      context: .
      dockerfile: Dockerfile
    ports:
      - "8000:8000"
    environment:
      - DATABASE_URL=postgresql://booklet:booklet_pass@db:5432/booklet
      - REDIS_URL=redis://redis:6379
    depends_on:
      - db
      - redis
    volumes:
      - ./app:/app/app
      - static_files:/app/app/static
      - uploaded_files:/app/uploads

  db:
    image: postgres:15-alpine
    environment:
      - POSTGRES_USER=booklet
      - POSTGRES_PASSWORD=booklet_pass
      - POSTGRES_DB=booklet
    volumes:
      - postgres_data:/var/lib/postgresql/data
      - ./init.sql:/docker-entrypoint-initdb.d/init.sql
    ports:
      - "5432:5432"

  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"
    volumes:
      - redis_data:/data

  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf
      - ./ssl:/etc/nginx/ssl
      - static_files:/app/static
    depends_on:
      - app

volumes:
  postgres_data:
  redis_data:
  static_files:
  uploaded_files:
```

### Kubernetes Configuration

```yaml
# k8s/deployment.yaml

apiVersion: apps/v1
kind: Deployment
metadata:
  name: booklet-api
  labels:
    app: booklet
    component: api
spec:
  replicas: 3
  selector:
    matchLabels:
      app: booklet
      component: api
  template:
    metadata:
      labels:
        app: booklet
        component: api
    spec:
      containers:
      - name: api
        image: booklet/api:latest
        ports:
        - containerPort: 8000
        env:
        - name: DATABASE_URL
          valueFrom:
            secretKeyRef:
              name: booklet-secrets
              key: database-url
        - name: REDIS_URL
          valueFrom:
            secretKeyRef:
              name: booklet-secrets
              key: redis-url
        - name: SECRET_KEY
          valueFrom:
            secretKeyRef:
              name: booklet-secrets
              key: secret-key
        resources:
          requests:
            cpu: 500m
            memory: 512Mi
          limits:
            cpu: 2000m
            memory: 2Gi
        livenessProbe:
          httpGet:
            path: /health
            port: 8000
          initialDelaySeconds: 30
          periodSeconds: 10
        readinessProbe:
          httpGet:
            path: /ready
            port: 8000
          initialDelaySeconds: 5
          periodSeconds: 5

---
apiVersion: v1
kind: Service
metadata:
  name: booklet-api-service
spec:
  selector:
    app: booklet
    component: api
  ports:
  - protocol: TCP
    port: 80
    targetPort: 8000
  type: ClusterIP

---
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: booklet-api-hpa
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: booklet-api
  minReplicas: 3
  maxReplicas: 20
  metrics:
  - type: Resource
    resource:
      name: cpu
      target:
        type: Utilization
        averageUtilization: 70
  - type: Resource
    resource:
      name: memory
      target:
        type: Utilization
        averageUtilization: 80
```

### CI/CD Pipeline

```yaml
# .github/workflows/deploy.yml

name: Build and Deploy

on:
  push:
    branches: [main, develop]
  pull_request:
    branches: [main]

jobs:
  test:
    runs-on: ubuntu-latest
    services:
      postgres:
        image: postgres:15
        env:
          POSTGRES_PASSWORD: postgres
        options: >-
          --health-cmd pg_isready
          --health-interval 10s
          --health-timeout 5s
          --health-retries 5
      redis:
        image: redis:7-alpine
        options: >-
          --health-cmd "redis-cli ping"
          --health-interval 10s
          --health-timeout 5s
          --health-retries 5

    steps:
    - uses: actions/checkout@v3

    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: '3.11'
        cache: 'pip'

    - name: Install dependencies
      run: |
        pip install -r requirements.txt
        pip install pytest pytest-cov

    - name: Run tests
      env:
        DATABASE_URL: postgresql://postgres:postgres@localhost:5432/test
        REDIS_URL: redis://localhost:6379
      run: |
        pytest --cov=app --cov-report=xml

    - name: Upload coverage
      uses: codecov/codecov-action@v3

    - name: Security scan
      run: |
        pip install safety bandit
        safety check
        bandit -r app

  build:
    needs: test
    runs-on: ubuntu-latest
    if: github.ref == 'refs/heads/main'

    steps:
    - uses: actions/checkout@v3

    - name: Set up Docker Buildx
      uses: docker/setup-buildx-action@v2

    - name: Login to Container Registry
      uses: docker/login-action@v2
      with:
        registry: ghcr.io
        username: ${{ github.actor }}
        password: ${{ secrets.GITHUB_TOKEN }}

    - name: Build and push
      uses: docker/build-push-action@v4
      with:
        context: .
        push: true
        tags: |
          ghcr.io/planex/booklet:latest
          ghcr.io/planex/booklet:${{ github.sha }}
        cache-from: type=gha
        cache-to: type=gha,mode=max

  deploy:
    needs: build
    runs-on: ubuntu-latest
    if: github.ref == 'refs/heads/main'

    steps:
    - name: Deploy to Kubernetes
      uses: azure/k8s-deploy@v4
      with:
        manifests: |
          k8s/deployment.yaml
          k8s/service.yaml
          k8s/ingress.yaml
        images: |
          ghcr.io/planex/booklet:${{ github.sha }}
        kubectl-version: 'latest'
```

### Monitoring & Observability

```yaml
# Prometheus Configuration

global:
  scrape_interval: 15s
  evaluation_interval: 15s

scrape_configs:
  - job_name: 'booklet-api'
    kubernetes_sd_configs:
      - role: pod
    relabel_configs:
      - source_labels: [__meta_kubernetes_pod_label_app]
        regex: booklet
        action: keep
      - source_labels: [__meta_kubernetes_pod_name]
        target_label: pod_name

  - job_name: 'postgres'
    static_configs:
      - targets: ['postgres-exporter:9187']

  - job_name: 'redis'
    static_configs:
      - targets: ['redis-exporter:9121']

alerting:
  alertmanagers:
    - static_configs:
        - targets: ['alertmanager:9093']

# Grafana Dashboards
# - API latency (p50, p95, p99)
# - Request rate (per endpoint)
# - Error rate (4xx, 5xx)
# - Database connections
# - Cache hit ratio
# - Queue depth
# - Pod resource usage
```

---

## API & Integrations

### REST API Specification

All API endpoints follow REST conventions with proper HTTP methods, status codes, and error responses.

#### Authentication

```http
POST /api/v1/auth/login
Content-Type: application/json

{
  "email": "user@example.com",
  "password": "secure_password"
}

Response 200:
{
  "access_token": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "refresh_token": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "token_type": "bearer",
  "expires_in": 1800
}
```

#### Customer Endpoints

```http
# List customers
GET /api/v1/customers?page=1&limit=50&search=john

Response 200:
{
  "data": [
    {
      "id": 1,
      "name": "Acme Corporation",
      "contact_person": "John Doe",
      "email": "john@acme.com",
      "phone": "+1234567890",
      "address": "123 Main St",
      "balance": 1500.00,
      "created_at": "2026-01-15T10:30:00Z"
    }
  ],
  "pagination": {
    "page": 1,
    "limit": 50,
    "total": 150,
    "pages": 3
  }
}

# Create customer
POST /api/v1/customers
Content-Type: application/json
Authorization: Bearer <token>

{
  "name": "Acme Corporation",
  "contact_person": "John Doe",
  "email": "john@acme.com",
  "phone": "+1234567890",
  "address": "123 Main St"
}

Response 201:
{
  "id": 151,
  "name": "Acme Corporation",
  "customer_number": "CUST-2026-001"
}
```

### Webhooks

Webhooks enable real-time notifications to external systems when events occur in Booklet.

```python
# app/models/webhooks.py (tenant schema)

class Webhook(Base):
    """Webhook subscriptions"""
    __tablename__ = "webhooks"

    id = Column(Integer, primary_key=True)
    name = Column(String(255))

    # Events to subscribe to
    events = Column(JSON)  # ["customer.created", "invoice.paid"]
    event_filter = Column(JSON)  # {"amount": {"gt": 1000}}

    # Endpoint details
    url = Column(String(500))
    method = Column(String(10), default="POST")  # POST, PUT
    headers = Column(JSON)  # Custom headers
    secret = Column(String(100))  # For signature verification

    # Retry config
    retry_on_failure = Column(Boolean, default=True)
    max_retries = Column(Integer, default=3)
    retry_interval_seconds = Column(Integer, default=60)

    # Status
    is_active = Column(Boolean, default=True)
    last_triggered_at = Column(DateTime(timezone=True))
    last_status = Column(String(50))  # success, failed

    # Logging
    # Relationship to webhook_delivery_log


class WebhookDeliveryLog(Base):
    """Webhook delivery attempts"""
    __tablename__ = "webhook_delivery_logs"

    id = Column(BigInteger, primary_key=True)
    webhook_id = Column(Integer, ForeignKey("webhooks.id"))

    # Event
    event_type = Column(String(100))
    event_id = Column(String(100))  # Invoice ID, etc.
    payload = Column(JSON)

    # Delivery
    attempt_number = Column(Integer, default=1)
    sent_at = Column(DateTime(timezone=True))

    # Response
    status_code = Column(Integer)
    response_body = Column(Text)
    duration_ms = Column(Integer)

    # Retry info
    will_retry = Column(Boolean, default=False)
    next_retry_at = Column(DateTime(timezone=True))


# Webhook triggering service
class WebhookService:
    async def trigger_event(self, tenant_id: int, event: str, data: dict):
        """Trigger webhooks for event"""

        # Find active webhooks for this event
        webhooks = db.query(Webhook).filter(
            Webhook.tenant_id == tenant_id,
            Webhook.is_active == True,
            Webhook.events.contains(event)
        ).all()

        for webhook in webhooks:
            # Apply filters
            if webhook.event_filter:
                if not self._match_filters(data, webhook.event_filter):
                    continue

            # Send webhook asynchronously
            await self._send_webhook(webhook, event, data)

    async def _send_webhook(self, webhook: Webhook, event: str, data: dict):
        """Send webhook request"""

        import httpx
        import hmac
        import hashlib

        # Prepare payload
        payload = {
            "event": event,
            "timestamp": datetime.now().isoformat(),
            "data": data
        }

        # Sign payload
        signature = hmac.new(
            webhook.secret.encode(),
            json.dumps(payload).encode(),
            hashlib.sha256
        ).hexdigest()

        # Send request
        async with httpx.AsyncClient() as client:
            try:
                response = await client.request(
                    method=webhook.method,
                    url=webhook.url,
                    json=payload,
                    headers={
                        **webhook.headers,
                        "X-Booklet-Signature": f"sha256={signature}",
                        "X-Booklet-Event": event,
                        "X-Booklet-Delivery": str(uuid.uuid4())
                    },
                    timeout=10
                )

                # Log delivery
                log = WebhookDeliveryLog(
                    webhook_id=webhook.id,
                    event_type=event,
                    event_id=data.get("id"),
                    payload=payload,
                    sent_at=datetime.now(),
                    status_code=response.status_code,
                    response_body=response.text[:1000],
                    duration_ms=response.elapsed.total_seconds() * 1000
                )
                db.add(log)
                db.commit()

            except Exception as e:
                # Log failure and schedule retry
                log = WebhookDeliveryLog(
                    webhook_id=webhook.id,
                    event_type=event,
                    sent_at=datetime.now(),
                    status_code=0,
                    response_body=str(e),
                    will_retry=webhook.retry_on_failure,
                    next_retry_at=datetime.now() + timedelta(seconds=webhook.retry_interval_seconds)
                )
                db.add(log)
                db.commit()
```

### Integration Partners

| Category | Partner | Integration | Features |
|----------|---------|-------------|----------|
| **Payment** | Stripe | Native | Cards, subscriptions, invoicing |
| **Payment** | PayPal | Native | PayPal checkout, Venmo |
| **Payment** | Square | API | POS integration |
| **Banking** | Plaid | API | Bank feeds, account verification |
| **Banking** | Yodlee | API | International bank feeds |
| **E-commerce** | Shopify | API | Sync orders, inventory |
| **E-commerce** | WooCommerce | API | Sync orders, products |
| **E-commerce** | Magento | API | Order sync |
| **Shipping** | FedEx | API | Shipping labels, tracking |
| **Shipping** | UPS | API | Shipping labels, rates |
| **Shipping** | USPS | API | Shipping labels |
| **Tax** | Avalara | API | Sales tax calculation |
| **Tax** | TaxJar | API | Sales tax filing |
| **Communication** | Twilio | API | SMS notifications |
| **Communication** | SendGrid | API | Transactional email |
| **Communication** | Slack | Webhook | Notifications |
| **CRM** | Salesforce | API | Lead sync |
| **CRM** | HubSpot | API | Contact sync |
| **Productivity** | Google Workspace | API | Calendar, Drive |
| **Productivity** | Microsoft 365 | API | Outlook, OneDrive |

---

## Missing Features - Production Checklist

### Critical (Must Have for MVP Launch)

- [ ] **Testing Suite**
  - [ ] Unit tests (pytest) - 80%+ coverage
  - [ ] Integration tests (API endpoints)
  - [ ] E2E tests (Playwright)
  - [ ] Load testing (Locust)
  - [ ] Security testing (OWASP ZAP)

- [ ] **Error Handling & Logging**
  - [ ] Structured logging (JSON format)
  - [ ] Error tracking (Sentry)
  - [ ] Log aggregation (ELK)
  - [ ] Request tracing (distributed tracing)
  - [ ] Alerting (PagerDuty/OpsGenie)

- [ ] **Performance Optimization**
  - [ ] Database indexing strategy
  - [ ] Query optimization (N+1 elimination)
  - [ ] Caching layer (Redis)
  - [ ] API response pagination
  - [ ] Static asset CDN
  - [ ] Database connection pooling
  - [ ] Lazy loading for large datasets

- [ ] **Security Hardening**
  - [ ] Rate limiting (API, login attempts)
  - [ ] CSRF protection
  - [ ] SQL injection prevention (ORM parameterized)
  - [ ] XSS protection headers
  - [ ] Security headers (CSP, HSTS)
  - [ ] Input validation & sanitization
  - [ ] Secret management (Vault)
  - [ ] Dependency scanning (Snyk)

- [ ] **Backup & Disaster Recovery**
  - [ ] Automated daily backups
  - [ ] Point-in-time recovery (PITR)
  - [ ] Backup encryption
  - [ ] Off-site backup storage
  - [ ] Disaster recovery runbook
  - [ ] RTO/RPO targets (RTO: 4h, RPO: 15min)

- [ ] **Multi-tenancy Implementation**
  - [ ] Tenant isolation (schema-based)
  - [ ] Tenant-specific domains
  - [ ] Tenant resource limits
  - [ ] Tenant data separation
  - [ ] Tenant onboarding automation

- [ ] **Subscription & Billing**
  - [ ] Stripe integration
  - [ ] Subscription management
  - [ ] Invoice generation
  - [ ] Payment processing
  - [ ] Usage tracking/metering
  - [ ] Dunning (failed payment handling)
  - [ ] Proration for plan changes

- [ ] **User Management**
  - [ ] Multi-factor authentication
  - [ ] Password reset flow
  - [ ] Email verification
  - [ ] Role-based permissions
  - [ ] Audit logging
  - [ ] Session management
  - [ ] User invitation flow

- [ ] **Documentation**
  - [ ] API documentation (OpenAPI/Swagger)
  - [ ] User guide
  - [ ] Admin guide
  - [ ] Developer documentation
  - [ ] Architecture diagrams
  - [ ] Runbook/SOP

### High Priority (Important for Production)

- [ ] **Monitoring & Observability**
  - [ ] Metrics collection (Prometheus)
  - [ ] Dashboards (Grafana)
  - [ ] Health check endpoints
  - [ ] Uptime monitoring
  - [ ] Performance monitoring (APM)
  - [ ] Real user monitoring (RUM)

- [ ] **Internationalization**
  - [ ] Multi-language support (i18n)
  - [ ] Multi-currency accounting
  - [ ] Date/number formatting
  - [ ] Tax compliance per country
  - [ ] Timezone handling

- [ ] **API Features**
  - [ ] API key management
  - [ ] Rate limiting per API key
  - [ ] API usage analytics
  - [ ] Webhooks
  - [ ] SDK libraries (Python, JS)

- [ ] **Data Management**
  - [ ] Bulk import/export
  - [ ] Data migration tools
  - [ ] Data anonymization (GDPR)
  - [ ] Data retention policies
  - [ ] Audit log export

- [ ] **Frontend Improvements**
  - [ ] Dark mode
  - [ ] Mobile responsive design
  - [ ] Accessibility (WCAG 2.1 AA)
  - [ ] Progressive Web App (PWA)
  - [ ] Offline support

- [ ] **Compliance**
  - [ ] GDPR compliance
  - [ ] SOC 2 Type II preparation
  - [ ] Data processing agreements
  - [ ] Cookie consent
  - [ ] Privacy policy
  - [ ] Terms of service

- [ ] **DevOps**
  - [ ] CI/CD pipeline
  - [ ] Automated testing in CI
  - [ ] Blue-green deployments
  - [ ] Canary deployments
  - [ ] Rollback procedures
  - [ ] Infrastructure as Code (Terraform)

### Medium Priority (Growth & Scale)

- [ ] **Advanced Features**
  - [ ] Custom report builder
  - [ ] Scheduled reports (email)
  - [ ] Custom fields per module
  - [ ] Workflow automation
  - [ ] Approval workflows
  - [ ] Document templates

- [ ] **Integrations**
  - [ ] CRM integration (HubSpot, Salesforce)
  - [ ] E-commerce platforms (Shopify, WooCommerce)
  - [ ] Payment gateways (Square, Adyen)
  - [ ] Tax services (Avalara, TaxJar)
  - [ ] Shipping carriers (FedEx, UPS)

- [ ] **Mobile Apps**
  - [ ] iOS app (React Native)
  - [ ] Android app (React Native)
  - [ ] Offline mode
  - [ ] Push notifications
  - [ ] Biometric auth

- [ ] **AI/ML Enhancements**
  - [ ] Invoice OCR
  - [ ] Anomaly detection
  - [ ] Cash flow forecasting
  - [ ] Smart categorization
  - [ ] Payment prediction

- [ ] **Communication**
  - [ ] In-app notifications
  - [ ] Email notifications
  - [ ] SMS notifications
  - [ ] Slack/Discord integration
  - [ ] In-app chat (support)

### Nice to Have (Future Enhancements)

- [ ] **White-label capabilities**
  - [ ] Custom domains
  - [ ] Custom branding (logo, colors)
  - [ ] Custom email templates
  - [ ] Custom help center

- [ ] **Industry Modules**
  - [ ] Retail POS
  - [ ] Restaurant management
  - [ ] Manufacturing (MRP)
  - [ ] Construction (job costing)
  - [ ] Non-profit (fund accounting)

- [ ] **Advanced Analytics**
  - [ ] Machine learning predictions
  - [ ] Custom dashboards
  - [ ] Data warehouse integration
  - [ ] Business intelligence connectors

- [ ] **Marketplace**
  - [ ] Third-party app store
  - [ ] Developer portal
  - [ ] Revenue sharing

---

## Implementation Roadmap

### Phase 1: Foundation (Months 1-2)

**Goal:** Set up production-ready infrastructure and core multi-tenancy

**Tasks:**
1. Infrastructure setup
   - AWS/GCP account setup
   - VPC and network configuration
   - Kubernetes cluster setup
   - CI/CD pipeline setup
   - Monitoring & logging setup
   - Backup & disaster recovery

2. Multi-tenancy implementation
   - Tenant schema isolation
   - Tenant middleware
   - Tenant onboarding automation
   - Subdomain routing

3. Security foundation
   - JWT authentication with refresh tokens
   - RBAC implementation
   - Audit logging
   - Security headers
   - Rate limiting

4. Billing foundation
   - Stripe integration
   - Subscription models
   - Invoice generation
   - Payment processing

**Deliverables:**
- Production infrastructure running
- Multi-tenant system operational
- Billing system working
- CI/CD pipeline automated

### Phase 2: Core Product (Months 3-4)

**Goal:** Build and test all ERP modules

**Tasks:**
1. Complete all ERP modules
   - Accounting (double-entry, financial statements)
   - Inventory (multi-warehouse, batches)
   - Sales & CRM (leads to invoices)
   - Purchasing (PO to payment)
   - HR & Payroll (processing and compliance)
   - Fixed Assets (depreciation)

2. Testing
   - Unit tests (80%+ coverage)
   - Integration tests
   - E2E tests
   - Load testing (1000 concurrent users)
   - Security testing

3. Frontend refinement
   - Responsive design
   - Mobile optimization
   - Accessibility
   - Performance optimization

**Deliverables:**
- All modules functional
- Full test suite passing
- Production-ready frontend

### Phase 3: Production Launch (Months 5-6)

**Goal:** Prepare and execute public launch

**Tasks:**
1. Compliance & certification
   - GDPR compliance implementation
   - SOC 2 Type II audit preparation
   - Security audit
   - Penetration testing

2. Documentation
   - API documentation (OpenAPI)
   - User guides
   - Admin guides
   - Developer documentation
   - Runbooks

3. Go-to-market
   - Marketing website
   - Pricing page
   - Landing pages
   - Email automation
   - Support setup

4. Launch preparation
   - Beta testing (50 users)
   - Bug fixes
   - Performance optimization
   - Uptime verification

**Deliverables:**
- SOC 2 compliant (or in progress)
- Full documentation suite
- Marketing website live
- Beta testers onboarded

### Phase 4: Growth & Scale (Months 7-12)

**Goal:** Add advanced features and scale operations

**Tasks:**
1. Advanced features
   - Custom report builder
   - Workflow automation
   - API & webhooks
   - Mobile apps (iOS/Android)
   - Advanced analytics

2. Integrations
   - CRM platforms
   - E-commerce platforms
   - Payment gateways
   - Tax services

3. Scale operations
   - Performance optimization
   - Auto-scaling improvements
   - Database optimization
   - CDN optimization

4. Expansion
   - Industry-specific modules
   - International markets
   - White-label program

**Deliverables:**
- 100+ paying customers
- Mobile apps launched
- 10+ integrations
- Self-serve onboarding

---

## Monitoring & Analytics

### Key Metrics to Track

**Product Metrics:**
- Daily Active Users (DAU)
- Monthly Active Users (MAU)
- Customer Acquisition Cost (CAC)
- Customer Lifetime Value (LTV)
- Churn rate
- MRR/ARR
- Feature usage

**Technical Metrics:**
- API response times (p50, p95, p99)
- Error rate
- Uptime
- Database query performance
- Cache hit ratio
- Queue depth
- Server resource utilization

**Business Metrics:**
- MRR (Monthly Recurring Revenue)
- ARPU (Average Revenue Per User)
- Trial-to-paid conversion
- Free tier conversion
- Plan distribution
- Add-on attach rate

### Dashboard Configuration

```yaml
# Grafana Dashboard Config

dashboards:
  - name: Executive Overview
    panels:
      - MRR/ARR
      - Customer count
      - Churn rate
      - Trial conversion
      - Revenue by plan

  - name: Technical Overview
    panels:
      - Request rate
      - Error rate
      - Response times
      - Database connections
      - CPU/Memory usage

  - name: Business Metrics
    panels:
      - Active subscriptions
      - New signups
      - Cancellations
      - Revenue trends
      - Feature usage
```

---

## Support & Maintenance

### Support Tiers

| Tier | Target | Response Time | Availability |
|------|--------|---------------|-------------|
| **Community** | Free tier users | 48 hours | Email (community) |
| **Standard** | Starter/Pro | 24 hours | Email |
| **Priority** | Enterprise | 4 hours | Email + Phone |
| **Premium** | Enterprise+ | 1 hour | 24/7 Phone + Slack |

### Maintenance Windows

- **Planned maintenance:** Monthly, first Sunday 2-4 AM UTC
- **Hotfixes:** As needed, with 24-hour notice
- **Emergency:** Immediate for critical issues

### SLA Commitment

| Plan | Uptime SLA | Credit for Downtime |
|------|-----------|---------------------|
| Starter | 99.5% | 10% credit |
| Professional | 99.9% | 25% credit |
| Enterprise | 99.99% | 100% credit |

---

## Conclusion

This comprehensive production plan outlines the complete architecture, features, and implementation roadmap for Booklet as a multi-tenant SaaS ERP platform. The system is designed to be:

1. **Scalable:** Handle growth from 10 to 10,000+ tenants
2. **Secure:** Enterprise-grade security with compliance
3. **Reliable:** 99.99% uptime with disaster recovery
4. **Modular:** Easy to extend with new features
5. **Profitable:** Clear monetization with usage-based pricing

The phased approach allows for iterative development and validation, reducing risk while accelerating time to market.

**Next Steps:**
1. Review and approve this plan
2. Prioritize features based on market research
3. Assemble development team
4. Set up infrastructure
5. Begin Phase 1 implementation

---

*Document Version: 2.0*
*Last Updated: 2026-02-13*
*Maintained By: Planex (Planexis) Solutions*


Note: currency should be configurable, the default currency should be naira 








# Booklet Architecture Update Guide
## Migrating to Flask + Jinja + HTMX Frontend with FastAPI Backend

**Project:** Booklet SaaS ERP
**Version:** Current → v2.0
**Date:** 2026-02-13

---

## Overview

This document outlines the architectural migration from a **single FastAPI + Jinja2** monolithic architecture to a **separated Flask frontend + FastAPI backend** architecture.

### Current Architecture (What You Have)

```
┌─────────────────────────────────────────────────────────────────────┐
│  FastAPI Application                                               │
│  ┌────────────────────────────────────────────────────────────────┐│
│  │  Jinja2 Templates (Server-Side Rendering)                      ││
│  │  └── HTML with HTMX attributes                                ││
│  └────────────────────────────────────────────────────────────────┘│
│  ┌────────────────────────────────────────────────────────────────┐│
│  │  API Routes (Returning HTML templates)                         ││
│  └────────────────────────────────────────────────────────────────┘│
│  ┌────────────────────────────────────────────────────────────────┐│
│  │  Business Logic & CRUD Operations                              ││
│  └────────────────────────────────────────────────────────────────┘│
│  ┌────────────────────────────────────────────────────────────────┐│
│  │  SQLAlchemy ORM                                                ││
│  └────────────────────────────────────────────────────────────────┘│
└─────────────────────────────────────────────────────────────────────┘
```

### Target Architecture (What You Want)

```
┌─────────────────────────────────────────────────────────────────────┐
│                        FRONTEND LAYER                               │
│  ┌────────────────────────────────────────────────────────────────┐│
│  │  Flask Application (Port 5000)                                 ││
│  │  ┌──────────────────────────────────────────────────────────┐│
│  │  │  Jinja2 Templates (HTML pages)                            ││
│  │  │  └── HTMX for dynamic interactions                        ││
│  │  └──────────────────────────────────────────────────────────┘│
│  │  ┌──────────────────────────────────────────────────────────┐│
│  │  │  Alpine.js for client-side reactivity                    ││
│  │  └──────────────────────────────────────────────────────────┘│
│  │  ┌──────────────────────────────────────────────────────────┐│
│  │  │  Flowbite UI Components (CDN)                           ││
│  │  └──────────────────────────────────────────────────────────┘│
│  │  ┌──────────────────────────────────────────────────────────┐│
│  │  │  Tailwind CSS (CDN)                                      ││
│  │  └──────────────────────────────────────────────────────────┘│
│  │  ┌──────────────────────────────────────────────────────────┐│
│  │  │  ECharts (Data Visualization)                           ││
│  │  └──────────────────────────────────────────────────────────┘│
│  └────────────────────────────────────────────────────────────────┘│
└─────────────────────────────────────────────────────────────────────┘
                              │
                              │ HTTP (REST API calls)
                              ▼
┌─────────────────────────────────────────────────────────────────────┐
│                        BACKEND LAYER                                │
│  ┌────────────────────────────────────────────────────────────────┐│
│  │  FastAPI Application (Port 8000)                              ││
│  │  ┌──────────────────────────────────────────────────────────┐│
│  │  │  RESTful API Endpoints (JSON responses)                  ││
│  │  │  /api/v1/customers                                      ││
│  │  │  /api/v1/invoices                                       ││
│  │  │  /api/v1/products                                       ││
│  │  └──────────────────────────────────────────────────────────┘│
│  │  ┌──────────────────────────────────────────────────────────┐│
│  │  │  Business Logic & CRUD Services                          ││
│  │  └──────────────────────────────────────────────────────────┘│
│  │  ┌──────────────────────────────────────────────────────────┐│
│  │  │  Authentication (JWT)                                   ││
│  │  └──────────────────────────────────────────────────────────┘│
│  │  ┌──────────────────────────────────────────────────────────┐│
│  │  │  SQLAlchemy ORM                                          ││
│  │  └──────────────────────────────────────────────────────────┘│
│  └────────────────────────────────────────────────────────────────┘│
└─────────────────────────────────────────────────────────────────────┘
```

---

## Migration Strategy

### Option 1: Gradual Migration (Recommended)

Migrate incrementally without breaking existing functionality.

**Phase 1: Set up FastAPI as pure API backend (2 weeks)**
1. Create `/api/` routes for JSON responses
2. Keep existing HTML routes in place
3. Frontend still uses old routes, new API available for future use

**Phase 2: Set up Flask frontend (2 weeks)**
1. Create Flask application structure
2. Copy templates to Flask project
3. Set up Jinja2 environment in Flask
4. Configure static assets

**Phase 3: Wire Flask to FastAPI (2 weeks)**
1. Update Flask templates to call FastAPI `/api/` endpoints
2. Use HTMX for API calls to FastAPI
3. Remove HTML responses from FastAPI
4. Switch DNS to point to Flask frontend

**Phase 4: Cleanup (1 week)**
1. Remove HTML templates from FastAPI
2. Remove deprecated routes
3. Update documentation
4. Final testing

### Option 2: Parallel Development (Faster)

Build Flask frontend alongside existing FastAPI, then switch over.

1. Create new `frontend/` directory for Flask
2. Copy and adapt templates to Flask
3. Build API endpoints in FastAPI
4. Test Flask + FastAPI integration in parallel
5. Cutover when ready

---

## Implementation Details

### 1. Directory Structure

```
booklet5/
├── backend/                      # FastAPI backend service
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py              # FastAPI entry point
│   │   ├── database.py
│   │   ├── models.py
│   │   ├── schemas.py
│   │   ├── crud/               # Business logic
│   │   ├── routers/            # API routes (JSON only)
│   │   ├── services/           # Additional services
│   │   └── ai_providers.py
│   ├── requirements.txt
│   └── tests/
│
├── frontend/                     # Flask frontend service
│   ├── app/
│   │   ├── __init__.py         # Flask app factory
│   │   ├── routes/             # Page routes (returns HTML)
│   │   ├── templates/          # Jinja2 templates
│   │   │   ├── _shared/        # Base layouts, components
│   │   │   ├── dashboard/
│   │   │   ├── customers/
│   │   │   ├── sales/
│   │   │   └── ...
│   │   ├── static/            # Static assets
│   │   │   ├── css/
│   │   │   ├── js/
│   │   │   └── img/
│   │   └── utils/             # Frontend utilities
│   ├── requirements.txt
│   └── tests/
│
├── shared/                      # Shared code
│   ├── __init__.py
│   ├── config.py              # Shared configuration
│   ├── constants.py           # Shared constants
│   └── types.py               # Shared type definitions
│
├── docker-compose.yml
├── Dockerfile.backend
├── Dockerfile.frontend
└── .env
```

### 2. FastAPI Backend Configuration

```python
# backend/app/main.py

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

# CORS Configuration
app = FastAPI(
    title="Booklet API",
    description="Multi-tenant SaaS ERP Backend API",
    version="2.0.0"
)

# Allow requests from Flask frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5000", "https://*.booklet.com"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API routers (JSON responses only)
from .routers import (
    auth, customers, sales, purchases, inventory,
    accounting, hr, reports, analytics
)

app.include_router(auth.router, prefix="/api/v1/auth", tags=["Authentication"])
app.include_router(customers.router, prefix="/api/v1/customers", tags=["Customers"])
app.include_router(sales.router, prefix="/api/v1/sales", tags=["Sales"])
app.include_router(purchases.router, prefix="/api/v1/purchases", tags=["Purchases"])
app.include_router(inventory.router, prefix="/api/v1/inventory", tags=["Inventory"])
app.include_router(accounting.router, prefix="/api/v1/accounting", tags=["Accounting"])
app.include_router(hr.router, prefix="/api/v1/hr", tags=["HR"])
app.include_router(reports.router, prefix="/api/v1/reports", tags=["Reports"])
app.include_router(analytics.router, prefix="/api/v1/analytics", tags=["Analytics"])

# Health check
@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "backend-api"}

# Exception handlers
@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    return JSONResponse(
        status_code=exc.status_code,
        content={"error": True, "message": exc.detail}
    )
```

#### API Route Example (JSON Response)

```python
# backend/app/routers/customers.py

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from ..database import get_db
from .. import schemas, crud
from ..security import get_current_user

router = APIRouter()

@router.get("/", response_model=List[schemas.Customer])
async def list_customers(
    skip: int = 0,
    limit: int = 50,
    search: str = None,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """List all customers (JSON response)"""
    tenant_id = current_user.tenant_id

    customers = crud.customer.get_multi(
        db,
        tenant_id=tenant_id,
        skip=skip,
        limit=limit,
        search=search
    )
    return customers

@router.post("/", response_model=schemas.Customer, status_code=201)
async def create_customer(
    customer_data: schemas.CustomerCreate,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Create new customer (JSON response)"""
    tenant_id = current_user.tenant_id

    customer = crud.customer.create(db, obj_in=customer_data, tenant_id=tenant_id)
    return customer

@router.get("/{customer_id}", response_model=schemas.Customer)
async def get_customer(
    customer_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Get single customer by ID (JSON response)"""
    customer = crud.customer.get(db, id=customer_id)
    if not customer:
        raise HTTPException(status_code=404, detail="Customer not found")
    return customer
```

### 3. Flask Frontend Configuration

```python
# frontend/app/__init__.py

from flask import Flask, render_template, session, g
from functools import wraps
import requests

# Configuration
API_BASE_URL = "http://localhost:8000/api/v1"

def create_app(config_name='development'):
    """Flask application factory"""
    app = Flask(__name__,
                template_folder='templates',
                static_folder='static')

    app.config['SECRET_KEY'] = 'your-secret-key'
    app.config['API_BASE_URL'] = API_BASE_URL

    # Register blueprints
    from .routes import (
        auth, dashboard, customers, sales, purchases,
        inventory, accounting, hr, reports, analytics
    )

    app.register_blueprint(auth.bp)
    app.register_blueprint(dashboard.bp)
    app.register_blueprint(customers.bp, url_prefix='/customers')
    app.register_blueprint(sales.bp, url_prefix='/sales')
    app.register_blueprint(purchases.bp, url_prefix='/purchases')
    app.register_blueprint(inventory.bp, url_prefix='/inventory')
    app.register_blueprint(accounting.bp, url_prefix='/accounting')
    app.register_blueprint(hr.bp, url_prefix='/hr')
    app.register_blueprint(reports.bp, url_prefix='/reports')
    app.register_blueprint(analytics.bp, url_prefix='/analytics')

    # Context processors
    @app.context_processor
    def utility_processor():
        """Make utilities available in templates"""
        return {
            'tenant': lambda: session.get('tenant'),
            'user': lambda: session.get('user'),
        }

    return app
```

#### Flask Route Example (HTML Response)

```python
# frontend/app/routes/customers.py

from flask import Blueprint, render_template, request, session, redirect, url_for
import requests

bp = Blueprint('customers', __name__)

API_BASE_URL = "http://localhost:8000/api/v1"

def get_api_headers():
    """Get API request headers with auth token"""
    token = session.get('access_token')
    return {
        'Authorization': f'Bearer {token}',
        'Content-Type': 'application/json'
    }

@bp.route('/')
def list_customers():
    """Render customers list page"""
    page = request.args.get('page', 1, type=int)
    search = request.args.get('search', '')

    # Fetch data from backend API
    headers = get_api_headers()
    params = {'skip': (page - 1) * 20, 'limit': 20}
    if search:
        params['search'] = search

    response = requests.get(
        f"{API_BASE_URL}/customers/",
        headers=headers,
        params=params
    )
    customers = response.json() if response.status_code == 200 else []

    return render_template('customers/list.html',
                         customers=customers,
                         page=page,
                         search=search)

@bp.route('/new')
def new_customer():
    """Render new customer form"""
    return render_template('customers/new.html')

@bp.route('/', methods=['POST'])
def create_customer():
    """Handle new customer form submission"""
    headers = get_api_headers()
    data = request.form.to_dict()

    response = requests.post(
        f"{API_BASE_URL}/customers/",
        headers=headers,
        json=data
    )

    if response.status_code == 201:
        return redirect(url_for('customers.list_customers'))
    else:
        return render_template('customers/new.html', error=response.json())
```

### 4. Jinja2 Template with HTMX Integration

```jinja
{# frontend/app/templates/customers/list.html #}

{% extends "_shared/base.html" %}

{% block title %}Customers{% endblock %}

{% block content %}
<div class="container mx-auto px-4 py-6">
    <!-- Header -->
    <div class="flex justify-between items-center mb-6">
        <h1 class="text-2xl font-bold text-gray-900">Customers</h1>
        <a href="{{ url_for('customers.new_customer') }}"
           class="bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700">
            Add Customer
        </a>
    </div>

    <!-- Search -->
    <div class="mb-4">
        <form hx-get="{{ url_for('customers.list_customers') }}"
              hx-target="#customers-table"
              hx-indicator="#loading">
            <input type="text"
                   name="search"
                   value="{{ search }}"
                   placeholder="Search customers..."
                   class="w-full md:w-96 px-4 py-2 border rounded-lg">
        </form>
    </div>

    <!-- Loading indicator -->
    <div id="loading" class="htmx-indicator hidden">
        <div class="spinner"></div>
    </div>

    <!-- Customers Table -->
    <div id="customers-table"
         class="bg-white rounded-lg shadow overflow-hidden">
        <table class="min-w-full divide-y divide-gray-200">
            <thead class="bg-gray-50">
                <tr>
                    <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                        Name
                    </th>
                    <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                        Email
                    </th>
                    <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                        Phone
                    </th>
                    <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                        Balance
                    </th>
                    <th class="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase">
                        Actions
                    </th>
                </tr>
            </thead>
            <tbody class="bg-white divide-y divide-gray-200">
                {% for customer in customers %}
                <tr>
                    <td class="px-6 py-4 whitespace-nowrap">
                        {{ customer.name }}
                    </td>
                    <td class="px-6 py-4 whitespace-nowrap">
                        {{ customer.email or '-' }}
                    </td>
                    <td class="px-6 py-4 whitespace-nowrap">
                        {{ customer.phone or '-' }}
                    </td>
                    <td class="px-6 py-4 whitespace-nowrap">
                        {{ "${:,.2f}".format(customer.balance) }}
                    </td>
                    <td class="px-6 py-4 whitespace-nowrap text-right text-sm font-medium">
                        <a href="{{ url_for('customers.view_customer', customer_id=customer.id) }}"
                           class="text-blue-600 hover:text-blue-900">View</a>
                        <a href="{{ url_for('customers.edit_customer', customer_id=customer.id) }}"
                           class="ml-4 text-indigo-600 hover:text-indigo-900">Edit</a>
                    </td>
                </tr>
                {% endfor %}
            </tbody>
        </table>

        {% if not customers %}
        <div class="text-center py-12">
            <p class="text-gray-500">No customers found</p>
        </div>
        {% endif %}
    </div>
</div>
{% endblock %}
```

### 5. HTMX Configuration

```html
{# frontend/app/templates/_shared/base.html #}

<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">

    <!-- Tailwind CSS (CDN) -->
    <script src="https://cdn.tailwindcss.com"></script>

    <!-- Flowbite (CDN) -->
    <link href="https://cdnjs.cloudflare.com/ajax/libs/flowbite/2.2.0/flowbite.min.css" rel="stylesheet" />

    <!-- HTMX (CDN) -->
    <script src="https://unpkg.com/htmx.org@1.9.10"></script>

    <!-- Alpine.js (CDN) -->
    <script defer src="https://cdn.jsdelivr.net/npm/alpinejs@3.x.x/dist/cdn.min.js"></script>

    <!-- ECharts (CDN) -->
    <script src="https://cdn.jsdelivr.net/npm/echarts@5.4.3/dist/echarts.min.js"></script>

    <!-- Custom Styles -->
    <link rel="stylesheet" href="{{ url_for('static', filename='css/app.css') }}">

    {% block head %}{% endblock %}
</head>
<body class="bg-gray-50">

    <!-- Navigation -->
    {% include '_shared/navbar.html' %}

    <!-- Main Content -->
    <main>
        {% block content %}{% endblock %}
    </main>

    <!-- Footer -->
    {% include '_shared/footer.html' %}

    <!-- Scripts -->
    <script src="https://cdnjs.cloudflare.com/ajax/libs/flowbite/2.2.0/flowbite.min.js"></script>
    <script src="{{ url_for('static', filename='js/app.js') }}"></script>
    {% block scripts %}{% endblock %}
</body>
</html>
```

### 6. Docker Configuration

```yaml
# docker-compose.yml

version: '3.8'

services:
  backend:
    build:
      context: .
      dockerfile: Dockerfile.backend
    ports:
      - "8000:8000"
    environment:
      - DATABASE_URL=postgresql://booklet:booklet_pass@db:5432/booklet
      - REDIS_URL=redis://redis:6379
    depends_on:
      - db
      - redis

  frontend:
    build:
      context: .
      dockerfile: Dockerfile.frontend
    ports:
      - "5000:5000"
    environment:
      - API_BASE_URL=http://backend:8000/api/v1
    depends_on:
      - backend

  db:
    image: postgres:15-alpine
    environment:
      - POSTGRES_USER=booklet
      - POSTGRES_PASSWORD=booklet_pass
      - POSTGRES_DB=booklet
    volumes:
      - postgres_data:/var/lib/postgresql/data

  redis:
    image: redis:7-alpine
    volumes:
      - redis_data:/data

  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf
    depends_on:
      - frontend

volumes:
  postgres_data:
  redis_data:
```

```dockerfile
# Dockerfile.backend
FROM python:3.11-slim

WORKDIR /app

COPY requirements.backend.txt .
RUN pip install --no-cache-dir -r requirements.backend.txt

COPY backend/ .

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

```dockerfile
# Dockerfile.frontend
FROM python:3.11-slim

WORKDIR /app

COPY requirements.frontend.txt .
RUN pip install --no-cache-dir -r requirements.frontend.txt

COPY frontend/ .

CMD ["gunicorn", "-b", "0.0.0.0:5000", "app:create_app()"]
```

---

## Benefits of This Architecture

### Separation of Concerns
- **Backend (FastAPI):** Pure API, business logic, data access
- **Frontend (Flask):** Presentation, user interface, routing

### Scalability
- Scale frontend and backend independently
- Deploy more backend pods for API-heavy workloads
- Deploy more frontend pods for serving static assets

### Flexibility
- Easy to add new frontend clients (mobile, desktop)
- Backend API can be consumed by third parties
- Frontend can be swapped (React, Vue) without touching backend

### Development Efficiency
- Frontend and backend teams can work independently
- Clear API contracts (OpenAPI documentation)
- Parallel development

### Reusability
- Backend API can be reused for:
  - Mobile apps (React Native)
  - Desktop apps (Electron)
  - Third-party integrations
  - Webhooks
  - Partner platforms

---

## Migration Checklist

### Phase 1: Backend API Preparation
- [ ] Create new `backend/` directory structure
- [ ] Move models, crud, schemas to backend
- [ ] Convert all routes to return JSON (no HTML)
- [ ] Add proper API documentation (OpenAPI)
- [ ] Set up CORS for Flask frontend
- [ ] Test all API endpoints with Postman/Insomnia

### Phase 2: Flask Frontend Setup
- [ ] Create new `frontend/` directory structure
- [ ] Set up Flask application factory
- [ ] Copy and adapt Jinja2 templates
- [ ] Configure HTMX for API calls
- [ ] Set up Alpine.js for interactivity
- [ ] Configure Tailwind CSS and Flowbite
- [ ] Test all pages render correctly

### Phase 3: Integration
- [ ] Update Flask routes to call FastAPI endpoints
- [ ] Implement authentication flow (JWT handoff)
- [ ] Set up session sharing between Flask and FastAPI
- [ ] Test end-to-end user workflows
- [ ] Performance testing

### Phase 4: Deployment
- [ ] Update docker-compose.yml
- [ ] Create separate Dockerfiles
- [ ] Update CI/CD pipeline
- [ ] Set up nginx routing
- [ ] Deploy to staging
- [ ] Run full integration tests
- [ ] Deploy to production

---

## Summary

This architecture update provides a clear separation between frontend and backend, enabling:

1. **Independent scaling** of UI and API layers
2. **Multiple client types** accessing the same backend
3. **Clearer code organization** and team responsibilities
4. **Future flexibility** for technology changes
5. **Better testing** with isolated components

The migration can be done incrementally without disrupting existing functionality, and the result is a more maintainable and scalable system suitable for a production SaaS product.

---

*Document Version: 1.0*
*Last Updated: 2026-02-13*









# Booklet Developer Quick Start Guide

**Project:** Booklet SaaS ERP
**For:** New Developers Joining the Team
**Last Updated:** 2026-02-13

---

## Table of Contents

1. [Getting Started](#getting-started)
2. [Development Environment Setup](#development-environment-setup)
3. [Project Structure](#project-structure)
4. [Common Development Tasks](#common-development-tasks)
5. [Testing](#testing)
6. [Debugging](#debugging)
7. [Git Workflow](#git-workflow)
8. [Useful Commands](#useful-commands)
9. [Troubleshooting](#troubleshooting)

---

## Getting Started

### Prerequisites

- **Python 3.11+** - Download from [python.org](https://python.org)
- **Git** - Download from [git-scm.com](https://git-scm.com)
- **PostgreSQL 15+** - Download from [postgresql.org](https://postgresql.org) (or use Docker)
- **Redis 7+** - For caching and sessions (or use Docker)
- **Docker** (optional but recommended) - Download from [docker.com](https://docker.com)

### Clone and Setup

```bash
# Clone repository
git clone https://github.com/planexis/booklet.git
cd booklet

# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Windows:
venv\Scripts\activate
# On Linux/Mac:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Install development dependencies
pip install -r requirements-dev.txt

# Copy environment template
cp .env.example .env

# Edit .env file with your settings
# Generate a secret key: python -c "import secrets; print(secrets.token_urlsafe(32))"
```

### Environment Variables

Create a `.env` file in the project root:

```env
# Database
DATABASE_URL=postgresql://booklet:booklet_password@localhost:5432/booklet_dev

# Redis
REDIS_URL=redis://localhost:6379/0

# Security
SECRET_KEY=your-secret-key-here
ENCRYPTION_KEY=your-32-byte-encryption-key

# API Keys (Optional)

i wanna use Paga (nigeria fintech)

STRIPE_API_KEY=sk_test_...
STRIPE_WEBHOOK_SECRET=whsec_...
OPENAI_API_KEY=sk-...

# Email (Optional)
MAIL_USERNAME=your-email@example.com
MAIL_PASSWORD=your-app-password
MAIL_FROM=noreply@booklet.com
MAIL_PORT=587
MAIL_SERVER=smtp.gmail.com

# Frontend (if using separated architecture)
FRONTEND_URL=http://localhost:5000
```

### Initialize Database

```bash
# Run migrations
alembic upgrade head

# Or create all tables (if not using Alembic)
python -c "from app.database import engine, Base; Base.metadata.create_all(bind=engine)"

# Seed initial data (permissions, roles)
python scripts/seed_data.py
```

### Run Development Server

```bash
# Backend only (FastAPI)
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# Frontend only (Flask - if separated)
cd frontend
flask run --host 0.0.0.0 --port 5000


create a global run to run both on same sever

# Or use docker-compose
docker-compose up
```

Access the application at:
- **Frontend:** http://localhost:5000
- **Backend API:** http://localhost:8000
- **API Docs (Swagger):** http://localhost:8000/docs

---

## Development Environment Setup

### VS Code Extensions (Recommended)

1. **Python** - Microsoft
2. **Pylance** - Microsoft
3. **Python Test Explorer** - LittleFoxTeam
4. **GitLens** - GitKraken
5. **Docker** - Microsoft
6. **PostgreSQL** -cjhowe7
7. **Thunder Client** (for API testing) - Ranga Vadhineni
8. **Alpine JS Syntax Highlighting** - Luke Edwards

### VS Code Settings

Create `.vscode/settings.json`:

```json
{
    "python.defaultInterpreterPath": "${workspaceFolder}/venv/bin/python",
    "python.formatting.provider": "black",
    "python.linting.enabled": true,
    "python.linting.pylintEnabled": true,
    "python.linting.flake8Enabled": false,
    "python.testing.pytestEnabled": true,
    "python.testing.pytestArgs": ["tests/"],
    "editor.formatOnSave": true,
    "editor.codeActionsOnSave": {
        "source.organizeImports": true
    },
    "files.exclude": {
        "**/__pycache__": true,
        "**/.pytest_cache": true,
        "**/.mypy_cache": true,
        "**/.venv": true
    }
}
```

---

## Project Structure

```
booklet5/
├── app/                          # Main application
│   ├── __init__.py
│   ├── main.py                  # FastAPI/Flask entry point
│   ├── database.py              # Database connection
│   ├── models.py                # SQLAlchemy ORM models
│   ├── schemas.py               # Pydantic validation schemas
│   ├── security.py              # Auth, JWT, encryption
│   ├── crud/                   # Database operations
│   ├── routers/                # API routes
│   ├── templates/              # Jinja2 templates (if using FastAPI)
│   └── static/                 # Static assets (CSS, JS, images)
│
├── tests/                      # Test suite
│   ├── unit/                  # Unit tests
│   ├── integration/           # Integration tests
│   ├── e2e/                  # End-to-end tests
│   └── conftest.py           # Pytest fixtures
│
├── scripts/                   # Utility scripts
│   ├── seed_data.py          # Seed initial data
│   ├── create_admin.py       # Create admin user
│   └── migrate_data.py       # Data migration scripts
│
├── docs/                     # Documentation
│   ├── api/                 # API documentation
│   ├── architecture/        # Architecture diagrams
│   └── guides/              # User guides
│
├── .env.example             # Environment template
├── .gitignore              # Git ignore file
├── requirements.txt        # Production dependencies
├── requirements-dev.txt     # Development dependencies
├── alembic.ini             # Database migrations config
├── pyproject.toml          # Project config (optional)
└── README.md               # Project overview
```

---

## Common Development Tasks

### 1. Create a New API Endpoint

```python
# In app/routers/products.py

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from app.database import get_db
from app import schemas, crud
from app.security import get_current_user

router = APIRouter()

@router.get("/", response_model=List[schemas.Product])
async def list_products(
    skip: int = 0,
    limit: int = 50,
    db: Session = Depends(get_db),
    user = Depends(get_current_user)
):
    """List all products"""
    products = crud.product.get_multi(
        db,
        tenant_id=user.tenant_id,
        skip=skip,
        limit=limit
    )
    return products

@router.post("/", response_model=schemas.Product, status_code=201)
async def create_product(
    product_data: schemas.ProductCreate,
    db: Session = Depends(get_db),
    user = Depends(get_current_user)
):
    """Create new product"""
    product = crud.product.create(
        db,
        obj_in=product_data,
        tenant_id=user.tenant_id
    )
    return product
```

### 2. Create a New Database Model

```python
# In app/models.py

from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

class Product(Base):
    """Product model"""
    __tablename__ = "products"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    sku = Column(String(100), unique=True, index=True)
    description = Column(String(500), nullable=True)
    purchase_price = Column(Float, default=0.0)
    sales_price = Column(Float, default=0.0)
    stock_quantity = Column(Integer, default=0)

    tenant_id = Column(Integer, ForeignKey("tenants.id"), nullable=False)
    branch_id = Column(Integer, ForeignKey("branches.id"), nullable=False)

    category_id = Column(Integer, ForeignKey("categories.id"), nullable=True)
    category = relationship("Category", back_populates="products")

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
```

### 3. Create a New CRUD Function

```python
# In app/crud/crud_product.py

from typing import List, Optional
from sqlalchemy.orm import Session
from app import models
from app.schemas.product import ProductCreate, ProductUpdate

class CRUDProduct:
    def get(self, db: Session, id: int) -> Optional[models.Product]:
        """Get product by ID"""
        return db.query(models.Product).filter(
            models.Product.id == id
        ).first()

    def get_multi(
        self,
        db: Session,
        tenant_id: int,
        skip: int = 0,
        limit: int = 100,
        search: str = None
    ) -> List[models.Product]:
        """Get multiple products"""
        query = db.query(models.Product).filter(
            models.Product.tenant_id == tenant_id
        )

        if search:
            query = query.filter(
                models.Product.name.ilike(f"%{search}%")
            )

        return query.offset(skip).limit(limit).all()

    def create(
        self,
        db: Session,
        obj_in: ProductCreate,
        tenant_id: int
    ) -> models.Product:
        """Create new product"""
        db_obj = models.Product(**obj_in.dict(), tenant_id=tenant_id)
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def update(
        self,
        db: Session,
        db_obj: models.Product,
        obj_in: ProductUpdate
    ) -> models.Product:
        """Update product"""
        for field, value in obj_in.dict(exclude_unset=True).items():
            setattr(db_obj, field, value)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def delete(self, db: Session, id: int) -> models.Product:
        """Delete product"""
        obj = db.query(models.Product).get(id)
        db.delete(obj)
        db.commit()
        return obj

product = CRUDProduct()
```

### 4. Create a Database Migration

```bash
# Generate migration from model changes
alembic revision --autogenerate -m "add products table"

# Apply migration
alembic upgrade head

# Rollback migration
alembic downgrade -1
```

### 5. Add a New Page/Route

```python
# In app/routes/customers.py (Flask)

from flask import Blueprint, render_template, redirect, url_for
from app.services.api import api_client

bp = Blueprint('customers', __name__)

@bp.route('/')
def list_customers():
    """Customers list page"""
    customers = api_client.get('/api/v1/customers/')
    return render_template('customers/list.html', customers=customers)

@bp.route('/new')
def new_customer():
    """New customer form"""
    return render_template('customers/new.html')
```

### 6. Run Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=app --cov-report=html

# Run specific test file
pytest tests/unit/test_crud_customer.py

# Run specific test
pytest tests/unit/test_crud_customer.py::test_create_customer

# Run with verbose output
pytest -v

# Run and stop on first failure
pytest -x
```

---

## Testing

### Unit Tests

```python
# tests/unit/test_crud_customer.py

import pytest
from sqlalchemy.orm import Session
from app import crud, schemas
from app.models import Customer

def test_create_customer(db: Session):
    """Test customer creation"""
    customer_data = schemas.CustomerCreate(
        name="Test Customer",
        email="test@example.com",
        phone="1234567890"
    )

    customer = crud.customer.create(
        db,
        obj_in=customer_data,
        tenant_id=1
    )

    assert customer.id is not None
    assert customer.name == "Test Customer"
    assert customer.email == "test@example.com"

def test_get_customer(db: Session):
    """Test getting customer by ID"""
    # Create customer first
    customer = crud.customer.create(
        db,
        obj_in=schemas.CustomerCreate(name="Test"),
        tenant_id=1
    )

    # Get customer
    retrieved = crud.customer.get(db, id=customer.id)

    assert retrieved is not None
    assert retrieved.id == customer.id
    assert retrieved.name == "Test"
```

### Integration Tests

```python
# tests/integration/test_api_customers.py

from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_list_customers(client, auth_headers):
    """Test GET /api/v1/customers/"""
    response = client.get(
        "/api/v1/customers/",
        headers=auth_headers
    )

    assert response.status_code == 200
    assert isinstance(response.json(), list)

def test_create_customer(client, auth_headers):
    """Test POST /api/v1/customers/"""
    data = {
        "name": "New Customer",
        "email": "new@example.com"
    }

    response = client.post(
        "/api/v1/customers/",
        json=data,
        headers=auth_headers
    )

    assert response.status_code == 201
    assert response.json()["name"] == "New Customer"
```

### Pytest Fixtures

```python
# tests/conftest.py

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from fastapi.testclient import TestClient

from app.main import app
from app.database import get_db, Base
from app.models import User
from app.security import create_access_token

# Test database
SQLALCHEMY_TEST_DATABASE_URL = "sqlite:///./test.db"
engine = create_engine(SQLALCHEMY_TEST_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

@pytest.fixture(scope="function")
def db():
    """Create test database session"""
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()
        Base.metadata.drop_all(bind=engine)

@pytest.fixture(scope="function")
def client(db):
    """Create test client with database override"""
    def override_get_db():
        try:
            yield db
        finally:
            pass

    app.dependency_overrides[get_db] = override_get_db
    yield TestClient(app)
    app.dependency_overrides.clear()

@pytest.fixture
def auth_headers(client):
    """Create authenticated user and return headers"""
    # Create test user
    user_data = {
        "email": "test@example.com",
        "username": "testuser",
        "hashed_password": "$2b$12$...",  # bcrypt hash
        "is_superuser": True,
        "tenant_id": 1
    }
    db.add(User(**user_data))
    db.commit()

    token = create_access_token(subject="testuser")
    return {"Authorization": f"Bearer {token}"}
```

---

## Debugging

### Using VS Code Debugger

Create `.vscode/launch.json`:

```json
{
    "version": "0.2.0",
    "configurations": [
        {
            "name": "Python: FastAPI",
            "type": "python",
            "request": "launch",
            "module": "uvicorn",
            "args": [
                "app.main:app",
                "--reload",
                "--host", "0.0.0.0",
                "--port", "8000"
            ],
            "envFile": "${workspaceFolder}/.env",
            "console": "integratedTerminal"
        }
    ]
}
```

### Logging

```python
# In your route handlers
import logging

logger = logging.getLogger(__name__)

@router.post("/customers")
async def create_customer(customer_data: CustomerCreate):
    logger.info(f"Creating customer: {customer_data.name}")
    try:
        customer = crud.customer.create(db, obj_in=customer_data)
        logger.info(f"Customer created with ID: {customer.id}")
        return customer
    except Exception as e:
        logger.error(f"Failed to create customer: {e}")
        raise
```

---

## Git Workflow

### Branch Naming

```
feature/           # New features
  feature/add-customer-export
  feature/pos-module

bugfix/           # Bug fixes
  bugfix/invoice-calculation-error
  bugfix/login-redirect

hotfix/           # Production hotfixes
  hotfix/security-patch
  hotfix/payment-failure

refactor/         # Code refactoring
  refactor/optimize-queries
  refactor/split-models-file
```

### Commit Message Format

```
type(scope): subject

body (optional)

footer (optional)
```

**Types:**
- `feat` - New feature
- `fix` - Bug fix
- `docs` - Documentation changes
- `style` - Code style (formatting, etc.)
- `refactor` - Code refactoring
- `test` - Adding/updating tests
- `chore` - Maintenance tasks
- `perf` - Performance improvements

**Examples:**
```
feat(customers): add bulk import from CSV

- Add CSV upload endpoint
- Parse and validate CSV data
- Create customers in bulk
- Return import summary with errors

Closes #123
```

```
fix(invoices): correct tax calculation for discounts

Tax was being calculated on subtotal including discount
instead of subtotal before discount. Fixed calculation order.

Fixes #456
```

---

## Useful Commands

```bash
# Database
alembic revision --autogenerate -m "description"  # Create migration
alembic upgrade head                              # Apply migrations
alembic downgrade -1                              # Rollback one migration
alembic history                                   # Show migration history

# Testing
pytest                                           # Run all tests
pytest --cov=app --cov-report=html              # With coverage
pytest -k "test_create"                         # Run matching tests
pytest -x                                       # Stop on first failure
pytest -v                                       # Verbose output

# Code Quality
black app/                                      # Format code
isort app/                                      # Sort imports
flake8 app/                                     # Lint code
mypy app/                                       # Type checking
safety check                                    # Check for security vulnerabilities

# Docker
docker-compose up                                # Start all services
docker-compose up -d                            # Start detached
docker-compose down                              # Stop and remove
docker-compose logs -f backend                   # Follow backend logs
docker-compose exec backend bash                 # Enter backend container
docker-compose exec db psql -U booklet booklet    # Connect to PostgreSQL

# Development
uvicorn app.main:app --reload                    # Run dev server
python scripts/seed_data.py                     # Seed initial data
python scripts/create_admin.py                 # Create admin user
```

---

## Troubleshooting

### Database Connection Issues

```bash
# Check PostgreSQL is running
sudo service postgresql status

# Check connection
psql -U booklet -d booklet_dev

# Reset database
dropdb booklet_dev
createdb booklet_dev -U booklet
alembic upgrade head
```

### Import Errors

```bash
# Clear Python cache
find . -type d -name __pycache__ -exec rm -r {} +
find . -type f -name "*.pyc" -delete

# Reinstall dependencies
pip install --force-reinstall -r requirements.txt
```

### Migration Issues

```bash
# Stamp current state
alembic stamp head

# Reset migrations (CAUTION: drops all tables)
alembic downgrade base
alembic upgrade head
```

### Port Already in Use

```bash
# Find process using port
lsof -i :8000  # macOS/Linux
netstat -ano | findstr :8000  # Windows

# Kill process
kill -9 <PID>
```

---

## Resources

- **FastAPI Docs:** https://fastapi.tiangolo.com
- **SQLAlchemy Docs:** https://docs.sqlalchemy.org
- **Pytest Docs:** https://docs.pytest.org
- **HTMX Docs:** https://htmx.org
- **Alpine.js Docs:** https://alpinejs.dev
- **Tailwind CSS:** https://tailwindcss.com

---

*For questions or help, reach out to the development team or create an issue on GitHub.*







# Planex SaaS ERP & Accounting Software
## Technical Documentation & Developer Guide

**Project Name:** Planex (Plan Next Excellence)
**Version:** Development/Pre-Release
**Last Updated:** 2026-02-13

---

## Table of Contents

1. [Project Overview](#project-overview)
2. [Technology Stack](#technology-stack)
3. [Architecture](#architecture)
4. [Database Models](#database-models)
5. [API Routes & Features](#api-routes--features)
6. [Authentication & Security](#authentication--security)
7. [Permission System](#permission-system)
8. [AI Integration (Jarvis)](#ai-integration-jarvis)
9. [Analytics & Reporting](#analytics--reporting)
10. [Installation & Setup](#installation--setup)
11. [Future Development Roadmap](#future-development-roadmap)
12. [Advanced Features Planning](#advanced-features-planning)

---

## Project Overview

Planex is a comprehensive **SaaS-based Accounting & ERP (Enterprise Resource Planning)** software solution designed for multi-branch businesses. It provides a full suite of financial management tools including:

- **Double-entry bookkeeping** with Chart of Accounts
- **Multi-branch/multi-currency** support
- **Sales & Purchases** management with invoicing
- **Inventory management** with stock tracking
- **HR & Payroll** with PAYE/Pension calculations
- **Fixed Assets** with depreciation tracking
- **Budgeting** and expense management
- **AI-powered Business Analyst (Jarvis)** for natural language queries
- **Advanced Analytics** with forecasting and comparison tools
- **Financial Reporting** (P&L, Balance Sheet, Trial Balance, Aging reports)

---

## Technology Stack

### Backend Framework
- **FastAPI** - Modern, high-performance Python web framework
- **Uvicorn/Gunicorn** - ASGI server for production deployment
- **Python 3.10+** - Core language

### Database & ORM
- **SQLite** - Default database (development)
- **SQLAlchemy** - Python SQL toolkit and ORM
- **PostgreSQL (psycopg2-binary)** - Production-ready alternative

### Security & Authentication
- **python-jose[cryptography]** - JWT token handling
- **passlib + bcrypt** - Password hashing
- **python-dotenv** - Environment variable management
- **Fernet (cryptography)** - API key encryption

### Frontend & Templating
- **Jinja2** - Server-side HTML templating
- **HTMX** - Dynamic interactivity without heavy JavaScript
- **Tailwind CSS** - Utility-first CSS framework (implied from class names)
- **Markdown (python-markdown)** - For AI response formatting

### AI & Analytics
- **Google Generative AI (gemini-2.5-flash)** - AI provider option
- **Zai SDK (zai-sdk)** - Alternative AI provider (glm-4.5-flash)
- **NumPy** - Numerical computing for analytics
- **Scikit-learn** - Machine learning for cash flow forecasting

### Document Generation
- **WeasyPrint** - HTML to PDF conversion for reports
- **openpyxl** - Excel file generation for exports

### Email
- **FastAPI-Mail** - Email sending capabilities

### Utilities
- **python-dateutil** - Advanced date/datetime handling
- **python-multipart** - Form data handling
- **pydantic** - Data validation
- **email-validator** - Email format validation

---

## Architecture

### Directory Structure

```
booklet5/
├── app/
│   ├── __init__.py
│   ├── main.py                 # FastAPI application entry point
│   ├── database.py             # Database connection & session management
│   ├── models.py               # SQLAlchemy ORM models (all tables)
│   ├── schemas.py              # Pydantic schemas for validation
│   ├── security.py             # Authentication, encryption, JWT
│   ├── ai_providers.py         # AI provider abstraction (Gemini, Zai)
│   ├── email_utils.py          # Email configuration & sending
│   ├── templating.py           # Jinja2 templates setup
│   │
│   ├── crud/                   # Database operations (CRUD functions)
│   │   ├── __init__.py
│   │   ├── account.py          # Chart of Accounts operations
│   │   ├── analytics.py        # Analytics calculations
│   │   ├── banking.py          # Bank accounts & reconciliation
│   │   ├── budget.py           # Budget management
│   │   ├── business.py         # Business operations
│   │   ├── cashbook.py         # Cash/Bank transactions
│   │   ├── customer.py         # Customer management
│   │   ├── employee.py         # HR & Payroll
│   │   ├── expenses.py         # Expense tracking
│   │   ├── fixed_assets.py     # Asset depreciation
│   │   ├── inventory.py       # Product & stock management
│   │   ├── journal.py          # Journal vouchers
│   │   ├── ledger.py           # General ledger queries
│   │   ├── other_income.py     # Non-sales income
│   │   ├── purchase.py         # Purchase bills & debit notes
│   │   ├── reports.py          # Report data aggregation
│   │   ├── sales.py            # Sales invoices & credit notes
│   │   ├── user.py             # User management
│   │   ├── vendor.py          # Vendor/supplier management
│   │   ├── branch.py           # Branch operations
│   │   ├── role.py             # Role & permission assignments
│   │   └── permission.py       # Permission checks
│   │
│   ├── routers/                 # API route handlers
│   │   ├── __init__.py
│   │   ├── accounting.py       # Chart of Accounts, General Ledger, P&L, BS
│   │   ├── analytics.py        # Analytics dashboard & tools
│   │   ├── auth.py            # Login, signup, logout
│   │   ├── banking.py          # Bank accounts & transfers
│   │   ├── branches.py        # Branch management
│   │   ├── budget.py           # Budget operations
│   │   ├── customers.py       # Customer CRUD
│   │   ├── dashboard.py       # Main dashboard
│   │   ├── expenses.py        # Expense tracking
│   │   ├── fixed_assets.py    # Fixed assets & depreciation
│   │   ├── hr.py             # Employee & payroll management
│   │   ├── inventory.py       # Product & stock management
│   │   ├── jarvis.py         # AI chat interface
│   │   ├── journal.py        # Journal voucher entries
│   │   ├── onboarding.py     # Data import & opening balances
│   │   ├── other_income.py   # Other income tracking
│   │   ├── purchases.py      # Purchase bills & debit notes
│   │   ├── reports.py        # Financial reports
│   │   ├── roles.py          # Role management
│   │   ├── sales.py          # Sales invoices & credit notes
│   │   ├── settings_ai.py   # AI configuration
│   │   ├── settings_business.py # Business settings
│   │   ├── settings_user.py  # User preferences
│   │   ├── team.py           # User invitations
│   │   └── vendors.py        # Vendor CRUD
│   │
│   ├── templates/              # Jinja2 HTML templates
│   │   ├── _shared/           # Shared components (layouts, sidebar)
│   │   ├── auth/              # Login/signup pages
│   │   ├── dashboard/         # Dashboard templates
│   │   ├── accounting/        # Accounting pages
│   │   ├── analytics/         # Analytics tools
│   │   ├── banking/           # Bank management
│   │   ├── budgeting/         # Budget templates
│   │   ├── crm/               # Customer/vendor pages
│   │   ├── expenses/          # Expense pages
│   │   ├── fixed_assets/      # Fixed asset pages
│   │   ├── hr/                # Payroll pages
│   │   ├── inventory/          # Product management
│   │   ├── jarvis/            # AI chat interface
│   │   ├── onboarding/        # Data import wizard
│   │   ├── purchases/         # Purchase management
│   │   ├── reports/           # Financial reports
│   │   ├── sales/             # Sales management
│   │   ├── settings/          # Settings pages
│   │   └── email/             # Email templates
│   │
│   └── static/                 # Static assets
│       ├── js/
│       │   └── main.js        # Custom JavaScript (HTMX extensions)
│       └── css/               # Stylesheets
│
├── saas.db                    # SQLite database file
├── requirements.txt            # Python dependencies
├── .env                       # Environment variables (not in repo)
├── run_daily_tasks.py         # Scheduled task runner (depreciation, bad debt)
├── code.py                    # Code file consolidator utility
├── code.txt                   # Consolidated code output
├── plan.txt                   # Project notes
└── .claude/                   # Claude Code settings
```

### Key Design Patterns

#### 1. Multi-Tenancy with Data Isolation
- **Business** is the top-level entity
- Each business has multiple **Branches**
- Users are assigned roles per-branch (UserBranchRole junction table)
- Superusers bypass branch restrictions

#### 2. Double-Entry Bookkeeping
- **LedgerEntry** is the central transaction table
- Every financial transaction creates balanced debit/credit entries
- **JournalVoucher** groups related ledger entries
- Automatic posting from invoices, expenses, payments, etc.

#### 3. Permission-Based Access Control
- **Granular permissions** (e.g., `sales:create`, `accounting:edit`)
- **Role-based**: Roles aggregate permissions
- **Branch-scoped**: Users have different roles per branch
- **PermissionChecker** dependency for route protection

#### 4. AI-Provider Pattern
- Abstract **AIProvider** protocol
- **GeminiProvider** and **ZaiProvider** implementations
- Easy to add new AI providers

---

## Database Models

### Core Business Models

#### Business
```python
- id: int (PK)
- name: str (unique)
- plan: str (default: "basic")           # Subscription tier
- is_vat_registered: bool
- vat_rate: float
- depreciation_day: int                    # Day of month for auto depreciation
- auto_depreciate: bool
- auto_write_off_bad_debts: bool
- bad_debt_age_days: int
- ai_provider: str (nullable)              # "gemini" or "zai"
- encrypted_api_key: str (nullable)        # Fernet-encrypted API key
```

#### User
```python
- id: int (PK)
- username: str (unique, indexed)
- email: str (unique, indexed)
- hashed_password: str
- is_superuser: bool
- business_id: int (FK → businesses)
```

#### Branch
```python
- id: int (PK)
- name: str
- currency: str (default: "USD")
- is_default: bool
- business_id: int (FK → businesses)
- UniqueConstraint: (business_id, name)
```

#### UserBranchRole (Junction Table)
```python
- user_id: int (PK, FK → users)
- branch_id: int (PK, FK → branches)
- role_id: int (PK, FK → roles)
```

### Permission System Models

#### Role
```python
- id: int (PK)
- name: str
- description: str (nullable)
- is_system: bool
- business_id: int (FK → businesses)
```

#### Permission
```python
- id: int (PK)
- name: str (unique)                      # e.g., "sales:create"
- category: str                            # e.g., "Sales"
```

#### RolePermission (Junction Table)
```python
- role_id: int (PK, FK → roles)
- permission_id: int (PK, FK → permissions)
```

### Accounting Models

#### Account (Chart of Accounts)
```python
- id: int (PK)
- name: str
- type: AccountType (Enum)               # Asset, Liability, Equity, Revenue, Expense
- description: str (nullable)
- is_system_account: bool                 # Cannot delete system accounts
- business_id: int (FK → businesses)
- is_active: bool
```

**AccountType Enum:**
- `ASSET` - Cash, bank, receivables, inventory, fixed assets
- `LIABILITY` - Payables, loans, statutory liabilities
- `EQUITY` - Owner's equity, retained earnings
- `REVENUE` - Sales, other income
- `EXPENSE` - Cost of sales, operating expenses

#### LedgerEntry
```python
- id: int (PK)
- transaction_date: date
- description: str
- debit: float (default: 0.0)
- credit: float (default: 0.0)
- account_id: int (FK → accounts)
- vendor_id: int (FK → vendors, nullable)
- customer_id: int (FK → customers, nullable)
- purchase_bill_id: int (FK → purchase_bills, nullable)
- debit_note_id: int (FK → debit_notes, nullable)
- sales_invoice_id: int (FK → sales_invoices, nullable)
- credit_note_id: int (FK → credit_notes, nullable)
- payslip_id: int (FK → payslips, nullable)
- other_income_id: int (FK → other_incomes, nullable)
- fund_transfer_id: int (FK → fund_transfers, nullable)
- journal_voucher_id: int (FK → journal_vouchers, nullable)
- branch_id: int (FK → branches)
- is_reconciled: bool
- reconciliation_id: int (FK → bank_reconciliations, nullable)
```

#### JournalVoucher
```python
- id: int (PK)
- voucher_number: str
- transaction_date: date
- description: text (nullable)
- business_id: int (FK → businesses)
- branch_id: int (FK → branches)
- → LedgerEntry[] (one-to-many)
```

### CRM Models

#### Customer
```python
- id: int (PK)
- name: str
- email: str (nullable)
- phone: str (nullable)
- address: text (nullable)
- created_at: datetime
- business_id: int (FK → businesses)
- branch_id: int (FK → branches)
- → SalesInvoice[] (one-to-many)
- → CreditNote[] (one-to-many)
```

#### Vendor
```python
- id: int (PK)
- name: str
- email: str (nullable)
- phone: str (nullable)
- address: text (nullable)
- created_at: datetime
- business_id: int (FK → businesses)
- branch_id: int (FK → branches)
```

#### Category (Product Categories)
```python
- id: int (PK)
- name: str
- description: str (nullable)
- business_id: int (FK → businesses)
- branch_id: int (FK → branches)
- → Product[] (one-to-many)
```

### Inventory Models

#### Product
```python
- id: int (PK)
- name: str
- sku: str (nullable, indexed)
- unit: str (nullable)                    # e.g., "pcs", "kg", "liters"
- purchase_price: float
- sales_price: float
- opening_stock: int (default: 0)
- stock_quantity: int (default: 0)
- branch_id: int (FK → branches)
- category_id: int (FK → categories)
- → StockAdjustment[] (one-to-many)
```

#### StockAdjustment
```python
- id: int (PK)
- product_id: int (FK → products)
- quantity_change: int                    # Positive or negative
- reason: str
- created_at: datetime
- user_id: int (FK → users)
```

### Sales Models

#### SalesInvoice
```python
- id: int (PK)
- invoice_number: str
- invoice_date: date
- due_date: date (nullable)
- sub_total: float
- vat_amount: float
- total_amount: float
- paid_amount: float (default: 0.0)
- status: str (default: "Unpaid")         # Unpaid, Partially Paid, Paid, Written Off
- customer_id: int (FK → customers)
- branch_id: int (FK → branches)
- business_id: int (FK → businesses)
- UniqueConstraint: (business_id, invoice_number)
- → SalesInvoiceItem[] (one-to-many)
```

#### SalesInvoiceItem
```python
- id: int (PK)
- sales_invoice_id: int (FK → sales_invoices)
- product_id: int (FK → products)
- quantity: float
- price: float
- returned_quantity: float (default: 0.0)
```

#### CreditNote
```python
- id: int (PK)
- credit_note_number: str
- customer_id: int (FK → customers)
- credit_note_date: date
- total_amount: float (default: 0.0)
- reason: str (nullable)
- business_id: int (FK → businesses)
- branch_id: int (FK → branches)
- → CreditNoteItem[] (one-to-many)
```

#### CreditNoteItem
```python
- id: int (PK)
- credit_note_id: int (FK → credit_notes)
- product_id: int (FK → products)
- quantity: float
- price: float
```

### Purchase Models

#### PurchaseBill
```python
- id: int (PK)
- bill_number: str
- bill_date: date
- due_date: date (nullable)
- sub_total: float
- vat_amount: float
- total_amount: float
- paid_amount: float (default: 0.0)
- status: str (default: "Unpaid")         # Unpaid, Partially Paid, Paid
- vendor_id: int (FK → vendors)
- branch_id: int (FK → branches)
- business_id: int (FK → businesses)
- UniqueConstraint: (business_id, bill_number)
- → PurchaseBillItem[] (one-to-many)
```

#### PurchaseBillItem
```python
- id: int (PK)
- purchase_bill_id: int (FK → purchase_bills)
- product_id: int (FK → products)
- quantity: float
- price: float
- returned_quantity: float (default: 0.0)
```

#### DebitNote
```python
- id: int (PK)
- debit_note_number: str
- vendor_id: int (FK → vendors)
- debit_note_date: date
- total_amount: float (default: 0.0)
- reason: str (nullable)
- business_id: int (FK → businesses)
- branch_id: int (FK → branches)
- → DebitNoteItem[] (one-to-many)
```

#### DebitNoteItem
```python
- id: int (PK)
- debit_note_id: int (FK → debit_notes)
- product_id: int (FK → products)
- quantity: float
- price: float
```

### HR & Payroll Models

#### Employee
```python
- id: int (PK)
- full_name: str
- email: str (indexed)
- phone_number: str (nullable)
- address: text (nullable)
- hire_date: date
- is_active: bool (default: True)
- termination_date: date (nullable)
- business_id: int (FK → businesses)
- branch_id: int (FK → branches)
- → PayrollConfig (one-to-one)
- → Payslip[] (one-to-many)
```

#### PayrollConfig
```python
- id: int (PK)
- employee_id: int (FK → employees, unique)
- gross_salary: float
- pay_frequency: PayFrequency (Enum)
- paye_rate: float (nullable)              # PAYE tax rate
- pension_employee_rate: float (nullable)
- pension_employer_rate: float (nullable)
```

**PayFrequency Enum:** `MONTHLY`, `WEEKLY`, `BI_WEEKLY`

#### Payslip
```python
- id: int (PK)
- employee_id: int (FK → employees)
- pay_period_start: date
- pay_period_end: date
- pay_date: date
- gross_pay: float
- paye_deduction: float (default: 0.0)
- pension_employee_deduction: float (default: 0.0)
- pension_employer_contribution: float (default: 0.0)
- total_deductions: float (default: 0.0)
- net_pay: float
- → PayslipAddition[] (one-to-many)
- → PayslipDeduction[] (one-to-many)
- → LedgerEntry[] (one-to-many)
```

#### PayslipAddition
```python
- id: int (PK)
- payslip_id: int (FK → payslips)
- description: str
- amount: float
```

#### PayslipDeduction
```python
- id: int (PK)
- payslip_id: int (FK → payslips)
- description: str
- amount: float
```

### Fixed Assets Models

#### FixedAsset
```python
- id: int (PK)
- name: str
- description: text
- purchase_date: date
- purchase_cost: float
- depreciation_method: str (default: "straight_line")
- useful_life_years: int
- salvage_value: float (default: 0.0)
- asset_account_id: int (FK → accounts)
- accumulated_depreciation_account_id: int (FK → accounts)
- business_id: int (FK → businesses)
- branch_id: int (FK → branches)
- → DepreciationEntry[] (one-to-many)
```

#### DepreciationEntry
```python
- id: int (PK)
- asset_id: int (FK → fixed_assets)
- entry_date: date
- amount: float
- journal_voucher_id: int (FK → journal_vouchers)
```

### Budgeting Models

#### Budget
```python
- id: int (PK)
- name: str
- branch_id: int (FK → branches)
- start_date: date
- end_date: date
- created_at: datetime
- UniqueConstraint: (branch_id, name)
- → BudgetLine[] (one-to-many)
```

#### BudgetLine
```python
- id: int (PK)
- budget_id: int (FK → budgets)
- account_id: int (FK → accounts)
- amount: float
```

### Banking Models

#### BankAccount
```python
- id: int (PK)
- account_name: str
- bank_name: str (nullable)
- account_number: str (nullable, indexed)
- chart_of_account_id: int (FK → accounts, unique)
- branch_id: int (FK → branches)
- business_id: int (FK → businesses)
- last_reconciliation_date: date (nullable)
- last_reconciliation_balance: float (nullable)
- UniqueConstraint: (branch_id, account_name)
```

#### BankReconciliation
```python
- id: int (PK)
- account_id: int (FK → accounts)
- statement_date: date
- statement_balance: float
- reconciled_at: datetime
- business_id: int (FK → businesses)
- branch_id: int (FK → branches)
- → LedgerEntry[] (one-to-many)
```

#### FundTransfer
```python
- id: int (PK)
- transfer_date: date
- description: text (nullable)
- amount: float
- from_account_id: int (FK → accounts)
- to_account_id: int (FK → accounts)
- business_id: int (FK → businesses)
- branch_id: int (FK → branches)
- → LedgerEntry[] (one-to-many)
```

### Other Models

#### Expense
```python
- id: int (PK)
- expense_number: str
- expense_date: date
- category: str
- sub_total: float
- vat_amount: float
- amount: float
- description: text (nullable)
- paid_from_account_id: int (FK → accounts)
- expense_account_id: int (FK → accounts)
- vendor_id: int (FK → vendors, nullable)
- branch_id: int (FK → branches)
- business_id: int (FK → businesses)
- UniqueConstraint: (business_id, expense_number)
```

#### OtherIncome
```python
- id: int (PK)
- income_number: str (unique)
- income_date: date
- description: text (nullable)
- amount: float
- income_account_id: int (FK → accounts)      # Revenue account
- deposited_to_account_id: int (FK → accounts) # Asset account
- branch_id: int (FK → branches)
- business_id: int (FK → businesses)
- → LedgerEntry[] (one-to-many)
```

---

## API Routes & Features

### Authentication Routes (`/auth`)

| Route | Method | Description | Permissions |
|-------|--------|-------------|--------------|
| `/` | GET | Root/Login page | Public |
| `/login` | GET | Login page | Public |
| `/signup` | GET | Signup page | Public |
| `/signup` | POST | Create business, admin user, default branch, roles, chart of accounts | Public |
| `/token` | POST | Authenticate user, set JWT cookie | Public |
| `/logout` | GET | Clear JWT cookie, redirect | Authenticated |

**Signup Flow:**
1. Creates Business with provided name
2. Creates default "Admin" role with all permissions
3. Creates superuser account
4. Creates default "Main Branch"
5. Assigns admin role to user for main branch
6. Creates default chart of accounts
7. Logs user in automatically

### Dashboard Routes (`/dashboard`)

| Route | Method | Description | Permissions |
|-------|--------|-------------|--------------|
| `/dashboard` | GET | Main dashboard with KPIs | Authenticated |

**Dashboard KPIs:**
- Total Sales (period)
- Total Purchases (period)
- Total Expenses (period)
- Net Profit
- Bank/Cash balances
- Receivables/Payables aging summary

### Settings - Business (`/settings/business`)

| Route | Method | Description | Permissions |
|-------|--------|-------------|--------------|
| `/settings/business` | GET | Business settings page | Authenticated |
| `/settings/business/update` | POST | Update VAT, depreciation, bad debt settings | `business:edit` |

**Configurable Settings:**
- VAT registration & rate
- Depreciation day (for automated runs)
- Auto-depreciation toggle
- Bad debt write-off age (days)
- Auto bad debt write-off toggle

### Settings - AI (`/settings/ai`)

| Route | Method | Description | Permissions |
|-------|--------|-------------|--------------|
| `/settings/ai` | GET | AI configuration page | Authenticated |
| `/settings/ai/configure` | POST | Save AI provider and encrypted API key | Authenticated |

**Supported AI Providers:**
- **Gemini** (Google Generative AI - gemini-2.5-flash)
- **Zai** (Zai SDK - glm-4.5-flash)

### Settings - User (`/settings/user`)

| Route | Method | Description | Permissions |
|-------|--------|-------------|--------------|
| `/settings/user` | GET | User profile page | Authenticated |
| `/settings/user/update-profile` | POST | Update user details | Authenticated |
| `/settings/user/change-password` | POST | Change password | Authenticated |

### Branches (`/branches`)

| Route | Method | Description | Permissions |
|-------|--------|-------------|--------------|
| `/branches` | GET | Branch list page | `branches:view` |
| `/branches/new` | GET | New branch form | `branches:create` |
| `/branches` | POST | Create branch | `branches:create` |
| `/branches/{id}/edit` | GET | Edit branch form | `branches:edit` |
| `/branches/{id}` | PUT | Update branch | `branches:edit` |
| `/branches/{id}` | DELETE | Delete branch | `branches:delete` |

### Team Management (`/team`)

| Route | Method | Description | Permissions |
|-------|--------|-------------|--------------|
| `/team` | GET | Team members list | `users:view` |
| `/team/invite` | POST | Invite new user (sends email with temp password) | `users:create` |
| `/team/{user_id}/roles` | GET | User role assignments | `users:assign-roles` |
| `/team/{user_id}/roles` | POST | Update user's branch roles | `users:assign-roles` |
| `/team/{user_id}` | DELETE | Delete/deactivate user | `users:delete` |

### Roles (`/roles`)

| Route | Method | Description | Permissions |
|-------|--------|-------------|--------------|
| `/roles` | GET | Roles list page | `roles:view` |
| `/roles/new` | GET | New role form | `roles:create` |
| `/roles` | POST | Create role | `roles:create` |
| `/roles/{id}` | GET | Role detail with permissions | `roles:view` |
| `/roles/{id}/edit` | GET | Edit role form | `roles:edit` |
| `/roles/{id}` | PUT | Update role | `roles:edit` |
| `/roles/{id}` | DELETE | Delete role (cannot delete system roles) | `roles:delete` |

### Customers (`/customers`)

| Route | Method | Description | Permissions |
|-------|--------|-------------|--------------|
| `/customers` | GET | Customers list | `customers:view` |
| `/customers/new` | GET | New customer form | `customers:create` |
| `/customers` | POST | Create customer | `customers:create` |
| `/customers/{id}` | GET | Customer detail with sales history | `customers:view` |
| `/customers/{id}/edit` | GET | Edit customer form | `customers:edit` |
| `/customers/{id}` | PUT | Update customer | `customers:edit` |
| `/customers/{id}` | DELETE | Delete customer | `customers:delete` |

### Vendors (`/vendors`)

| Route | Method | Description | Permissions |
|-------|--------|-------------|--------------|
| `/vendors` | GET | Vendors list | `vendors:view` |
| `/vendors/new` | GET | New vendor form | `vendors:create` |
| `/vendors` | POST | Create vendor | `vendors:create` |
| `/vendors/{id}` | GET | Vendor detail with purchase history | `vendors:view` |
| `/vendors/{id}/edit` | GET | Edit vendor form | `vendors:edit` |
| `/vendors/{id}` | PUT | Update vendor | `vendors:edit` |
| `/vendors/{id}` | DELETE | Delete vendor | `vendors:delete` |

### Inventory (`/inventory`)

| Route | Method | Description | Permissions |
|-------|--------|-------------|--------------|
| `/inventory` | GET | Products list with stock levels | `inventory:view` |
| `/inventory/categories` | GET | Product categories | `inventory:view` |
| `/inventory/categories/new` | GET | New category form | `inventory:create` |
| `/inventory/categories` | POST | Create category | `inventory:create` |
| `/inventory/products/new` | GET | New product form | `inventory:create` |
| `/inventory/products` | POST | Create product | `inventory:create` |
| `/inventory/products/{id}` | GET | Product detail | `inventory:view` |
| `/inventory/products/{id}/edit` | GET | Edit product form | `inventory:edit` |
| `/inventory/products/{id}` | PUT | Update product | `inventory:edit` |
| `/inventory/products/{id}` | DELETE | Delete product | `inventory:delete` |
| `/inventory/products/{id}/adjust-stock` | POST | Adjust stock quantity | `inventory:adjust-stock` |

### Sales (`/sales`)

| Route | Method | Description | Permissions |
|-------|--------|-------------|--------------|
| `/sales` | GET | Sales invoices list | `sales:view` |
| `/sales/new` | GET | New invoice form | `sales:create` |
| `/sales` | POST | Create invoice (posts to ledger) | `sales:create` |
| `/sales/{id}` | GET | Invoice detail | `sales:view` |
| `/sales/{id}/edit` | GET | Edit invoice form | `sales:edit` |
| `/sales/{id}` | PUT | Update invoice | `sales:edit` |
| `/sales/{id}/credit-note` | GET | Credit note form | `sales:create_credit_note` |
| `/sales/{id}/credit-note` | POST | Create credit note | `sales:create_credit_note` |
| `/sales/credit-notes/{id}` | GET | Credit note detail | `sales:view` |

**Automatic Ledger Posting:**
- Debit: Customer Receivables / Cash
- Credit: Sales Revenue
- Debit: Cost of Goods Sold
- Credit: Inventory

### Purchases (`/purchases`)

| Route | Method | Description | Permissions |
|-------|--------|-------------|--------------|
| `/purchases` | GET | Purchase bills list | `purchases:view` |
| `/purchases/new` | GET | New bill form | `purchases:create` |
| `/purchases` | POST | Create bill (posts to ledger) | `purchases:create` |
| `/purchases/{id}` | GET | Bill detail | `purchases:view` |
| `/purchases/{id}/edit` | GET | Edit bill form | `purchases:edit` |
| `/purchases/{id}` | PUT | Update bill | `purchases:edit` |
| `/purchases/{id}/debit-note` | GET | Debit note form | `purchases:create_debit_note` |
| `/purchases/{id}/debit-note` | POST | Create debit note | `purchases:create_debit_note` |

**Automatic Ledger Posting:**
- Debit: Inventory / Expense
- Credit: Vendor Payables / Cash

### Expenses (`/expenses`)

| Route | Method | Description | Permissions |
|-------|--------|-------------|--------------|
| `/expenses` | GET | Expenses list | `expenses:view` |
| `/expenses/new` | GET | New expense form | `expenses:create` |
| `/expenses` | POST | Create expense | `expenses:create` |
| `/expenses/{id}` | GET | Expense detail | `expenses:view` |
| `/expenses/{id}/edit` | GET | Edit expense form | `expenses:edit` |
| `/expenses/{id}` | PUT | Update expense | `expenses:edit` |
| `/expenses/{id}` | DELETE | Delete expense | `expenses:delete` |

**Automatic Ledger Posting:**
- Debit: Expense Account
- Credit: Bank/Cash Account

### Banking (`/banking`)

| Route | Method | Description | Permissions |
|-------|--------|-------------|--------------|
| `/banking/bank-accounts` | GET | Bank accounts list | `bank:view` |
| `/banking/bank-accounts/new` | GET | New bank account form | `bank:create` |
| `/banking/bank-accounts` | POST | Create bank account | `bank:create` |
| `/banking/transfers/new` | GET | Fund transfer form | `bank:create` |
| `/banking/transfers` | POST | Transfer between accounts | `bank:create` |
| `/banking/recile/{account_id}` | GET | Reconciliation page | `bank:view` |
| `/banking/recile` | POST | Perform reconciliation | `bank:view` |

### Accounting (`/accounting`)

#### Chart of Accounts
| Route | Method | Description | Permissions |
|-------|--------|-------------|--------------|
| `/accounting/chart-of-accounts` | GET | COA page grouped by type | `accounting:view` |
| `/accounting/chart-of-accounts/new-form` | GET | Add account form partial | `accounting:create` |
| `/accounting/chart-of-accounts` | POST | Create account | `accounting:create` |
| `/accounting/chart-of-accounts/{id}/edit` | GET | Edit account form | `accounting:edit` |
| `/accounting/chart-of-accounts/{id}` | PUT | Update account | `accounting:edit` |
| `/accounting/chart-of-accounts/{id}` | DELETE | Delete account | `accounting:delete` |

#### General Ledger
| Route | Method | Description | Permissions |
|-------|--------|-------------|--------------|
| `/accounting/general-ledger` | GET | General ledger with filters | `accounting:view` |

**Filters:** Start date, End date, Account ID

#### Cash & Bank Management
| Route | Method | Description | Permissions |
|-------|--------|-------------|--------------|
| `/accounting/cash` | GET | Cash account detail | `accounting:view` |
| `/accounting/bank` | GET | Bank account selector & detail | `accounting:view` |
| `/accounting/cashbook` | GET | Unified cashbook view | `accounting:view` |
| `/accounting/cashbook/spend-money` | POST | Record expense/payment | `accounting:create` |
| `/accounting/cashbook/receive-money` | POST | Record income/receipt | `accounting:create` |

#### Financial Statements
| Route | Method | Description | Permissions |
|-------|--------|-------------|--------------|
| `/accounting/profit-and-loss` | GET | P&L Statement | `accounting:view` |
| `/accounting/balance-sheet` | GET | Balance Sheet | `accounting:view` |
| `/accounting/trial-balance` | GET | Trial Balance | `accounting:view` |

#### Payroll Liabilities
| Route | Method | Description | Permissions |
|-------|--------|-------------|--------------|
| `/accounting/payroll-liabilities` | GET | PAYE, Pension, Net Payables | `accounting:view` |
| `/accounting/payroll-liabilities/pay` | POST | Pay statutory liabilities | `accounting:create` |

#### Journal Vouchers
| Route | Method | Description | Permissions |
|-------|--------|-------------|--------------|
| `/accounting/journal` | GET | Journal vouchers list | `accounting:view` |
| `/accounting/journal/new` | GET | New voucher form | `accounting:create` |
| `/accounting/journal` | POST | Create journal entry | `accounting:create` |

### Fixed Assets (`/fixed-assets`)

| Route | Method | Description | Permissions |
|-------|--------|-------------|--------------|
| `/fixed-assets` | GET | Fixed assets list | `accounting:view` |
| `/fixed-assets` | POST | Create new asset | `accounting:create` |
| `/fixed-assets/{id}` | GET | Asset detail with depreciation | `accounting:view` |
| `/fixed-assets/run-depreciation` | POST | Run depreciation for all assets | `accounting:create` |
| `/fixed-assets/opening-balance` | POST | Create asset with opening accumulated depreciation | `accounting:create` |

**Depreciation Methods:** Straight-line, Double-declining balance

### HR & Payroll (`/hr`)

| Route | Method | Description | Permissions |
|-------|--------|-------------|--------------|
| `/hr` | GET | Employees list | `hr:view` |
| `/hr/new` | GET | New employee form | `hr:create` |
| `/hr` | POST | Create employee with payroll config | `hr:create` |
| `/hr/{id}` | GET | Employee detail | `hr:view` |
| `/hr/{id}/edit` | GET | Edit employee form | `hr:edit` |
| `/hr/{id}` | PUT | Update employee | `hr:edit` |
| `/hr/{id}` | DELETE | Terminate employee | `hr:delete` |
| `/hr/payslips` | GET | Payslips list | `hr:view` |
| `/hr/payslips/run` | GET | Run payroll wizard | `hr:run_payroll` |
| `/hr/payslips/run` | POST | Generate payslips for period | `hr:run_payroll` |

**Payroll Calculations:**
- PAYE deduction based on configured rate
- Pension (employee + employer contribution)
- Net pay = Gross - Total Deductions
- Automatic posting to Payroll Liabilities

### Budgeting (`/budgeting`)

| Route | Method | Description | Permissions |
|-------|--------|-------------|--------------|
| `/budgeting` | GET | Budgets list | `budgeting:view` |
| `/budgeting/new` | GET | New budget form | `budgeting:create` |
| `/budgeting` | POST | Create budget | `budgeting:create` |
| `/budgeting/{id}` | GET | Budget detail with actual vs budget | `budgeting:view` |
| `/budgeting/{id}/edit` | GET | Edit budget form | `budgeting:edit` |
| `/budgeting/{id}` | PUT | Update budget | `budgeting:edit` |
| `/budgeting/{id}` | DELETE | Delete budget | `budgeting:delete` |

### Other Income (`/other-income`)

| Route | Method | Description | Permissions |
|-------|--------|-------------|--------------|
| `/other-income` | GET | Other income list | `accounting:view` |
| `/other-income/new` | GET | New income form | `accounting:create` |
| `/other-income` | POST | Record other income | `accounting:create` |

### Reports (`/reports`)

| Route | Method | Description | Permissions |
|-------|--------|-------------|--------------|
| `/reports/consolidated-dashboard` | GET | Multi-branch dashboard (superusers) | `report:view` |
| `/reports/sales` | GET | Sales report with filters | `sales:view` |
| `/reports/purchase` | GET | Purchase report with filters | `purchases:view` |
| `/reports/expenses` | GET | Expense report with filters | `expenses:view` |
| `/reports/ar-aging` | GET | Accounts receivable aging | `report:view` |
| `/reports/ap-aging` | GET | Accounts payable aging | `report:view` |
| `/reports/excel/sales` | GET | Export sales to Excel | `sales:view` |
| `/reports/excel/purchase` | GET | Export purchases to Excel | `purchases:view` |
| `/reports/excel/expenses` | GET | Export expenses to Excel | `expenses:view` |
| `/reports/pdf/ar-aging` | GET | PDF aging report | `report:view` |

**Report Filters:** Date range, Customer/Vendor, Category, Branch

### Analytics (`/analytics`)

| Route | Method | Description | Permissions |
|-------|--------|-------------|--------------|
| `/analytics` | GET | Analytics hub | Authenticated |
| `/analytics/comparison` | GET | Comparison tool (bar/line charts) | Authenticated |
| `/analytics/financial-health` | GET | Financial ratios & trends | Authenticated |
| `/analytics/deep-dive` | GET | Deep dive analyzer (sunburst) | Authenticated |
| `/analytics/cash-flow-forecast` | GET | Cash flow forecaster | Authenticated |
| `/analytics/cash-flow-forecast/update` | POST | Update forecast with scenarios | Authenticated |

**Analytics Features:**
- **Comparison Tool:** Compare metrics (sales, profit, expenses) across months or branches
- **Financial Health:** Key ratios (GPM, NPM, Current Ratio) with 6-month trends
- **Deep Dive:** Sunburst breakdown of expenses/sales by category
- **Cash Flow Forecast:** ML-based prediction using linear regression + what-if scenarios

### AI Analyst - Jarvis (`/jarvis`)

| Route | Method | Description | Permissions |
|-------|--------|-------------|--------------|
| `/jarvis` | GET | Jarvis chat interface | `jarvis:ask` |
| `/jarvis/ask` | POST | Ask question, get AI response | `jarvis:ask` |

**Jarvis Features:**
- Natural language questions about business data
- Context-aware: receives filtered business data as JSON
- Supports SQL query understanding
- Markdown formatted responses with tables
- Security: Data filtered by user's branch permissions before sending to AI

### Onboarding (`/onboarding`)

| Route | Method | Description | Permissions |
|-------|--------|-------------|--------------|
| `/onboarding/data-importer` | GET | AI data importer page | Authenticated |
| `/onboarding/data-importer/analyze` | POST | AI parses raw data into JSON | Authenticated |
| `/onboarding/data-importer/import` | POST | Save imported data to DB | Authenticated |
| `/onboarding/opening-balances` | GET | Opening balances entry | Authenticated |
| `/onboarding/opening-balances` | POST | Save as journal voucher | Authenticated |

**AI Data Importer (Setter):**
- Paste raw data (Excel, CSV, tab-separated)
- AI maps columns to schema fields intelligently
- Preview before import
- Supports: Customers, Vendors, Products

---

## Authentication & Security

### JWT Token Authentication

**Token Generation (`security.create_access_token`):**
```python
{
    "sub": "username",  # Subject
    "exp": "datetime"   # Expiration
}
```

**Token Storage:** HTTP-only cookie (`access_token`)
**Expiration:** 30 minutes (configurable)
**Algorithm:** HS256

### Authentication Flow

1. **Login:** User submits username/password
2. **Verification:** `authenticate_user` checks hashed password
3. **Token Creation:** JWT created with username as subject
4. **Cookie Set:** Token stored in HTTP-only cookie
5. **Redirect:** Browser sent to `/dashboard`

### User Session Management

**`get_current_user` Dependency:**
1. Extracts token from `access_token` cookie
2. Decodes JWT and validates signature
3. Fetches user with all relations (`get_user_with_relations`)
4. Returns user object for route handlers

**`get_current_active_user` Dependency:**
1. Calls `get_current_user` first
2. Determines accessible branches:
   - **Superuser:** All branches in business
   - **Regular user:** Only assigned branches
3. Determines selected branch:
   - Reads `selected_branch_id` cookie
   - Validates user has access to that branch
   - Falls back to default branch or first accessible
4. Attaches `selected_branch` and `accessible_branches` to user

### Password Security

**Hashing:** bcrypt with `passlib`
**Cost Factor:** Default (12 rounds)
**Storage:** `hashed_password` column (never store plain text)

### API Key Encryption

**Method:** Fernet symmetric encryption
**Key:** Generated at runtime (`ENCRYPTION_KEY`)
**Usage:** AI provider API keys stored in `Business.encrypted_api_key`
**Functions:**
- `encrypt_data(data: str) -> str`
- `decrypt_data(encrypted_data: str) -> str`

### Security Middleware

**All authenticated routes require:**
```python
dependencies=[Depends(get_current_active_user)]
```

**Protected routes (with permissions):**
```python
dependencies=[
    Depends(get_current_active_user),
    Depends(PermissionChecker(["permission:name"]))
]
```

---

## Permission System

### Granular Permissions

**Format:** `resource:action`

**Current Permissions (47 total):**

| Category | Permissions |
|----------|-------------|
| **Users** | `users:view`, `users:create`, `users:edit`, `users:delete`, `users:assign-roles` |
| **Roles** | `roles:view`, `roles:create`, `roles:edit`, `roles:delete` |
| **Branches** | `branches:view`, `branches:create`, `branches:edit`, `branches:delete` |
| **Banking** | `bank:view`, `bank:create` |
| **Customers** | `customers:view`, `customers:create`, `customers:edit`, `customers:delete` |
| **Vendors** | `vendors:view`, `vendors:create`, `vendors:edit`, `vendors:delete` |
| **Inventory** | `inventory:view`, `inventory:create`, `inventory:edit`, `inventory:delete`, `inventory:adjust_stock` |
| **Purchases** | `purchases:view`, `purchases:create`, `purchases:edit`, `purchases:delete`, `purchases:create_debit_note` |
| **Sales** | `sales:view`, `sales:create`, `sales:edit`, `sales:delete`, `sales:create_credit_note` |
| **Expenses** | `expenses:view`, `expenses:create`, `expenses:edit`, `expenses:delete` |
| **Accounting** | `accounting:view`, `accounting:create`, `accounting:edit`, `accounting:delete` |
| **HR** | `hr:view`, `hr:create`, `hr:edit`, `hr:delete`, `hr:run_payroll` |
| **Budgeting** | `budgeting:view`, `budgeting:create`, `budgeting:edit`, `budgeting:delete` |
| **Reports** | `report:view` |
| **AI Analyst** | `jarvis:ask` |

### Permission Checking

**`PermissionChecker` Class:**
```python
class PermissionChecker:
    def __init__(self, required_permissions: List[str]):
        self.required_permissions = set(required_permissions)

    def __call__(self, user, db):
        # Superusers bypass all checks
        if user.is_superuser:
            return

        # Get user's permissions from roles
        user_permissions = crud.get_user_permissions(user, db)

        # Check all required permissions present
        if not self.required_permissions.issubset(user_permissions):
            raise HTTPException(status_code=403)
```

**Getting User Permissions:**
```python
# Aggregates all permissions from all roles across all branches
def get_user_permissions(user: User, db: Session) -> Set[str]:
    permissions = set()
    for assignment in user.roles:
        for rp in assignment.role.permissions:
            permissions.add(rp.permission.name)
    return permissions
```

### Data-Level Security

**Jarvis AI Data Filtering:**
- All business data fetched initially
- Filtered by user's accessible branches
- Only user's permissions are considered
- AI receives only sanitized data

**Report Data Filtering:**
- All reports support optional `branch_id` filter
- Non-superusers restricted to selected/accessible branches
- Consolidated reports superuser-only

---

## AI Integration (Jarvis)

### Architecture

```
User Question
    ↓
[jarvis.ask] endpoint
    ↓
Encrypt API Key → Decrypt
    ↓
Get AI Provider (Gemini/Zai)
    ↓
Build Prompt:
    - System Prompt (analyst persona)
    - Business Data (filtered JSON)
    - User Question
    ↓
AI Provider.ask()
    ↓
Markdown Response
    ↓
Rendered in Chat UI
```

### System Prompt

```
You are Jarvis, an expert financial and business analyst.
Your sole purpose is to answer questions based ONLY on JSON data provided.
Do not use any external knowledge. Do not browse internet.
If the answer cannot be found in the provided JSON, you must state that clearly.
Also you understand SQL queries, use your data to translate and answer accordingly.

Analyze the following JSON data which contains information about customers, vendors,
products, sales, purchases, and expenses for a business.

When providing your answer:
- Be concise and professional
- Use simple Markdown for formatting
- Perform calculations if necessary (totals, averages)
- Present lists of items clearly (no IDs unless asked, users are not programmers)
```

### AI Providers

#### GeminiProvider (Google)
```python
genai.configure(api_key=api_key)
model = genai.GenerativeModel('gemini-2.5-flash')
response = model.generate_content(full_prompt)
return response.text
```

#### ZaiProvider (Zai SDK)
```python
client = ZaiClient(api_key=api_key)
messages = [
    {"role": "system", "content": system_prompt + business_data},
    {"role": "user", "content": user_question}
]
response = client.chat.completions.create(
    model="glm-4.5-flash",
    messages=messages,
    temperature=0.5,
    max_tokens=4096
)
return response.choices[0].message.content
```

### Security in Jarvis

1. **API Key Encryption:** Stored encrypted in database, decrypted only at runtime
2. **Data Filtering:** Business data filtered by user's branch access
3. **Prompt Isolation:** Each request独立的 prompt
4. **No Training:** AI never stores or learns from user data

### Example Interactions

**Q:** "What were our total sales last month?"
**A:** Analyzes `sales_invoices` in data, sums `total_amount` for dates in range

**Q:** "Which customers owe us money?"
**A:** Filters invoices with status "Unpaid" or "Partially Paid", lists customers

**Q:** "Show me the top 5 products by revenue"
**A:** Aggregates sales by product, sorts, returns top 5

---

## Analytics & Reporting

### Analytics Modules

#### 1. Comparison Tool (`analytics/comparison_tool.html`)
- **Purpose:** Compare metrics across dimensions (time or branches)
- **Metrics Available:** Total Sales, Gross Profit, Net Profit, Total Expenses
- **Dimensions:** Month, Branch
- **Chart Type:** Bar chart (multiple series)
- **SQL Query:** Dynamic case statements for metric calculation

#### 2. Financial Health Scorecard (`analytics/financial_health.html`)
- **Purpose:** Key financial ratios with trend analysis
- **Ratios:**
  - Gross Profit Margin = (Gross Profit / Revenue) × 100
  - Net Profit Margin = (Net Profit / Revenue) × 100
  - Current Ratio = Current Assets / Current Liabilities
- **Trends:** 6-month historical trend line charts
- **Data Source:** P&L and Balance Sheet calculations

#### 3. Deep Dive Analyzer (`analytics/deep_dive.html`)
- **Purpose:** Hierarchical breakdown of metrics
- **Chart Type:** Sunburst chart
- **Metrics:** Total Expenses, Total Sales
- **Breakdown:** By category (expense categories, product categories)
- **Interactive:** Click segments to drill down

#### 4. Cash Flow Forecaster (`analytics/cash_flow_forecaster.html`)
- **Purpose:** Predict future cash position with ML
- **Method:** Linear Regression on 6 months historical data
- **Features:** Daily bank balance changes
- **Scenarios:** What-if adjustments (increase sales, reduce expenses, etc.)
- **Output:** Line chart with historical + forecasted + scenarios

### Report Modules

#### 1. Trial Balance (`reports.trial_balance`)
- **Output:** Debit/Credit balances for all accounts
- **Grouping:** By account type (Asset, Liability, Equity, Revenue, Expense)
- **Validation:** Debits = Credits (balanced books)
- **Filters:** As-of date, Branch

#### 2. Profit & Loss (`ledger.get_profit_and_loss_data`)
- **Sections:**
  - Revenue (Sales, Other Income)
  - Cost of Goods Sold
  - Gross Profit
  - Operating Expenses (by category)
  - Net Profit
- **Period:** User-defined date range
- **Comparison:** Actual vs Budget (if budget exists)

#### 3. Balance Sheet (`reports.get_balance_sheet_data`)
- **Sections:**
  - Current Assets (Cash, Bank, Receivables, Inventory)
  - Non-Current Assets (Fixed Assets - Accumulated Depreciation)
  - Current Liabilities (Payables, Statutory)
  - Non-Current Liabilities (Loans)
  - Equity (Capital, Retained Earnings)
- **Validation:** Assets = Liabilities + Equity

#### 4. Aging Reports (`reports.get_ar_aging_report`)
- **Buckets:** Current, 1-30, 31-60, 61-90, 90+ days
- **AR:** Unpaid/Partial sales invoices
- **AP:** Unpaid/Partial purchase bills
- **Calculations:** Days overdue = (Today - Due Date)

### Export Formats

#### Excel Export (`reports.export_to_excel`)
- **Library:** openpyxl
- **Features:**
  - Title row with bold font
  - Bold headers
  - Auto-width columns
  - Returns `BytesIO` buffer for download

#### PDF Export
- **Library:** WeasyPrint
- **Method:** HTML template → PDF
- **Features:** Professional formatting, company branding

---

## Installation & Setup

### Prerequisites

- Python 3.10 or higher
- pip (Python package manager)
- Git (optional, for version control)

### Step 1: Clone Repository

```bash
cd /path/to/your/projects
git clone <repository-url> booklet5
cd booklet5
```

### Step 2: Create Virtual Environment

```bash
# Windows
python -m venv venv
venv\Scripts\activate

# Linux/Mac
python3 -m venv venv
source venv/bin/activate
```

### Step 3: Install Dependencies

```bash
pip install -r requirements.txt
```

**Dependencies:**
```
fastapi
uvicorn
gunicorn
sqlalchemy
psycopg2-binary
python-jose[cryptography]
passlib
bcrypt==3.2.0
python-dotenv
jinja2
google-generativeai
zai-sdk
numpy
scikit-learn
weasyprint
openpyxl
python-dateutil
python-multipart
markdown
pydantic
email-validator
fastapi-mail
```

### Step 4: Environment Configuration

Create `.env` file in project root:

```env
# Database
DATABASE_URL=sqlite:///./saas.db

# Secret Key for JWT (generate your own!)
SECRET_KEY=your-random-secret-key-here

# Email Configuration (optional)
MAIL_USERNAME=your-email@example.com
MAIL_PASSWORD=your-app-password
MAIL_FROM=noreply@planex.com
MAIL_PORT=587
MAIL_SERVER=smtp.gmail.com
MAIL_STARTTLS=True
MAIL_SSL_TLS=False
```

### Step 5: Run Database Setup

```bash
python -c "from app.database import init_db; init_db()"
```

This creates:
- All tables with relationships
- Default permissions
- Default admin role (after signup)

### Step 6: Run Development Server

```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

**Access:** http://localhost:8000

### Step 7: Create First Account

1. Navigate to http://localhost:8000/signup
2. Enter:
   - Business Name
   - Your Email
   - Username
   - Password
3. System creates:
   - Business entity
   - Admin user (superuser)
   - Main Branch
   - Admin Role (all permissions)
   - Default Chart of Accounts
4. Auto-logs you in

### Step 8: Configure AI (Optional)

1. Go to Settings → AI Configuration
2. Choose provider: "Gemini" or "Zai"
3. Enter API Key (encrypted before storage)
4. Save
5. Test via Jarvis chat

### Production Deployment

#### Gunicorn + Uvicorn

```bash
gunicorn app.main:app \
    --workers 4 \
    --worker-class uvicorn.workers.UvicornWorker \
    --bind 0.0.0.0:8000 \
    --timeout 120 \
    --access-logfile - \
    --error-logfile -
```

#### PostgreSQL Migration

Update `.env`:
```env
DATABASE_URL=postgresql://user:password@localhost/planex_db
```

Update `database.py`:
```python
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./saas.db")

# For PostgreSQL
if DATABASE_URL.startswith("postgresql"):
    engine = create_engine(DATABASE_URL, pool_pre_ping=True)
else:
    # SQLite
    engine = create_engine(
        DATABASE_URL,
        connect_args={"check_same_thread": False}
    )

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
```

#### Scheduled Tasks (Cron)

Setup automated depreciation and bad debt write-off:

```bash
# Crontab entry
0 2 * * * /usr/bin/python3 /path/to/booklet5/run_daily_tasks.py
```

Runs daily at 2 AM to:
- Check for businesses with auto-depreciation enabled
- Run depreciation if today is configured day
- Write off bad debts past configured age

---

## Future Development Roadmap

### Immediate Priorities (Next 1-3 Months)

#### 1. Testing & Quality Assurance
- **Unit Tests:** Pytest for all CRUD functions
- **Integration Tests:** API route testing with TestClient
- **E2E Tests:** Playwright/Selenium for critical flows
- **Coverage Goal:** 80%+ code coverage

#### 2. Performance Optimization
- **Database Indexing:** Add indexes on foreign keys, date ranges
- **Query Optimization:** N+1 query elimination
- **Caching:** Redis for session/user data
- **Pagination:** All list views paginated

#### 3. Security Hardening
- **Rate Limiting:** Prevent brute force attacks
- **CSRF Protection:** Form token validation
- **Audit Logging:** Track all sensitive actions
- **2FA:** Two-factor authentication option

#### 4. Multi-Currency Enhancements
- **Exchange Rate Management:** Daily rates table
- **Currency Conversion:** Real-time balance conversion
- **Multi-Currency Reporting:** P&L in base currency
- **FX Gain/Loss:** Automatic calculation

### Medium-Term Features (3-6 Months)

#### 5. Advanced Reporting
- **Custom Report Builder:** Drag-and-drop report creator
- **Scheduled Reports:** Email reports periodically
- **Dashboard Widgets:** Drag-and-drop customizable dashboard
- **Drill-Down:** Click any amount to see source transactions

#### 6. Integration & API
- **REST API:** Full JSON API for mobile/third-party apps
- **API Keys:** Per-application key management
- **Webhooks:** Notify external systems on events
- **Bank Feeds:** Open banking integration for auto-reconciliation
- **Payment Gateways:** Stripe/PayPal integration for online payments

#### 7. Enhanced Inventory
- **Batch/Lot Tracking:** Expiry date tracking
- **Warehouse Management:** Multiple locations per branch
- **Assembly/BOM:** Manufactured products
- **Reorder Points:** Automated purchase orders

#### 8. Time & Billing
- **Timesheets:** Employee hours tracking
- **Project Tracking:** Billable vs non-billable hours
- **Invoicing:** Generate invoices from timesheets
- **Rate Cards:** Different rates per client/project

### Long-Term Vision (6-12 Months)

#### 9. Mobile Apps
- **React Native:** iOS/Android mobile apps
- **Offline Mode:** Cache data, sync when online
- **Push Notifications:** Approval alerts, invoice reminders
- **Barcode Scanning:** Inventory, invoicing

#### 10. Advanced AI Features
- **Anomaly Detection:** ML to flag unusual transactions
- **Invoice OCR:** Extract line items from PDF invoices
- **Cash Flow Prediction:** Advanced ML models (LSTM, Prophet)
- **Smart Categorization:** Auto-categorize expenses
- **Voice Assistant:** Siri/Google Assistant integration

#### 11. Multi-Entity Consolidation
- **Holding Company View:** Consolidate multiple businesses
- **Inter-Company Transactions:** Eliminate in consolidation
- **Minority Interest:** Complex ownership structures
- **Currency Translation:** Multi-GAAP reporting

#### 12. Industry-Specific Modules
- **Retail:** POS integration, loyalty programs
- **Manufacturing:** MRP, production planning
- **Construction:** Job costing, progress billing
- **Non-Profit:** Fund accounting, grant tracking
- **Professional Services:** Resource scheduling, WIP

---

## Advanced Features Planning

### 1. Blockchain Integration (Conceptual)

**Use Case:** Immutable Audit Trail

```
Journal Voucher → Hash → Blockchain (Ethereum/Hyperledger)
```

- Every ledger entry hashed and stored on-chain
- Proof of data integrity
- Regulatory compliance

### 2. Real-Time Collaboration

**Architecture:** WebSocket + Server-Sent Events

- Multiple users viewing same report
- Real-time updates when someone posts
- Collaborative budgeting
- Document locking during edits

### 3. Advanced Analytics with Data Warehousing

**Data Pipeline:**
```
Transactional DB (SQLite/PostgreSQL)
    ↓ (ETL Nightly)
ClickHouse (Columnar Data Warehouse)
    ↓ (Analytics)
Metabase/Grafana Dashboards
```

- Historical performance over years
- Complex aggregations without impacting transactional DB
- Machine learning on full historical dataset

### 4. Automated Bookkeeping

**AI-Driven Automation:**
- Bank feed → Categorize using ML
- Invoice OCR → Create bill automatically
- Receipt scanning → Expense entry
- Approval workflows → Auto-post on approval

### 5. Smart Reconciliation

**Features:**
- ML-based transaction matching (probability scores)
- Suggest reconciliation matches
- Learn from user corrections
- Auto-reconcile high-confidence matches (>95%)

### 6. Predictive Analytics

**Models:**
- **Cash Flow:** LSTM time series forecasting
- **Sales:** Prophet (Facebook) with seasonality
- **Churn:** Predict customer payment defaults
- **Inventory:** Optimize stock levels, prevent stockouts
- **Pricing:** Dynamic pricing optimization

### 7. Tax Compliance Automation

**Features:**
- VAT/GST filing preparation
- PAYE/P11D generation (UK)
- W-2, 1099 (US)
- Direct integration with tax authorities APIs
- Audit trail for all tax calculations

### 8. White-Label SaaS Platform

**Architecture:**
- Multi-tenant with data isolation (row-level security)
- Custom domains per customer
- Branding configuration (logo, colors)
- Feature tiers (Basic, Pro, Enterprise)
- Usage-based pricing (API calls, records)

### 9. Internationalization (i18n)

**Requirements:**
- Multi-language support (JSON translation files)
- Date/number formatting per locale
- RTL (Right-to-Left) for Arabic
- Tax compliance per country
- Multi-currency accounting

### 10. Advanced Security

**Zero-Trust Architecture:**
- Device fingerprinting
- IP-based geofencing
- Contextual MFA (new device, unusual location)
- Hardware security keys (WebAuthn)
- Zero-knowledge encryption for sensitive data

---

## Development Guidelines

### Code Style

**Python:** PEP 8 with Black formatter
**JavaScript:** ESLint with Prettier
**HTML/Templates:** consistent indentation, component-based

### Git Workflow

```
main (production)
  ↑
develop (integration)
  ↑
feature/xxx (feature branches)
```

**Commit Message Format:**
```
type(scope): description

# Types: feat, fix, docs, style, refactor, test, chore
# Example: feat(inventory): add batch expiration tracking
```

### Database Migrations

**Alembic (Recommended):**
```bash
alembic revision --autogenerate -m "description"
alembic upgrade head
```

**For now:** `Base.metadata.create_all()` in startup

### Error Handling

**Standard Pattern:**
```python
try:
    # Database operation
    db.commit()
except ValueError as e:
    db.rollback()
    raise HTTPException(status_code=400, detail=str(e))
except Exception as e:
    db.rollback()
    raise HTTPException(status_code=500, detail="Internal error")
```

### Logging Strategy

```python
import logging
logger = logging.getLogger(__name__)

logger.info("User {username} created invoice {invoice_number}")
logger.error("Payment processing failed", exc_info=True)
logger.warning("Stock below reorder point: {product}")
```

**Log Levels:** DEBUG, INFO, WARNING, ERROR, CRITICAL

---

## Contact & Support

**Project:** Planex (Plan Next Excellence)
**Company:** Planex Software Solutions
**Documentation Version:** 1.0.0
**Last Updated:** 2026-02-13

For technical questions or contributions, please refer to:
- GitHub Issues (if repository is public)
- Internal development team contacts
- API documentation (if REST API exposed)

---

## Appendix A: Default Chart of Accounts

### Assets
- 1000 - Cash (System)
- 1100 - Bank (System)
- 1200 - Accounts Receivable
- 1300 - Inventory
- 1400 - VAT Refundable
- 1500 - Fixed Assets
- 1510 - Accumulated Depreciation (System)

### Liabilities
- 2000 - Accounts Payable
- 2100 - VAT Payable
- 2200 - PAYE Payable (System)
- 2210 - Pension Payable (System)
- 2300 - Payroll Liabilities (System)
- 2400 - Loans

### Equity
- 3000 - Owner's Capital
- 3100 - Retained Earnings

### Revenue
- 4000 - Sales Revenue (System)
- 4100 - Other Income
- 4200 - Interest Income
- 4300 - Discount Received

### Expenses
- 5000 - Cost of Goods Sold (System)
- 5100 - Salaries & Wages
- 5200 - Rent
- 5300 - Utilities
- 5400 - Office Expenses
- 5500 - Travel & Vehicle
- 5600 - Marketing
- 5700 - Bank Charges
- 5800 - Bad Debts

---

## Appendix B: API Key Setup Guide

### Google Gemini AI

1. Go to [AI Studio](https://makersuite.google.com/app/apikey)
2. Create new API key
3. Copy key
4. In Planex: Settings → AI → Select "Gemini" → Paste key → Save

### Zai (Z.ai)

1. Go to [Z.ai Platform](https://z.ai)
2. Register/login
3. Navigate to API Keys section
4. Generate new key
5. In Planex: Settings → AI → Select "Zai" → Paste key → Save

---

*This documentation is a comprehensive guide for developers working on the Planex SaaS ERP & Accounting Software. It covers all models, routes, features, and provides a roadmap for future development.*
