"""
Payroll Service - Nigerian PAYE, Pension, and Payroll Processing
"""

from typing import List, Dict, Any, Optional
from sqlalchemy.orm import Session
from sqlalchemy import func, and_
from datetime import datetime, date, timedelta
from decimal import Decimal
import logging

from ..models.hr import Employee, PayrollConfig, Payslip, PayslipAddition, PayslipDeduction
from ..models.account import Account, LedgerEntry

logger = logging.getLogger(__name__)


# Nigerian PAYE Tax Brackets (2024)
# Annual income brackets and rates
PAYE_BRACKETS = [
    {'min': 0, 'max': 300000, 'rate': 0.07},        # First ₦300,000 @ 7%
    {'min': 300000, 'max': 600000, 'rate': 0.11},   # Next ₦300,000 @ 11%
    {'min': 600000, 'max': 1100000, 'rate': 0.15},  # Next ₦500,000 @ 15%
    {'min': 1100000, 'max': 1600000, 'rate': 0.19}, # Next ₦500,000 @ 19%
    {'min': 1600000, 'max': 3200000, 'rate': 0.21}, # Next ₦1,600,000 @ 21%
    {'min': 3200000, 'max': float('inf'), 'rate': 0.24},  # Above ₦3,200,000 @ 24%
]

# Nigerian Pension Rates
PENSION_EMPLOYEE_RATE = 0.08  # 8% employee contribution
PENSION_EMPLOYER_RATE = 0.10  # 10% employer contribution

# Consolidated Relief Allowance (CRA)
CRA_PERCENT = 0.20  # 20% of gross
CRA_MIN_FLAT = 200000  # Minimum ₦200,000


