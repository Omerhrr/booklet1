"""
Tests for Accounting Service
"""

import pytest
from datetime import date, timedelta
from decimal import Decimal

from ..app.services.accounting_service import accounting_service
from ..app.models.account import Account, AccountType, LedgerEntry, JournalVoucher


class TestAccountingService:
    """Tests for accounting operations"""
    
    def test_create_account(self, db, tenant, branch):
        """Test creating an account"""
        account = accounting_service.create_account(
            db,
            tenant_id=tenant.id,
            branch_id=branch.id,
            code="1000",
            name="Cash",
            account_type=AccountType.ASSET
        )
        
        assert account.id is not None
        assert account.code == "1000"
        assert account.name == "Cash"
        assert account.type == AccountType.ASSET
    
    def test_get_account_by_code(self, db, tenant, branch):
        """Test getting account by code"""
        # Create account
        accounting_service.create_account(
            db,
            tenant_id=tenant.id,
            branch_id=branch.id,
            code="1100",
            name="Bank",
            account_type=AccountType.ASSET
        )
        
        # Get account
        account = accounting_service.get_account_by_code(db, tenant.id, "1100")
        
        assert account is not None
        assert account.name == "Bank"
    
    def test_post_journal_entry(self, db, tenant, branch):
        """Test posting a journal entry"""
        # Create accounts
        cash = accounting_service.create_account(
            db, tenant.id, branch.id, "1000", "Cash", AccountType.ASSET
        )
        revenue = accounting_service.create_account(
            db, tenant.id, branch.id, "4000", "Sales Revenue", AccountType.REVENUE
        )
        
        # Post journal entry
        entries = [
            {'account_id': cash.id, 'debit': 1000, 'credit': 0},
            {'account_id': revenue.id, 'debit': 0, 'credit': 1000}
        ]
        
        voucher = accounting_service.post_journal_entry(
            db,
            tenant_id=tenant.id,
            branch_id=branch.id,
            entries=entries,
            description="Test entry"
        )
        
        assert voucher.id is not None
        assert voucher.is_posted == True
        
        # Check ledger entries created
        ledger_entries = db.query(LedgerEntry).filter(
            LedgerEntry.journal_voucher_id == voucher.id
        ).all()
        
        assert len(ledger_entries) == 2
    
    def test_unbalanced_journal_entry_raises_error(self, db, tenant, branch):
        """Test that unbalanced entry raises error"""
        cash = accounting_service.create_account(
            db, tenant.id, branch.id, "1000", "Cash", AccountType.ASSET
        )
        revenue = accounting_service.create_account(
            db, tenant.id, branch.id, "4000", "Revenue", AccountType.REVENUE
        )
        
        entries = [
            {'account_id': cash.id, 'debit': 1000, 'credit': 0},
            {'account_id': revenue.id, 'debit': 0, 'credit': 500}  # Not balanced!
        ]
        
        with pytest.raises(ValueError) as exc_info:
            accounting_service.post_journal_entry(
                db, tenant.id, branch.id, entries
            )
        
        assert "not balanced" in str(exc_info.value)
    
    def test_get_account_balance(self, db, tenant, branch):
        """Test calculating account balance"""
        cash = accounting_service.create_account(
            db, tenant.id, branch.id, "1000", "Cash", AccountType.ASSET
        )
        revenue = accounting_service.create_account(
            db, tenant.id, branch.id, "4000", "Revenue", AccountType.REVENUE
        )
        
        # Post entry
        accounting_service.post_journal_entry(
            db, tenant.id, branch.id,
            [
                {'account_id': cash.id, 'debit': 5000, 'credit': 0},
                {'account_id': revenue.id, 'debit': 0, 'credit': 5000}
            ]
        )
        
        # Check balance
        balance = accounting_service.get_account_balance(db, cash.id)
        assert balance == 5000
        
        revenue_balance = accounting_service.get_account_balance(db, revenue.id)
        assert revenue_balance == 5000  # Credit increases revenue
    
    def test_trial_balance(self, db, tenant, branch):
        """Test trial balance generation"""
        # Create accounts
        cash = accounting_service.create_account(
            db, tenant.id, branch.id, "1000", "Cash", AccountType.ASSET
        )
        revenue = accounting_service.create_account(
            db, tenant.id, branch.id, "4000", "Revenue", AccountType.REVENUE
        )
        expense = accounting_service.create_account(
            db, tenant.id, branch.id, "5000", "Expense", AccountType.EXPENSE
        )
        
        # Post entries
        accounting_service.post_journal_entry(
            db, tenant.id, branch.id,
            [
                {'account_id': cash.id, 'debit': 10000, 'credit': 0},
                {'account_id': revenue.id, 'debit': 0, 'credit': 10000}
            ]
        )
        
        accounting_service.post_journal_entry(
            db, tenant.id, branch.id,
            [
                {'account_id': expense.id, 'debit': 2000, 'credit': 0},
                {'account_id': cash.id, 'debit': 0, 'credit': 2000}
            ]
        )
        
        # Get trial balance
        tb = accounting_service.get_trial_balance(db, tenant.id)
        
        assert tb['is_balanced'] == True
        assert tb['total_debit'] == tb['total_credit']


