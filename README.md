# Booklet - Multi-Tenant SaaS ERP Platform

**Enterprise-grade accounting, inventory, HR, and business intelligence for businesses of all sizes.**

## Quick Start

### Prerequisites
- Python 3.10+
- PostgreSQL (recommended) or SQLite

### Installation

```bash
# Clone the repository
cd booklet

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Linux/Mac
# or
venv\Scripts\activate     # Windows

# Install dependencies
pip install -r requirements.txt

# Copy environment file
cp .env.example .env
# Edit .env with your settings

# Initialize database
python run.py init

# Run both servers
python run.py run
```

### Access the Application
- **Frontend:** http://localhost:5000
- **Backend API:** http://localhost:8000
- **API Documentation:** http://localhost:8000/api/docs

## Architecture

```
booklet/
├── backend/                 # FastAPI Backend
│   ├── app/
│   │   ├── main.py         # FastAPI entry point
│   │   ├── database.py     # Database configuration
│   │   ├── security.py     # Auth & encryption
│   │   ├── models/         # SQLAlchemy models
│   │   ├── crud/           # Database operations
│   │   └── routers/        # API endpoints
│   └── main.py
│
├── frontend/               # Flask Frontend
│   ├── app/
│   │   ├── __init__.py    # Flask app factory
│   │   ├── routes/        # Page routes
│   │   ├── templates/     # Jinja2 templates
│   │   └── static/        # CSS, JS, images
│   └── main.py
│
├── run.py                  # Main entry point
└── requirements.txt
```

## Features

### Core Modules
- **Accounting:** Double-entry bookkeeping, Chart of Accounts, General Ledger
- **Sales:** Invoices, Credit Notes, Customer Management
- **Purchases:** Bills, Debit Notes, Vendor Management
- **Inventory:** Products, Stock Management, Warehouses
- **HR & Payroll:** Employee Management, Nigerian PAYE/Pension
- **Banking:** Bank Accounts, Transfers, Reconciliation
- **Fixed Assets:** Asset Tracking, Depreciation
- **Budgeting:** Budget Planning, Variance Analysis
- **Reports:** P&L, Balance Sheet, Trial Balance, Aging Reports
- **AI Analyst (Jarvis):** Natural language business queries

### Multi-Tenancy
- Schema-based tenant isolation
- Custom subdomains per tenant
- Tenant-specific branding

### Nigerian Localization
- Default currency: Nigerian Naira (NGN)
- Nigerian VAT (7.5%)
- PAYE tax calculation
- Pension contributions (8% employee, 10% employer)
- Paga payment gateway integration

## Technology Stack

- **Backend:** FastAPI, SQLAlchemy, PostgreSQL
- **Frontend:** Flask, Jinja2, HTMX, Alpine.js
- **UI:** Tailwind CSS, Flowbite
- **Charts:** Apache ECharts
- **AI:** Google Gemini / Zai SDK

## License

Proprietary - Planex Solutions

---

**Booklet ERP** - *Multi-Tenant SaaS Platform for Modern Businesses*
