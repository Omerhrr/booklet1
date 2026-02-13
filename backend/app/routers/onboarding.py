"""
Onboarding Router - Setup Wizard for New Tenants
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional, List

from ..database import get_db
from ..security import get_current_user
from ..models.tenant import Tenant
from ..models.branch import Branch
from ..models.user import User

router = APIRouter(prefix="/onboarding", tags=["Onboarding"])


class OnboardingStep1(BaseModel):
    business_name: str
    trading_name: Optional[str] = None
    industry: str
    address: str
    city: str
    state: str
    phone: str
    email: str
    tax_id: Optional[str] = None  # Nigerian TIN
    rc_number: Optional[str] = None  # CAC number


class OnboardingStep2(BaseModel):
    branch_name: str
    branch_address: Optional[str] = None
    branch_city: Optional[str] = None
    branch_state: Optional[str] = None


class OnboardingStep3(BaseModel):
    employee_first_name: str
    employee_last_name: str
    employee_email: str
    employee_department: Optional[str] = None
    employee_position: Optional[str] = None
    basic_salary: float


@router.get("/status")
async def get_onboarding_status(
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Check onboarding progress"""
    tenant_id = current_user["tenant_id"]

    tenant = db.query(Tenant).filter(Tenant.id == tenant_id).first()

    # Check setup progress
    steps = {
        "company_info": bool(tenant.business_name and tenant.address),
        "branches": db.query(Branch).filter(Branch.tenant_id == tenant_id).count() > 0,
        "employees": db.query(User).filter(User.tenant_id == tenant_id).count() > 0
    }

    completed = sum(1 for step in steps.values() if step)
    total = len(steps)

    return {
        "is_completed": all(steps.values()),
        "progress": f"{completed}/{total}",
        "percentage": int((completed / total) * 100),
        "steps": steps
    }


@router.post("/step-1")
async def complete_step_1(
    data: OnboardingStep1,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Complete company information step"""
    tenant_id = current_user["tenant_id"]

    tenant = db.query(Tenant).filter(Tenant.id == tenant_id).first()

    if not tenant:
        raise HTTPException(status_code=404, detail="Company not found")

    tenant.business_name = data.business_name
    tenant.trading_name = data.trading_name
    tenant.industry = data.industry
    tenant.address = data.address
    tenant.city = data.city
    tenant.state = data.state
    tenant.phone = data.phone
    tenant.email = data.email
    tenant.tax_id = data.tax_id
    tenant.rc_number = data.rc_number

    db.commit()

    return {"message": "Company information saved", "step": 1}


@router.post("/step-2")
async def complete_step_2(
    data: OnboardingStep2,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Complete branch setup step"""
    tenant_id = current_user["tenant_id"]

    # Check if branch already exists
    existing = db.query(Branch).filter(Branch.tenant_id == tenant_id).count()

    branch = Branch(
        tenant_id=tenant_id,
        name=data.branch_name,
        address=data.branch_address,
        city=data.branch_city,
        state=data.branch_state,
        is_head_office=(existing == 0)  # First branch is head office
    )

    db.add(branch)
    db.commit()

    return {"message": "Branch created", "branch_id": branch.id, "step": 2}


@router.post("/step-3")
async def complete_step_3(
    data: OnboardingStep3,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Complete first employee setup"""
    tenant_id = current_user["tenant_id"]

    # Get default branch
    branch = db.query(Branch).filter(Branch.tenant_id == tenant_id).first()

    if not branch:
        raise HTTPException(status_code=400, detail="Please create a branch first")

    from ..models.hr import Employee
    from datetime import date

    employee = Employee(
        tenant_id=tenant_id,
        branch_id=branch.id,
        first_name=data.employee_first_name,
        last_name=data.employee_last_name,
        email=data.employee_email,
        department=data.employee_department,
        position=data.employee_position,
        basic_salary=data.basic_salary,
        hire_date=date.today()
    )

    db.add(employee)
    db.commit()

    return {"message": "Employee created", "employee_id": employee.id, "step": 3}


@router.post("/complete")
async def complete_onboarding(
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Mark onboarding as complete and set up default data"""
    tenant_id = current_user["tenant_id"]

    tenant = db.query(Tenant).filter(Tenant.id == tenant_id).first()

    if not tenant:
        raise HTTPException(status_code=404, detail="Company not found")

    # Create default chart of accounts if not exists
    from ..crud.account import create_default_chart_of_accounts

    branch = db.query(Branch).filter(Branch.tenant_id == tenant_id).first()
    if branch:
        create_default_chart_of_accounts(tenant_id, branch.id, db)

    # Mark onboarding complete
    tenant.onboarding_completed = True
    db.commit()

    return {
        "message": "Onboarding completed successfully",
        "next_steps": [
            "Add your products/services",
            "Create customers and vendors",
            "Set up bank accounts",
            "Invite team members"
        ]
    }


@router.get("/industries")
async def get_industry_options():
    """Get industry options for onboarding"""
    return {
        "industries": [
            {"value": "retail", "label": "Retail & Wholesale"},
            {"value": "manufacturing", "label": "Manufacturing"},
            {"value": "services", "label": "Professional Services"},
            {"value": "technology", "label": "Technology & IT"},
            {"value": "healthcare", "label": "Healthcare"},
            {"value": "education", "label": "Education"},
            {"value": "hospitality", "label": "Hospitality & Tourism"},
            {"value": "construction", "label": "Construction"},
            {"value": "agriculture", "label": "Agriculture"},
            {"value": "finance", "label": "Finance & Banking"},
            {"value": "oil_gas", "label": "Oil & Gas"},
            {"value": "other", "label": "Other"}
        ]
    }
