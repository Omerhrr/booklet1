"""
Booklet - Multi-Tenant SaaS ERP Platform
Backend Application Entry Point
"""

from fastapi import FastAPI, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from contextlib import asynccontextmanager
import logging
import os

from .database import init_db
from .routers import auth, dashboard, customers, vendors, sales, purchases, inventory, accounting, hr, reports, analytics, jarvis, settings, branches, team, roles, banking, expenses, fixed_assets, budget, onboarding

# Configure logging
logging.basicConfig(
    level=logging.INFO if os.getenv("DEBUG") else logging.WARNING,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan events"""
    # Startup
    logger.info("Starting Booklet ERP Backend...")
    await init_db()
    logger.info("Database initialized")
    
    yield
    
    # Shutdown
    logger.info("Shutting down Booklet ERP Backend...")


# Create FastAPI application
app = FastAPI(
    title="Booklet ERP API",
    description="Multi-Tenant SaaS ERP Platform - Enterprise-grade accounting, inventory, HR, and business intelligence",
    version="2.0.0",
    docs_url="/api/docs",
    redoc_url="/api/redoc",
    openapi_url="/api/openapi.json",
    lifespan=lifespan
)

# CORS Configuration - Allow requests from Flask frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5000",
        "http://127.0.0.1:5000",
        "http://localhost:3000",
        "https://*.booklet.com",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Exception handlers
@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    return JSONResponse(
        status_code=exc.status_code,
        content={"error": True, "message": exc.detail}
    )


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    return JSONResponse(
        status_code=422,
        content={"error": True, "message": "Validation error", "details": exc.errors()}
    )


@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    logger.error(f"Unhandled exception: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={"error": True, "message": "Internal server error"}
    )


# Health check endpoint
@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "booklet-backend"}


@app.get("/api/health")
async def api_health_check():
    return {"status": "healthy", "service": "booklet-api"}


# Include API routers
app.include_router(auth.router, prefix="/api/v1/auth", tags=["Authentication"])
app.include_router(dashboard.router, prefix="/api/v1/dashboard", tags=["Dashboard"])
app.include_router(customers.router, prefix="/api/v1/customers", tags=["Customers"])
app.include_router(vendors.router, prefix="/api/v1/vendors", tags=["Vendors"])
app.include_router(sales.router, prefix="/api/v1/sales", tags=["Sales"])
app.include_router(purchases.router, prefix="/api/v1/purchases", tags=["Purchases"])
app.include_router(inventory.router, prefix="/api/v1/inventory", tags=["Inventory"])
app.include_router(accounting.router, prefix="/api/v1/accounting", tags=["Accounting"])
app.include_router(hr.router, prefix="/api/v1/hr", tags=["HR & Payroll"])
app.include_router(reports.router, prefix="/api/v1/reports", tags=["Reports"])
app.include_router(analytics.router, prefix="/api/v1/analytics", tags=["Analytics"])
app.include_router(jarvis.router, prefix="/api/v1/jarvis", tags=["AI Analyst"])
app.include_router(settings.router, prefix="/api/v1/settings", tags=["Settings"])
app.include_router(branches.router, prefix="/api/v1/branches", tags=["Branches"])
app.include_router(team.router, prefix="/api/v1/team", tags=["Team"])
app.include_router(roles.router, prefix="/api/v1/roles", tags=["Roles"])
app.include_router(banking.router, prefix="/api/v1/banking", tags=["Banking"])
app.include_router(expenses.router, prefix="/api/v1/expenses", tags=["Expenses"])
app.include_router(fixed_assets.router, prefix="/api/v1/fixed-assets", tags=["Fixed Assets"])
app.include_router(budget.router, prefix="/api/v1/budget", tags=["Budgeting"])
app.include_router(onboarding.router, prefix="/api/v1/onboarding", tags=["Onboarding"])
