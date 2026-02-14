"""
Employee and Payroll CRUD Operations
"""

from typing import Optional, List
from sqlalchemy.orm import Session
from sqlalchemy import func
from datetime import datetime, date

from ..models.hr import Employee, PayrollConfig, Payslip, PayslipAddition, PayslipDeduction
from ..models.tenant import Tenant


class CRUDEmployee:
    
    def get(self, db: Session, employee_id: int) -> Optional[Employee]:
        return db.query(Employee).filter(Employee.id == employee_id).first()
    
    def get_multi(
        self,
        db: Session,
        tenant_id: int,
        branch_id: int = None,
        skip: int = 0,
        limit: int = 50,
        is_active: bool = None,
        search: str = None
    ) -> List[Employee]:
        query = db.query(Employee).filter(Employee.tenant_id == tenant_id)
        
        if branch_id:
            query = query.filter(Employee.branch_id == branch_id)
        
        if is_active is not None:
            query = query.filter(Employee.is_active == is_active)
        
        if search:
            search_term = f"%{search}%"
            query = query.filter(
                Employee.full_name.ilike(search_term) |
                Employee.email.ilike(search_term) |
                Employee.employee_number.ilike(search_term)
            )
        
        return query.order_by(Employee.full_name).offset(skip).limit(limit).all()
    
    def count(self, db: Session, tenant_id: int, branch_id: int = None) -> int:
        query = db.query(func.count(Employee.id)).filter(Employee.tenant_id == tenant_id)
        
        if branch_id:
            query = query.filter(Employee.branch_id == branch_id)
        
        return query.scalar() or 0
    
    def create(
        self,
        db: Session,
        *,
        tenant_id: int,
        branch_id: int,
        full_name: str,
        email: str,
        phone: str = None,
        address: str = None,
        hire_date: date,
        employee_number: str = None,
        gross_salary: float = 0,
        pay_frequency: str = "monthly"
    ) -> Employee:
        """Create employee with payroll config"""
        if not employee_number:
            employee_number = self._generate_employee_number(db, tenant_id)
        
        employee = Employee(
            tenant_id=tenant_id,
            branch_id=branch_id,
            employee_number=employee_number,
            full_name=full_name,
            email=email,
            phone=phone,
            address=address,
            hire_date=hire_date
        )
        db.add(employee)
        db.flush()
        
        # Create payroll config
        payroll_config = PayrollConfig(
            employee_id=employee.id,
            gross_salary=gross_salary,
            pay_frequency=pay_frequency
        )
        db.add(payroll_config)
        
        db.commit()
        db.refresh(employee)
        return employee
    
    def _generate_employee_number(self, db: Session, tenant_id: int) -> str:
        year = datetime.now().year
        
        last_emp = db.query(Employee).filter(
            Employee.tenant_id == tenant_id,
            Employee.employee_number.like(f"EMP-{year}-%")
        ).order_by(Employee.employee_number.desc()).first()
        
        if last_emp:
            last_num = int(last_emp.employee_number.split('-')[-1])
            new_num = last_num + 1
        else:
            new_num = 1
        
        return f"EMP-{year}-{new_num:04d}"
    
    def update(self, db: Session, employee: Employee, **kwargs) -> Employee:
        for key, value in kwargs.items():
            if hasattr(employee, key):
                setattr(employee, key, value)
        db.commit()
        db.refresh(employee)
        return employee
    
    def terminate(
        self,
        db: Session,
        employee_id: int,
        termination_date: date
    ) -> Employee:
        """Terminate employee"""
        employee = self.get(db, employee_id)
        if employee:
            employee.is_active = False
            employee.termination_date = termination_date
            db.commit()
            db.refresh(employee)
        return employee


class CRUDPayroll:
    
    def get_payslip(self, db: Session, payslip_id: int) -> Optional[Payslip]:
        return db.query(Payslip).filter(Payslip.id == payslip_id).first()
    
    def get_payslips(
        self,
        db: Session,
        tenant_id: int,
        employee_id: int = None,
        pay_period_start: date = None,
        pay_period_end: date = None,
        skip: int = 0,
        limit: int = 50
    ) -> List[Payslip]:
        query = db.query(Payslip).filter(Payslip.tenant_id == tenant_id)
        
        if employee_id:
            query = query.filter(Payslip.employee_id == employee_id)
        
        if pay_period_start:
            query = query.filter(Payslip.pay_period_start >= pay_period_start)
        
        if pay_period_end:
            query = query.filter(Payslip.pay_period_end <= pay_period_end)
        
        return query.order_by(Payslip.pay_date.desc()).offset(skip).limit(limit).all()
    
    def get_payroll_config(self, db: Session, employee_id: int) -> Optional[PayrollConfig]:
        return db.query(PayrollConfig).filter(
            PayrollConfig.employee_id == employee_id
        ).first()
    
    def update_payroll_config(
        self,
        db: Session,
        employee_id: int,
        **kwargs
    ) -> PayrollConfig:
        config = self.get_payroll_config(db, employee_id)
        
        if not config:
            config = PayrollConfig(employee_id=employee_id, **kwargs)
            db.add(config)
        else:
            for key, value in kwargs.items():
                if hasattr(config, key):
                    setattr(config, key, value)
        
        db.commit()
        db.refresh(config)
        return config
    
    def create_payslip(
        self,
        db: Session,
        *,
        tenant_id: int,
        employee_id: int,
        pay_period_start: date,
        pay_period_end: date,
        pay_date: date,
        gross_pay: float,
        total_allowances: float = 0,
        paye_deduction: float = 0,
        pension_employee: float = 0,
        pension_employer: float = 0,
        total_deductions: float = 0,
        net_pay: float = 0,
        additions: List[dict] = None,
        deductions: List[dict] = None
    ) -> Payslip:
        payslip = Payslip(
            tenant_id=tenant_id,
            employee_id=employee_id,
            pay_period_start=pay_period_start,
            pay_period_end=pay_period_end,
            pay_date=pay_date,
            gross_pay=gross_pay,
            total_allowances=total_allowances,
            paye_deduction=paye_deduction,
            pension_employee=pension_employee,
            pension_employer=pension_employer,
            total_deductions=total_deductions,
            net_pay=net_pay
        )
        db.add(payslip)
        db.flush()
        
        if additions:
            for add in additions:
                addition = PayslipAddition(
                    payslip_id=payslip.id,
                    description=add.get('description'),
                    amount=add.get('amount', 0)
                )
                db.add(addition)
        
        if deductions:
            for ded in deductions:
                deduction = PayslipDeduction(
                    payslip_id=payslip.id,
                    description=ded.get('description'),
                    amount=ded.get('amount', 0)
                )
                db.add(deduction)
        
        db.commit()
        db.refresh(payslip)
        return payslip


employee = CRUDEmployee()
payroll = CRUDPayroll()
payslip = CRUDPayroll()  # Alias for backward compatibility
