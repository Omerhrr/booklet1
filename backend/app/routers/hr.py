"""
HR & Payroll Router - Employees, Payroll, Payslips
Nigerian statutory deductions: PAYE, Pension (8% employee, 10% employer)
"""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime, date
from pydantic import BaseModel
from enum import Enum

from ..database import get_db
from ..security import get_current_user
from ..models.hr import Employee, PayrollConfig, Payslip, PayslipAddition, PayslipDeduction
from ..utils.nigerian_tax import calculate_paye, calculate_pension

router = APIRouter(prefix="/hr", tags=["HR & Payroll"])


# === Pydantic Schemas ===

class EmployeeCreate(BaseModel):
    first_name: str
    last_name: str
    email: Optional[str] = None
    phone: Optional[str] = None
    address: Optional[str] = None
    date_of_birth: Optional[date] = None
    hire_date: date
    department: Optional[str] = None
    position: Optional[str] = None
    employment_type: str = "full_time"  # full_time, part_time, contract
    basic_salary: float
    bank_name: Optional[str] = None
    bank_account: Optional[str] = None
    tax_id: Optional[str] = None  # Nigerian TIN
    pension_id: Optional[str] = None  # Pension PIN
    branch_id: int

class EmployeeUpdate(BaseModel):
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    department: Optional[str] = None
    position: Optional[str] = None
    basic_salary: Optional[float] = None
    bank_name: Optional[str] = None
    bank_account: Optional[str] = None
    is_active: Optional[bool] = None

class PayrollRun(BaseModel):
    month: int  # 1-12
    year: int
    branch_id: int
    employee_ids: Optional[List[int]] = None  # If None, process all active employees

class PayslipUpdate(BaseModel):
    additions: Optional[List[dict]] = None  # [{name, amount, is_taxable}]
    deductions: Optional[List[dict]] = None  # [{name, amount}]


# === Employees ===

@router.get("/employees")
async def list_employees(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, le=200),
    department: Optional[str] = None,
    is_active: Optional[bool] = None,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """List employees"""
    tenant_id = current_user["tenant_id"]

    query = db.query(Employee).filter(Employee.tenant_id == tenant_id)

    if department:
        query = query.filter(Employee.department == department)
    if is_active is not None:
        query = query.filter(Employee.is_active == is_active)

    employees = query.order_by(Employee.first_name).offset(skip).limit(limit).all()

    return {
        "items": [{
            "id": e.id,
            "first_name": e.first_name,
            "last_name": e.last_name,
            "full_name": f"{e.first_name} {e.last_name}",
            "email": e.email,
            "phone": e.phone,
            "department": e.department,
            "position": e.position,
            "employment_type": e.employment_type,
            "basic_salary": e.basic_salary,
            "hire_date": e.hire_date.isoformat() if e.hire_date else None,
            "is_active": e.is_active
        } for e in employees],
        "total": query.count()
    }