class TestPayrollCalculations:
    """Tests for Nigerian payroll calculations"""
    
    def test_paye_calculation(self):
        """Test PAYE tax calculation"""
        from ..app.services.payroll_service import payroll_service
        
        # Test various income levels
        # Annual gross: ₦600,000
        annual_gross = 600000
        
        paye = payroll_service.calculate_paye(annual_gross)
        
        # Should be roughly:
        # First ₦300,000 @ 7% = ₦21,000
        # Next ₦300,000 @ 11% = ₦33,000
        # Less CRA
        # Total should be reasonable
        
        assert paye > 0
        assert paye < annual_gross  # Tax should be less than income
    
    def test_pension_calculation(self):
        """Test pension calculation"""
        from ..app.services.payroll_service import payroll_service
        
        gross = 100000  # ₦100,000 monthly
        
        employee_pension = payroll_service.calculate_pension_employee(gross)
        employer_pension = payroll_service.calculate_pension_employer(gross)
        
        assert employee_pension == 8000  # 8%
        assert employer_pension == 10000  # 10%
    
    def test_payslip_calculation(self, db, tenant, branch):
        """Test full payslip calculation"""
        from ..app.services.payroll_service import payroll_service
        from ..app.models.hr import Employee, PayrollConfig
        
        # Create employee
        employee = Employee(
            tenant_id=tenant.id,
            branch_id=branch.id,
            full_name="John Doe",
            email="john@test.com",
            hire_date=date.today()
        )
        db.add(employee)
        db.flush()
        
        # Create payroll config
        config = PayrollConfig(
            employee_id=employee.id,
            gross_salary=200000  # ₦200,000 monthly
        )
        db.add(config)
        db.commit()
        
        # Calculate payslip
        calc = payroll_service.calculate_payslip(
            employee,
            date.today() - timedelta(days=30),
            date.today()
        )
        
        assert calc['gross_pay'] > 0
        assert calc['paye'] > 0
        assert calc['pension_employee'] > 0
        assert calc['net_pay'] < calc['gross_pay']


class TestCurrencyFormatting:
    """Tests for Nigerian Naira formatting"""
    
    def test_format_naira(self):
        """Test Naira formatting"""
        from ..app.services.currency_service import format_naira
        
        assert format_naira(1000) == "₦1,000.00"
        assert format_naira(1234567.89) == "₦1,234,567.89"
        assert format_naira(0) == "₦0.00"
        assert format_naira(None) == "-"
    
    def test_parse_naira(self):
        """Test parsing Naira string"""
        from ..app.services.currency_service import parse_naira
        
        assert parse_naira("₦1,000.00") == 1000.0
        assert parse_naira("1,234.56") == 1234.56
    
    def test_number_to_words(self):
        """Test number to words conversion"""
        from ..app.services.currency_service import number_to_words_naira
        
        words = number_to_words_naira(1500)
        assert "Naira" in words
        
        words_with_kobo = number_to_words_naira(1500.50)
        assert "Kobo" in words_with_kobo