class PayrollService:
    """Nigerian payroll processing service"""
    
    # ============================================
    # TAX CALCULATIONS
    # ============================================
    
    def calculate_paye(self, annual_gross: float) -> float:
        """
        Calculate Nigerian PAYE tax
        Uses consolidated relief allowance (CRA) and progressive rates
        """
        if annual_gross <= 0:
            return 0
        
        # Calculate Consolidated Relief Allowance (CRA)
        # CRA = higher of: ₦200,000 or 1% of gross + 20% of gross
        cra = max(CRA_MIN_FLAT, (annual_gross * 0.01) + (annual_gross * CRA_PERCENT))
        
        # Taxable income after CRA
        taxable_income = annual_gross - cra
        
        if taxable_income <= 0:
            return 0
        
        # Calculate tax using brackets
        tax = 0
        remaining = taxable_income
        
        for bracket in PAYE_BRACKETS:
            if remaining <= 0:
                break
            
            taxable_in_bracket = min(remaining, bracket['max'] - bracket['min'])
            tax += taxable_in_bracket * bracket['rate']
            remaining -= taxable_in_bracket
        
        return tax
    
    def calculate_paye_monthly(self, monthly_gross: float) -> float:
        """Calculate monthly PAYE from monthly gross"""
        annual_gross = monthly_gross * 12
        annual_paye = self.calculate_paye(annual_gross)
        return annual_paye / 12
    
    def calculate_pension_employee(self, gross_salary: float) -> float:
        """Calculate employee pension contribution (8%)"""
        return gross_salary * PENSION_EMPLOYEE_RATE
    
    def calculate_pension_employer(self, gross_salary: float) -> float:
        """Calculate employer pension contribution (10%)"""
        return gross_salary * PENSION_EMPLOYER_RATE
    
    # ============================================
    # PAYSLIP CALCULATIONS
    # ============================================
    
    def calculate_payslip(
        self,
        employee: Employee,
        pay_period_start: date,
        pay_period_end: date,
        additions: List[Dict] = None,
        deductions: List[Dict] = None
    ) -> Dict:
        """Calculate full payslip details"""
        
        config = employee.payroll_config
        if not config:
            raise ValueError(f"No payroll configuration for employee {employee.id}")
        
        # Base calculations
        gross_salary = config.gross_salary
        
        # Additions (bonuses, allowances)
        total_additions = 0
        addition_items = []
        if additions:
            for add in additions:
                total_additions += add.get('amount', 0)
                addition_items.append(add)
        
        # Include configured allowances
        if config.allowances:
            for allowance in config.allowances:
                total_additions += allowance.get('amount', 0)
                addition_items.append(allowance)
        
        gross_pay = gross_salary + total_additions
        
        # Nigerian statutory deductions
        paye = self.calculate_paye_monthly(gross_pay)
        pension_employee = self.calculate_pension_employee(gross_pay)
        
        # Other deductions
        total_other_deductions = 0
        deduction_items = []
        if deductions:
            for ded in deductions:
                total_other_deductions += ded.get('amount', 0)
                deduction_items.append(ded)
        
        # Include configured deductions
        if config.deductions:
            for deduction in config.deductions:
                total_other_deductions += deduction.get('amount', 0)
                deduction_items.append(deduction)
        
        total_deductions = paye + pension_employee + total_other_deductions
        net_pay = gross_pay - total_deductions
        
        # Employer contributions
        pension_employer = self.calculate_pension_employer(gross_pay)
        
        return {
            'employee_id': employee.id,
            'employee_name': employee.full_name,
            'pay_period_start': pay_period_start,
            'pay_period_end': pay_period_end,
            'gross_salary': gross_salary,
            'additions': addition_items,
            'total_additions': total_additions,
            'gross_pay': gross_pay,
            'paye': round(paye, 2),
            'pension_employee': round(pension_employee, 2),
            'pension_employer': round(pension_employer, 2),
            'other_deductions': deduction_items,
            'total_other_deductions': total_other_deductions,
            'total_deductions': round(total_deductions, 2),
            'net_pay': round(net_pay, 2)
        }
    
    # ============================================
    # PAYROLL PROCESSING
    # ============================================
    
    def run_payroll(
        self,
        db: Session,
        tenant_id: int,
        branch_id: int,
        pay_period_start: date,
        pay_period_end: date,
        pay_date: date,
        employee_ids: List[int] = None
    ) -> List[Payslip]:
        """Run payroll for a period"""
        
        # Get employees
        query = db.query(Employee).filter(
            Employee.tenant_id == tenant_id,
            Employee.branch_id == branch_id,
            Employee.is_active == True
        )
        
        if employee_ids:
            query = query.filter(Employee.id.in_(employee_ids))
        
        employees = query.all()
        payslips = []
        
        for employee in employees:
            try:
                # Check if payslip already exists
                existing = db.query(Payslip).filter(
                    Payslip.employee_id == employee.id,
                    Payslip.pay_period_start == pay_period_start,
                    Payslip.pay_period_end == pay_period_end
                ).first()
                
                if existing:
                    logger.warning(f"Payslip already exists for employee {employee.id}")
                    continue
                
                # Calculate payslip
                calc = self.calculate_payslip(
                    employee,
                    pay_period_start,
                    pay_period_end
                )
                
                # Create payslip record
                payslip = Payslip(
                    tenant_id=tenant_id,
                    employee_id=employee.id,
                    pay_period_start=pay_period_start,
                    pay_period_end=pay_period_end,
                    pay_date=pay_date,
                    gross_pay=calc['gross_pay'],
                    total_allowances=calc['total_additions'],
                    total_deductions=calc['total_deductions'],
                    paye_deduction=calc['paye'],
                    pension_employee=calc['pension_employee'],
                    pension_employer=calc['pension_employer'],
                    net_pay=calc['net_pay']
                )
                db.add(payslip)
                db.flush()  # Get ID
                
                # Add additions
                for add in calc['additions']:
                    addition = PayslipAddition(
                        payslip_id=payslip.id,
                        description=add.get('description', 'Addition'),
                        amount=add.get('amount', 0)
                    )
                    db.add(addition)
                
                # Add deductions
                for ded in calc['other_deductions']:
                    deduction = PayslipDeduction(
                        payslip_id=payslip.id,
                        description=ded.get('description', 'Deduction'),
                        amount=ded.get('amount', 0)
                    )
                    db.add(deduction)
                
                payslips.append(payslip)
                
            except Exception as e:
                logger.error(f"Error processing payroll for employee {employee.id}: {e}")
                continue
        
        db.commit()
        
        # Update employee current month salary
        for payslip in payslips:
            logger.info(f"Created payslip for employee {payslip.employee_id}: Net Pay = ₦{payslip.net_pay:,.2f}")
        
        return payslips
    
    def post_payroll_to_ledger(
        self,
        db: Session,
        payslips: List[Payslip],
        payroll_account_id: int,
        bank_account_id: int
    ) -> None:
        """Post payroll to general ledger"""
        from .accounting_service import accounting_service
        
        # Get liability accounts
        paye_account = db.query(Account).filter(
            Account.name == "PAYE Payable"
        ).first()
        pension_account = db.query(Account).filter(
            Account.name == "Pension Payable"
        ).first()
        payroll_liability = db.query(Account).filter(
            Account.name == "Payroll Liabilities"
        ).first()
        
        for payslip in payslips:
            entries = []
            
            # Debit Payroll Expense (gross pay)
            entries.append({
                'account_id': payroll_account_id,
                'debit': payslip.gross_pay,
                'credit': 0,
                'description': f"Salary - {payslip.employee.full_name}"
            })
            
            # Credit PAYE Payable
            if payslip.paye_deduction > 0:
                entries.append({
                    'account_id': paye_account.id,
                    'debit': 0,
                    'credit': payslip.paye_deduction,
                    'description': f"PAYE - {payslip.employee.full_name}"
                })
            
            # Credit Pension Payable (employee)
            if payslip.pension_employee > 0:
                entries.append({
                    'account_id': pension_account.id,
                    'debit': 0,
                    'credit': payslip.pension_employee,
                    'description': f"Pension (Employee) - {payslip.employee.full_name}"
                })
            
            # Credit Bank (net pay)
            entries.append({
                'account_id': bank_account_id,
                'debit': 0,
                'credit': payslip.net_pay,
                'description': f"Net Pay - {payslip.employee.full_name}"
            })
            
            # Post journal entry
            accounting_service.post_journal_entry(
                db,
                tenant_id=payslip.tenant_id,
                branch_id=payslip.employee.branch_id,
                entries=entries,
                description=f"Payroll - {payslip.employee.full_name}",
                transaction_date=payslip.pay_date,
                source_type='payslip',
                source_id=payslip.id
            )
            
            # Mark payslip as posted
            payslip.is_posted = True
            payslip.posted_at = datetime.utcnow()
        
        db.commit()
    
    # ============================================
    # STATUTORY PAYMENTS
    # ============================================
    
    def get_paye_liability(self, db: Session, tenant_id: int) -> float:
        """Get total PAYE liability"""
        from sqlalchemy import func as sql_func
        
        result = db.query(
            sql_func.coalesce(sql_func.sum(Payslip.paye_deduction), 0)
        ).filter(
            Payslip.tenant_id == tenant_id,
            Payslip.is_posted == True
        ).scalar()
        
        return float(result or 0)
    
    def get_pension_liability(self, db: Session, tenant_id: int) -> Dict:
        """Get total pension liability (employee + employer)"""
        from sqlalchemy import func as sql_func
        
        result = db.query(
            sql_func.coalesce(sql_func.sum(Payslip.pension_employee), 0).label('employee'),
            sql_func.coalesce(sql_func.sum(Payslip.pension_employer), 0).label('employer')
        ).filter(
            Payslip.tenant_id == tenant_id,
            Payslip.is_posted == True
        ).first()
        
        return {
            'employee': float(result.employee or 0),
            'employer': float(result.employer or 0),
            'total': float((result.employee or 0) + (result.employer or 0))
        }
    
    # ============================================
    # REPORTS
    # ============================================
    
    def get_payroll_summary(
        self,
        db: Session,
        tenant_id: int,
        branch_id: int,
        start_date: date,
        end_date: date
    ) -> Dict:
        """Get payroll summary for period"""
        from sqlalchemy import func as sql_func
        
        payslips = db.query(Payslip).filter(
            Payslip.tenant_id == tenant_id,
            Payslip.pay_date >= start_date,
            Payslip.pay_date <= end_date
        ).all()
        
        if branch_id:
            payslips = [p for p in payslips if p.employee.branch_id == branch_id]
        
        total_gross = sum(p.gross_pay for p in payslips)
        total_paye = sum(p.paye_deduction for p in payslips)
        total_pension_employee = sum(p.pension_employee for p in payslips)
        total_pension_employer = sum(p.pension_employer for p in payslips)
        total_net = sum(p.net_pay for p in payslips)
        
        return {
            'period_start': start_date,
            'period_end': end_date,
            'total_payslips': len(payslips),
            'total_gross': total_gross,
            'total_paye': total_paye,
            'total_pension_employee': total_pension_employee,
            'total_pension_employer': total_pension_employer,
            'total_net': total_net,
            'payslips': payslips
        }


# Singleton instance
payroll_service = PayrollService()
