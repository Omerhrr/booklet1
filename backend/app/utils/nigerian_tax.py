"""
Nigerian Tax Utilities
Handles PAYE, Pension, VAT, and other statutory deductions

PAYE (Pay As You Earn) Tax Brackets for Nigeria (as of 2024):
- First ₦300,000: 7%
- Next ₦300,000: 11%
- Next ₦500,000: 15%
- Next ₦500,000: 19%
- Next ₦1,600,000: 21%
- Over ₦3,200,000: 24%

Pension:
- Employee Contribution: 8% of gross salary
- Employer Contribution: 10% of gross salary

VAT:
- Standard Rate: 7.5%
"""

from decimal import Decimal, ROUND_HALF_UP
from typing import Optional, List, Dict, Tuple, Any
from dataclasses import dataclass
from enum import Enum


# ============================================
# PAYE TAX BRACKETS
# ============================================

@dataclass
class PAYEBand:
    """PAYE tax band"""
    lower_limit: Decimal
    upper_limit: Optional[Decimal]  # None means no upper limit
    rate: Decimal


# Nigerian PAYE Tax Brackets (2024)
PAYE_BRACKETS: List[PAYEBand] = [
    PAYEBand(Decimal('0'), Decimal('300000'), Decimal('0.07')),        # First ₦300,000 @ 7%
    PAYEBand(Decimal('300000'), Decimal('600000'), Decimal('0.11')),   # Next ₦300,000 @ 11%
    PAYEBand(Decimal('600000'), Decimal('1100000'), Decimal('0.15')),  # Next ₦500,000 @ 15%
    PAYEBand(Decimal('1100000'), Decimal('1600000'), Decimal('0.19')), # Next ₦500,000 @ 19%
    PAYEBand(Decimal('1600000'), Decimal('3200000'), Decimal('0.21')), # Next ₦1,600,000 @ 21%
    PAYEBand(Decimal('3200000'), None, Decimal('0.24')),               # Over ₦3,200,000 @ 24%
]


# ============================================
# PENSION RATES
# ============================================

PENSION_EMPLOYEE_RATE = Decimal('0.08')  # 8% employee contribution
PENSION_EMPLOYER_RATE = Decimal('0.10')  # 10% employer contribution


# ============================================
# VAT RATE
# ============================================

VAT_RATE = Decimal('0.075')  # 7.5% VAT


# ============================================
# CONSOLIDATED RELIEF ALLOWANCE (CRA)
# ============================================

CRA_PERCENTAGE = Decimal('0.01')  # 1% of gross income
CRA_FIXED = Decimal('200000')      # ₦200,000
CRA_MIN_PERCENTAGE = Decimal('0.01')  # Minimum 1% of gross income


# ============================================
# WITHHOLDING TAX RATES
# ============================================

WHT_RATES = {
    'dividends': Decimal('0.10'),      # 10%
    'interest': Decimal('0.10'),       # 10%
    'rent': Decimal('0.10'),           # 10%
    'royalties': Decimal('0.05'),      # 5%
    'consultancy': Decimal('0.05'),    # 5%
    'management_fee': Decimal('0.05'), # 5%
    'contract': Decimal('0.05'),       # 5%
    'commission': Decimal('0.05'),     # 5%
}


class TaxCategory(str, Enum):
    """Tax categories"""
    PAYE = "paye"
    PENSION_EMPLOYEE = "pension_employee"
    PENSION_EMPLOYER = "pension_employer"
    VAT = "vat"
    WHT = "withholding_tax"
    NSITF = "nsitf"  # Nigeria Social Insurance Trust Fund
    ITF = "itf"      # Industrial Training Fund


# ============================================
# PAYE CALCULATIONS
# ============================================