@router.post("/employees")
async def create_employee(
    employee_data: EmployeeCreate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Create new employee"""
    tenant_id = current_user["tenant_id"]

    # Check for duplicate email
    if employee_data.email:
        existing = db.query(Employee).filter(
            Employee.tenant_id == tenant_id,
            Employee.email == employee_data.email
        ).first()
        if existing:
            raise HTTPException(status_code=400, detail="Employee with this email already exists")

    employee = Employee(
        tenant_id=tenant_id,
        branch_id=employee_data.branch_id,
        first_name=employee_data.first_name,
        last_name=employee_data.last_name,
        email=employee_data.email,
        phone=employee_data.phone,
        address=employee_data.address,
        date_of_birth=employee_data.date_of_birth,
        hire_date=employee_data.hire_date,
        department=employee_data.department,
        position=employee_data.position,
        employment_type=employee_data.employment_type,
        basic_salary=employee_data.basic_salary,
        bank_name=employee_data.bank_name,
        bank_account=employee_data.bank_account,
        tax_id=employee_data.tax_id,
        pension_id=employee_data.pension_id
    )

    db.add(employee)
    db.commit()
    db.refresh(employee)

    return {"id": employee.id, "message": "Employee created successfully"}


@router.get("/employees/{employee_id}")
async def get_employee(
    employee_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Get employee details"""
    tenant_id = current_user["tenant_id"]

    employee = db.query(Employee).filter(
        Employee.id == employee_id,
        Employee.tenant_id == tenant_id
    ).first()

    if not employee:
        raise HTTPException(status_code=404, detail="Employee not found")

    return {
        "id": employee.id,
        "first_name": employee.first_name,
        "last_name": employee.last_name,
        "email": employee.email,
        "phone": employee.phone,
        "address": employee.address,
        "date_of_birth": employee.date_of_birth.isoformat() if employee.date_of_birth else None,
        "hire_date": employee.hire_date.isoformat() if employee.hire_date else None,
        "termination_date": employee.termination_date.isoformat() if employee.termination_date else None,
        "department": employee.department,
        "position": employee.position,
        "employment_type": employee.employment_type,
        "basic_salary": employee.basic_salary,
        "bank_name": employee.bank_name,
        "bank_account": employee.bank_account,
        "tax_id": employee.tax_id,
        "pension_id": employee.pension_id,
        "is_active": employee.is_active,
        "created_at": employee.created_at.isoformat() if employee.created_at else None
    }


@router.put("/employees/{employee_id}")
async def update_employee(
    employee_id: int,
    employee_data: EmployeeUpdate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Update employee"""
    tenant_id = current_user["tenant_id"]

    employee = db.query(Employee).filter(
        Employee.id == employee_id,
        Employee.tenant_id == tenant_id
    ).first()

    if not employee:
        raise HTTPException(status_code=404, detail="Employee not found")

    for field, value in employee_data.dict(exclude_unset=True).items():
        setattr(employee, field, value)

    db.commit()
    return {"message": "Employee updated successfully"}


@router.delete("/employees/{employee_id}")
async def delete_employee(
    employee_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Deactivate employee (soft delete)"""
    tenant_id = current_user["tenant_id"]

    employee = db.query(Employee).filter(
        Employee.id == employee_id,
        Employee.tenant_id == tenant_id
    ).first()

    if not employee:
        raise HTTPException(status_code=404, detail="Employee not found")

    employee.is_active = False
    employee.termination_date = date.today()

    db.commit()
    return {"message": "Employee deactivated successfully"}


# === Payroll ===

@router.get("/payroll/config")
async def get_payroll_config(
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Get payroll configuration"""
    tenant_id = current_user["tenant_id"]

    config = db.query(PayrollConfig).filter(
        PayrollConfig.tenant_id == tenant_id
    ).first()

    if not config:
        # Return defaults
        return {
            "payroll_cycle": "monthly",
            "pay_day": 25,
            "pension_rate_employee": 8.0,  # Nigerian default
            "pension_rate_employer": 10.0,  # Nigerian default
            "vat_rate": 7.5
        }

    return {
        "id": config.id,
        "payroll_cycle": config.payroll_cycle,
        "pay_day": config.pay_day,
        "pension_rate_employee": config.pension_rate_employee,
        "pension_rate_employer": config.pension_rate_employer,
        "default_additions": config.default_additions,
        "default_deductions": config.default_deductions
    }


@router.post("/payroll/run")
async def run_payroll(
    payroll_data: PayrollRun,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Run payroll for specified month/year"""
    tenant_id = current_user["tenant_id"]

    # Check if payroll already run for this period
    existing = db.query(Payslip).filter(
        Payslip.tenant_id == tenant_id,
        Payslip.pay_period_month == payroll_data.month,
        Payslip.pay_period_year == payroll_data.year
    ).first()

    if existing:
        raise HTTPException(
            status_code=400,
            detail=f"Payroll already run for {payroll_data.month}/{payroll_data.year}"
        )

    # Get active employees
    query = db.query(Employee).filter(
        Employee.tenant_id == tenant_id,
        Employee.is_active == True
    )

    if payroll_data.employee_ids:
        query = query.filter(Employee.id.in_(payroll_data.employee_ids))

    employees = query.all()

    if not employees:
        raise HTTPException(status_code=400, detail="No employees to process")

    # Get payroll config
    config = db.query(PayrollConfig).filter(
        PayrollConfig.tenant_id == tenant_id
    ).first()

    pension_employee_rate = config.pension_rate_employee if config else 8.0
    pension_employer_rate = config.pension_rate_employer if config else 10.0

    payslips_created = []

    for employee in employees:
        # Calculate gross pay
        gross_pay = employee.basic_salary

        # Calculate Nigerian statutory deductions
        pension_employee = calculate_pension(gross_pay, pension_employee_rate)
        paye = calculate_paye(gross_pay)

        # Calculate net pay
        total_deductions = pension_employee + paye
        net_pay = gross_pay - total_deductions

        # Generate payslip number
        last_payslip = db.query(Payslip).filter(
            Payslip.tenant_id == tenant_id
        ).order_by(Payslip.id.desc()).first()

        payslip_num = f"PS-{payroll_data.year}{payroll_data.month:02d}-{(last_payslip.id + 1) if last_payslip else 1:04d}"

        payslip = Payslip(
            tenant_id=tenant_id,
            branch_id=payroll_data.branch_id,
            employee_id=employee.id,
            payslip_number=payslip_num,
            pay_period_month=payroll_data.month,
            pay_period_year=payroll_data.year,
            basic_salary=employee.basic_salary,
            gross_pay=gross_pay,
            pension_employee=pension_employee,
            pension_employer=pension_employer,
            paye=paye,
            total_deductions=total_deductions,
            net_pay=net_pay
        )

        db.add(payslip)
        db.flush()

        # Add statutory deduction records
        pension_deduction = PayslipDeduction(
            payslip_id=payslip.id,
            name="Pension (Employee)",
            amount=pension_employee,
            is_statutory=True
        )
        db.add(pension_deduction)

        paye_deduction = PayslipDeduction(
            payslip_id=payslip.id,
            name="PAYE Tax",
            amount=paye,
            is_statutory=True
        )
        db.add(paye_deduction)

        payslips_created.append(payslip_num)

    db.commit()

    return {
        "message": f"Payroll processed for {len(employees)} employees",
        "payslips": payslips_created
    }


@router.get("/payslips")
async def list_payslips(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, le=200),
    month: Optional[int] = None,
    year: Optional[int] = None,
    employee_id: Optional[int] = None,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """List payslips"""
    tenant_id = current_user["tenant_id"]

    query = db.query(Payslip).filter(Payslip.tenant_id == tenant_id)

    if month:
        query = query.filter(Payslip.pay_period_month == month)
    if year:
        query = query.filter(Payslip.pay_period_year == year)
    if employee_id:
        query = query.filter(Payslip.employee_id == employee_id)

    payslips = query.order_by(Payslip.created_at.desc()).offset(skip).limit(limit).all()

    # Get employee names
    employee_ids = list(set(p.employee_id for p in payslips))
    employees = {e.id: e for e in db.query(Employee).filter(Employee.id.in_(employee_ids)).all()}

    return {
        "items": [{
            "id": p.id,
            "payslip_number": p.payslip_number,
            "employee_name": f"{employees.get(p.employee_id, Employee(first_name='Unknown')).first_name} {employees.get(p.employee_id, Employee(last_name='')).last_name}",
            "pay_period": f"{p.pay_period_month:02d}/{p.pay_period_year}",
            "gross_pay": p.gross_pay,
            "total_deductions": p.total_deductions,
            "net_pay": p.net_pay,
            "is_paid": p.is_paid,
            "paid_at": p.paid_at.isoformat() if p.paid_at else None
        } for p in payslips],
        "total": query.count()
    }


@router.get("/payslips/{payslip_id}")
async def get_payslip(
    payslip_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Get payslip details"""
    tenant_id = current_user["tenant_id"]

    payslip = db.query(Payslip).filter(
        Payslip.id == payslip_id,
        Payslip.tenant_id == tenant_id
    ).first()

    if not payslip:
        raise HTTPException(status_code=404, detail="Payslip not found")

    employee = db.query(Employee).filter(Employee.id == payslip.employee_id).first()

    # Get additions and deductions
    additions = db.query(PayslipAddition).filter(
        PayslipAddition.payslip_id == payslip_id
    ).all()

    deductions = db.query(PayslipDeduction).filter(
        PayslipDeduction.payslip_id == payslip_id
    ).all()

    return {
        "id": payslip.id,
        "payslip_number": payslip.payslip_number,
        "pay_period_month": payslip.pay_period_month,
        "pay_period_year": payslip.pay_period_year,
        "employee": {
            "id": employee.id,
            "name": f"{employee.first_name} {employee.last_name}",
            "position": employee.position,
            "department": employee.department,
            "tax_id": employee.tax_id,
            "pension_id": employee.pension_id
        } if employee else None,
        "earnings": {
            "basic_salary": payslip.basic_salary,
            "additions": [{
                "name": a.name,
                "amount": a.amount,
                "is_taxable": a.is_taxable
            } for a in additions],
            "gross_pay": payslip.gross_pay
        },
        "deductions": [{
            "name": d.name,
            "amount": d.amount,
            "is_statutory": d.is_statutory
        } for d in deductions],
        "pension_employee": payslip.pension_employee,
        "pension_employer": payslip.pension_employer,
        "paye": payslip.paye,
        "total_deductions": payslip.total_deductions,
        "net_pay": payslip.net_pay,
        "is_paid": payslip.is_paid,
        "paid_at": payslip.paid_at.isoformat() if payslip.paid_at else None
    }


@router.post("/payslips/{payslip_id}/pay")
async def mark_payslip_paid(
    payslip_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Mark payslip as paid"""
    tenant_id = current_user["tenant_id"]

    payslip = db.query(Payslip).filter(
        Payslip.id == payslip_id,
        Payslip.tenant_id == tenant_id
    ).first()

    if not payslip:
        raise HTTPException(status_code=404, detail="Payslip not found")

    if payslip.is_paid:
        raise HTTPException(status_code=400, detail="Payslip already paid")

    payslip.is_paid = True
    payslip.paid_at = datetime.utcnow()

    db.commit()

    return {"message": "Payslip marked as paid"}


# === Dashboard Stats ===

@router.get("/dashboard")
async def get_hr_dashboard(
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Get HR dashboard statistics"""
    tenant_id = current_user["tenant_id"]

    # Total employees
    total_employees = db.query(Employee).filter(
        Employee.tenant_id == tenant_id,
        Employee.is_active == True
    ).count()

    # Total payroll this month
    current_month = datetime.now().month
    current_year = datetime.now().year

    total_payroll = db.query(db.func.sum(Payslip.net_pay)).filter(
        Payslip.tenant_id == tenant_id,
        Payslip.pay_period_month == current_month,
        Payslip.pay_period_year == current_year
    ).scalar() or 0

    # Departments
    departments = db.query(
        Employee.department,
        db.func.count(Employee.id)
    ).filter(
        Employee.tenant_id == tenant_id,
        Employee.is_active == True
    ).group_by(Employee.department).all()

    return {
        "total_employees": total_employees,
        "total_payroll_month": total_payroll,
        "departments": [{"name": d[0] or "Unassigned", "count": d[1]} for d in departments]
    }