def calculate_paye(
    annual_gross_income: Decimal,
    pension_contribution: Decimal = Decimal('0'),
    other_deductions: Decimal = Decimal('0'),
    allowances: Decimal = Decimal('0')
) -> Dict[str, Any]:
    """
    Calculate Nigerian PAYE tax.
    
    The calculation follows these steps:
    1. Calculate Consolidated Relief Allowance (CRA)
    2. Determine taxable income
    3. Apply tax brackets
    
    Args:
        annual_gross_income: Annual gross salary
        pension_contribution: Annual pension contribution (8% of gross)
        other_deductions: Other allowable deductions
        allowances: Tax-free allowances
    
    Returns:
        Dictionary with tax calculation details
    """
    # Calculate CRA (Consolidated Relief Allowance)
    # CRA is the higher of:
    # - ₦200,000 + 1% of gross income
    # - 1% of gross income
    cra_base = CRA_FIXED + (annual_gross_income * CRA_PERCENTAGE)
    cra_min = annual_gross_income * CRA_MIN_PERCENTAGE
    cra = max(cra_base, cra_min)
    
    # Calculate taxable income
    taxable_income = annual_gross_income - cra - pension_contribution - allowances - other_deductions
    
    # Ensure taxable income is not negative
    if taxable_income < 0:
        taxable_income = Decimal('0')
    
    # Calculate tax using progressive bands
    tax_breakdown = []
    total_tax = Decimal('0')
    remaining_income = taxable_income
    
    for i, band in enumerate(PAYE_BRACKETS):
        if remaining_income <= 0:
            break
        
        # Calculate taxable amount in this band
        if band.upper_limit:
            band_width = band.upper_limit - band.lower_limit
        else:
            band_width = None
        
        # Income that falls in this band
        if band.upper_limit:
            income_in_band = min(remaining_income, band.upper_limit - band.lower_limit)
        else:
            income_in_band = remaining_income
        
        if income_in_band > 0:
            tax_for_band = income_in_band * band.rate
            total_tax += tax_for_band
            
            tax_breakdown.append({
                'band': i + 1,
                'lower_limit': float(band.lower_limit),
                'upper_limit': float(band.upper_limit) if band.upper_limit else None,
                'rate_percentage': float(band.rate * 100),
                'income_in_band': float(income_in_band),
                'tax_for_band': float(tax_for_band)
            })
            
            remaining_income -= income_in_band
    
    # Monthly tax
    monthly_tax = total_tax / 12
    
    return {
        'annual_gross_income': float(annual_gross_income),
        'cra': float(cra),
        'pension_deduction': float(pension_contribution),
        'other_deductions': float(other_deductions),
        'allowances': float(allowances),
        'taxable_income': float(taxable_income),
        'tax_breakdown': tax_breakdown,
        'annual_tax': float(total_tax),
        'monthly_tax': float(monthly_tax),
        'effective_rate': float(total_tax / annual_gross_income * 100) if annual_gross_income > 0 else 0
    }


def get_paye_brackets() -> List[Dict[str, Any]]:
    """
    Get PAYE tax brackets.
    
    Returns:
        List of tax bracket dictionaries
    """
    return [
        {
            'band': i + 1,
            'lower_limit': float(band.lower_limit),
            'upper_limit': float(band.upper_limit) if band.upper_limit else None,
            'rate': float(band.rate * 100),
            'description': _describe_band(band, i)
        }
        for i, band in enumerate(PAYE_BRACKETS)
    ]


def _describe_band(band: PAYEBand, index: int) -> str:
    """Generate human-readable description for a tax band"""
    if band.upper_limit is None:
        return f"Over ₦{band.lower_limit:,.0f}"
    elif index == 0:
        return f"First ₦{band.upper_limit:,.0f}"
    else:
        return f"Next ₦{band.upper_limit - band.lower_limit:,.0f}"


# ============================================
# PENSION CALCULATIONS
# ============================================

def calculate_pension(
    gross_salary: Decimal,
    employee_rate: Decimal = PENSION_EMPLOYEE_RATE,
    employer_rate: Decimal = PENSION_EMPLOYER_RATE
) -> Dict[str, Any]:
    """
    Calculate Nigerian pension contributions.
    
    Args:
        gross_salary: Monthly gross salary
        employee_rate: Employee contribution rate (default 8%)
        employer_rate: Employer contribution rate (default 10%)
    
    Returns:
        Dictionary with pension calculation details
    """
    employee_contribution = gross_salary * employee_rate
    employer_contribution = gross_salary * employer_rate
    total_contribution = employee_contribution + employer_contribution
    
    return {
        'gross_salary': float(gross_salary),
        'employee_rate': float(employee_rate * 100),
        'employer_rate': float(employer_rate * 100),
        'employee_contribution': float(employee_contribution),
        'employer_contribution': float(employer_contribution),
        'total_contribution': float(total_contribution)
    }


# ============================================
# VAT CALCULATIONS
# ============================================

def calculate_vat(
    amount: Decimal,
    vat_rate: Decimal = VAT_RATE,
    inclusive: bool = False
) -> Dict[str, Any]:
    """
    Calculate VAT on an amount.
    
    Args:
        amount: The amount to calculate VAT on
        vat_rate: VAT rate (default 7.5%)
        inclusive: Whether the amount includes VAT
    
    Returns:
        Dictionary with VAT calculation details
    """
    if inclusive:
        # VAT is included in the amount
        # Extract VAT: VAT = Amount * (rate / (1 + rate))
        vat_amount = amount * (vat_rate / (1 + vat_rate))
        net_amount = amount - vat_amount
    else:
        # VAT is added to the amount
        vat_amount = amount * vat_rate
        net_amount = amount
    
    total_amount = net_amount + vat_amount
    
    return {
        'net_amount': float(net_amount),
        'vat_rate': float(vat_rate * 100),
        'vat_amount': float(vat_amount),
        'total_amount': float(total_amount),
        'inclusive': inclusive
    }


# ============================================
# WITHHOLDING TAX (WHT) CALCULATIONS
# ============================================

def calculate_wht(
    amount: Decimal,
    transaction_type: str
) -> Dict[str, Any]:
    """
    Calculate Withholding Tax (WHT).
    
    Args:
        amount: The amount to calculate WHT on
        transaction_type: Type of transaction
    
    Returns:
        Dictionary with WHT calculation details
    """
    rate = WHT_RATES.get(transaction_type.lower(), Decimal('0.05'))
    wht_amount = amount * rate
    
    return {
        'gross_amount': float(amount),
        'transaction_type': transaction_type,
        'rate': float(rate * 100),
        'wht_amount': float(wht_amount),
        'net_amount': float(amount - wht_amount)
    }


# ============================================
# FULL PAYROLL CALCULATION
# ============================================

def calculate_payroll(
    monthly_gross_salary: Decimal,
    allowances: Decimal = Decimal('0'),
    deductions: Decimal = Decimal('0'),
    pension_employee_rate: Decimal = PENSION_EMPLOYEE_RATE,
    pension_employer_rate: Decimal = PENSION_EMPLOYER_RATE
) -> Dict[str, Any]:
    """
    Calculate complete Nigerian payroll with all statutory deductions.
    
    Args:
        monthly_gross_salary: Monthly gross salary
        allowances: Additional allowances
        deductions: Other deductions
        pension_employee_rate: Employee pension rate (default 8%)
        pension_employer_rate: Employer pension rate (default 10%)
    
    Returns:
        Dictionary with complete payroll breakdown
    """
    # Calculate gross pay
    gross_pay = monthly_gross_salary + allowances
    
    # Calculate pension (annual for PAYE calculation)
    annual_gross = gross_pay * 12
    pension = calculate_pension(monthly_gross_salary, pension_employee_rate, pension_employer_rate)
    
    # Calculate PAYE
    paye = calculate_paye(
        annual_gross_income=annual_gross,
        pension_contribution=pension['employee_contribution'] * 12
    )
    
    # Net pay calculation
    total_deductions = (
        pension['employee_contribution'] +
        paye['monthly_tax'] +
        deductions
    )
    net_pay = gross_pay - total_deductions
    
    # Employer costs
    employer_cost = monthly_gross_salary + pension['employer_contribution']
    
    return {
        'monthly': {
            'gross_salary': float(monthly_gross_salary),
            'allowances': float(allowances),
            'gross_pay': float(gross_pay),
            'pension_employee': float(pension['employee_contribution']),
            'paye': float(paye['monthly_tax']),
            'other_deductions': float(deductions),
            'total_deductions': float(total_deductions),
            'net_pay': float(net_pay),
        },
        'annual': {
            'gross_salary': float(monthly_gross_salary * 12),
            'allowances': float(allowances * 12),
            'gross_pay': float(gross_pay * 12),
            'pension_employee': float(pension['employee_contribution'] * 12),
            'paye': float(paye['annual_tax']),
            'other_deductions': float(deductions * 12),
            'total_deductions': float(total_deductions * 12),
            'net_pay': float(net_pay * 12),
        },
        'employer': {
            'gross_salary': float(monthly_gross_salary),
            'pension_employer': float(pension['employer_contribution']),
            'total_cost': float(employer_cost),
        },
        'statutory': {
            'pension': pension,
            'paye': paye,
        },
        'summary': {
            'gross_pay': float(gross_pay),
            'total_deductions': float(total_deductions),
            'net_pay': float(net_pay),
            'deduction_ratio': float(total_deductions / gross_pay * 100) if gross_pay > 0 else 0,
        }
    }


# ============================================
# TAX COMPLIANCE HELPERS
# ============================================

def check_tax_registration_threshold(
    annual_turnover: Decimal,
    vat_threshold: Decimal = Decimal('25000000')  # ₦25 million
) -> Dict[str, bool]:
    """
    Check if business meets tax registration thresholds.
    
    Args:
        annual_turnover: Annual business turnover
        vat_threshold: VAT registration threshold
    
    Returns:
        Dictionary indicating which taxes apply
    """
    return {
        'vat_registration_required': annual_turnover >= vat_threshold,
        'cit_required': True,  # All companies must pay Company Income Tax
        'paye_required': True,  # All employers must deduct PAYE
        'pension_required': True,  # Employers with 15+ employees
    }


def calculate_company_income_tax(
    profit_before_tax: Decimal,
    is_small_company: bool = False,
    is_medium_company: bool = False
) -> Dict[str, Any]:
    """
    Calculate Nigerian Company Income Tax (CIT).
    
    Tax rates:
    - Small companies (turnover < ₦25M): 0%
    - Medium companies (turnover ₦25M-₦100M): 15%
    - Large companies (turnover > ₦100M): 30%
    
    Args:
        profit_before_tax: Profit before tax
        is_small_company: Whether company qualifies as small
        is_medium_company: Whether company qualifies as medium
    
    Returns:
        Dictionary with CIT calculation
    """
    if is_small_company:
        rate = Decimal('0')
        category = 'small'
    elif is_medium_company:
        rate = Decimal('0.15')
        category = 'medium'
    else:
        rate = Decimal('0.30')
        category = 'large'
    
    tax_amount = profit_before_tax * rate
    profit_after_tax = profit_before_tax - tax_amount
    
    return {
        'profit_before_tax': float(profit_before_tax),
        'tax_rate': float(rate * 100),
        'tax_category': category,
        'tax_amount': float(tax_amount),
        'profit_after_tax': float(profit_after_tax)
    }


# ============================================
# UTILITY FUNCTIONS
# ============================================

def round_to_naira(amount: Decimal) -> Decimal:
    """Round amount to nearest naira"""
    return amount.quantize(Decimal('1'), rounding=ROUND_HALF_UP)


def round_to_kobo(amount: Decimal) -> Decimal:
    """Round amount to nearest kobo (2 decimal places)"""
    return amount.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)


def format_tax_amount(amount: float) -> str:
    """Format tax amount with naira symbol"""
    return f"₦{amount:,.2f}"


# Export all public functions and constants
__all__ = [
    # PAYE
    'calculate_paye',
    'get_paye_brackets',
    'PAYE_BRACKETS',
    'PAYEBand',
    
    # Pension
    'calculate_pension',
    'PENSION_EMPLOYEE_RATE',
    'PENSION_EMPLOYER_RATE',
    
    # VAT
    'calculate_vat',
    'VAT_RATE',
    
    # WHT
    'calculate_wht',
    'WHT_RATES',
    
    # Payroll
    'calculate_payroll',
    
    # Compliance
    'check_tax_registration_threshold',
    'calculate_company_income_tax',
    
    # Utilities
    'round_to_naira',
    'round_to_kobo',
    'format_tax_amount',
    
    # Enums
    'TaxCategory',
]
