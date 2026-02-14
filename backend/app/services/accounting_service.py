"""
Accounting Service - Double-Entry Bookkeeping Engine
Core service for all accounting operations
"""

from typing import List, Dict, Any, Optional, Tuple
from sqlalchemy.orm import Session
from sqlalchemy import func, and_, or_
from datetime import datetime, date, timedelta
from decimal import Decimal
import logging

from ..models.account import Account, AccountType, LedgerEntry, JournalVoucher
from ..models.sales import SalesInvoice
from ..models.purchase import PurchaseBill
from ..models.expense import Expense, OtherIncome
from ..models.hr import Payslip
from ..models.banking import FundTransfer

logger = logging.getLogger(__name__)


class AccountingService:
    """Core accounting service for double-entry bookkeeping"""
    
    # ============================================
    # CHART OF ACCOUNTS
    # ============================================
    
    def get_account_by_code(self, db: Session, tenant_id: int, code: str) -> Optional[Account]:
        """Get account by code"""
        return db.query(Account).filter(
            Account.tenant_id == tenant_id,
            Account.code == code
        ).first()
    
    def get_account_by_name(self, db: Session, tenant_id: int, name: str) -> Optional[Account]:
        """Get account by name"""
        return db.query(Account).filter(
            Account.tenant_id == tenant_id,
            Account.name == name
        ).first()
    
    def get_accounts_by_type(self, db: Session, tenant_id: int, account_type: AccountType) -> List[Account]:
        """Get all accounts of a specific type"""
        return db.query(Account).filter(
            Account.tenant_id == tenant_id,
            Account.type == account_type,
            Account.is_active == True
        ).order_by(Account.code).all()
    
    def get_all_accounts(self, db: Session, tenant_id: int, branch_id: int = None) -> List[Dict]:
        """Get all accounts grouped by type"""
        query = db.query(Account).filter(
            Account.tenant_id == tenant_id,
            Account.is_active == True
        )
        
        if branch_id:
            query = query.filter(Account.branch_id == branch_id)
        
        accounts = query.order_by(Account.code).all()
        
        # Group by type
        grouped = {}
        for acc in accounts:
            type_name = acc.type.value.upper()
            if type_name not in grouped:
                grouped[type_name] = []
            grouped[type_name].append({
                'id': acc.id,
                'code': acc.code,
                'name': acc.name,
                'type': acc.type.value,
                'balance': self.get_account_balance(db, acc.id)
            })
        
        return grouped
    
    def create_account(
        self,
        db: Session,
        tenant_id: int,
        branch_id: int,
        code: str,
        name: str,
        account_type: AccountType,
        description: str = None,
        parent_id: int = None,
        opening_balance: float = 0
    ) -> Account:
        """Create new account"""
        account = Account(
            tenant_id=tenant_id,
            branch_id=branch_id,
            code=code,
            name=name,
            type=account_type,
            description=description,
            parent_id=parent_id,
            opening_balance=opening_balance
        )
        db.add(account)
        db.commit()
        db.refresh(account)
        return account
    
    # ============================================
    # LEDGER OPERATIONS
    # ============================================
    
    def get_account_balance(
        self,
        db: Session,
        account_id: int,
        as_of_date: date = None
    ) -> float:
        """Calculate account balance"""
        query = db.query(
            func.coalesce(func.sum(LedgerEntry.debit), 0).label('total_debit'),
            func.coalesce(func.sum(LedgerEntry.credit), 0).label('total_credit')
        ).filter(LedgerEntry.account_id == account_id)
        
        if as_of_date:
            query = query.filter(LedgerEntry.transaction_date <= as_of_date)
        
        result = query.first()
        
        account = db.query(Account).get(account_id)
        if not account:
            return 0
        
        # Debit increases assets and expenses, credit increases liabilities, equity, revenue
        total_debit = float(result.total_debit or 0)
        total_credit = float(result.total_credit or 0)
        opening = float(account.opening_balance or 0)
        
        if account.type in [AccountType.ASSET, AccountType.EXPENSE]:
            # Debit increases balance
            return opening + total_debit - total_credit
        else:
            # Credit increases balance
            return opening + total_credit - total_debit
    
    def post_journal_entry(
        self,
        db: Session,
        tenant_id: int,
        branch_id: int,
        entries: List[Dict],
        description: str = None,
        reference: str = None,
        transaction_date: date = None,
        source_type: str = None,
        source_id: int = None
    ) -> JournalVoucher:
        """
        Post a journal entry (double-entry)
        
        entries: List of {'account_id': int, 'debit': float, 'credit': float, 'description': str}
        """
        # Validate balanced entry
        total_debit = sum(e.get('debit', 0) for e in entries)
        total_credit = sum(e.get('credit', 0) for e in entries)
        
        if abs(total_debit - total_credit) > 0.01:
            raise ValueError(f"Journal entry not balanced. Debit: {total_debit}, Credit: {total_credit}")
        
        if not transaction_date:
            transaction_date = date.today()
        
        # Generate voucher number
        voucher_number = self._generate_voucher_number(db, tenant_id, transaction_date)
        
        # Create journal voucher
        voucher = JournalVoucher(
            tenant_id=tenant_id,
            branch_id=branch_id,
            voucher_number=voucher_number,
            transaction_date=transaction_date,
            description=description,
            reference=reference,
            is_posted=True,
            posted_at=datetime.utcnow()
        )
        db.add(voucher)
        db.flush()  # Get the ID
        
        # Create ledger entries
        for entry in entries:
            ledger_entry = LedgerEntry(
                tenant_id=tenant_id,
                branch_id=branch_id,
                account_id=entry['account_id'],
                transaction_date=transaction_date,
                description=entry.get('description', description),
                debit=entry.get('debit', 0),
                credit=entry.get('credit', 0),
                journal_voucher_id=voucher.id
            )
            
            # Set source reference
            if source_type == 'sales_invoice':
                ledger_entry.sales_invoice_id = source_id
            elif source_type == 'purchase_bill':
                ledger_entry.purchase_bill_id = source_id
            elif source_type == 'expense':
                ledger_entry.expense_id = source_id
            elif source_type == 'other_income':
                ledger_entry.other_income_id = source_id
            elif source_type == 'payslip':
                ledger_entry.payslip_id = source_id
            elif source_type == 'fund_transfer':
                ledger_entry.fund_transfer_id = source_id
            
            db.add(ledger_entry)
        
        db.commit()
        db.refresh(voucher)
        
        logger.info(f"Posted journal entry {voucher_number}: Debit={total_debit}, Credit={total_credit}")
        
        return voucher
    
    def _generate_voucher_number(self, db: Session, tenant_id: int, trans_date: date) -> str:
        """Generate sequential voucher number"""
        prefix = f"JV-{trans_date.year}-{trans_date.month:02d}-"
        
        # Get last voucher number for this month
        last_voucher = db.query(JournalVoucher).filter(
            JournalVoucher.tenant_id == tenant_id,
            JournalVoucher.voucher_number.like(f"{prefix}%")
        ).order_by(JournalVoucher.voucher_number.desc()).first()
        
        if last_voucher:
            last_num = int(last_voucher.voucher_number.split('-')[-1])
            new_num = last_num + 1
        else:
            new_num = 1
        
        return f"{prefix}{new_num:05d}"
    
    # ============================================
    # SALES INVOICE POSTING
    # ============================================
    
    def post_sales_invoice(self, db: Session, invoice: SalesInvoice) -> JournalVoucher:
        """Post sales invoice to ledger"""
        tenant_id = invoice.tenant_id
        branch_id = invoice.branch_id
        
        # Get accounts
        ar_account = self.get_account_by_name(db, tenant_id, "Accounts Receivable")
        sales_account = self.get_account_by_name(db, tenant_id, "Sales Revenue")
        vat_account = self.get_account_by_name(db, tenant_id, "VAT Payable")
        cogs_account = self.get_account_by_name(db, tenant_id, "Cost of Goods Sold")
        inventory_account = self.get_account_by_name(db, tenant_id, "Inventory")
        
        entries = []
        
        # Debit Accounts Receivable (total amount)
        entries.append({
            'account_id': ar_account.id,
            'debit': invoice.total_amount,
            'credit': 0,
            'description': f"Invoice {invoice.invoice_number} - {invoice.customer.name}"
        })
        
        # Credit Sales Revenue (subtotal)
        entries.append({
            'account_id': sales_account.id,
            'debit': 0,
            'credit': invoice.subtotal,
            'description': f"Sales - Invoice {invoice.invoice_number}"
        })
        
        # Credit VAT Payable (if applicable)
        if invoice.vat_amount > 0:
            entries.append({
                'account_id': vat_account.id,
                'debit': 0,
                'credit': invoice.vat_amount,
                'description': f"VAT - Invoice {invoice.invoice_number}"
            })
        
        # Post COGS and reduce inventory (if items have cost)
        # This would require calculating COGS from line items
        
        return self.post_journal_entry(
            db,
            tenant_id=tenant_id,
            branch_id=branch_id,
            entries=entries,
            description=f"Sales Invoice {invoice.invoice_number}",
            reference=invoice.invoice_number,
            transaction_date=invoice.invoice_date,
            source_type='sales_invoice',
            source_id=invoice.id
        )
    
    # ============================================
    # PURCHASE BILL POSTING
    # ============================================
    
    def post_purchase_bill(self, db: Session, bill: PurchaseBill) -> JournalVoucher:
        """Post purchase bill to ledger"""
        tenant_id = bill.tenant_id
        branch_id = bill.branch_id
        
        # Get accounts
        ap_account = self.get_account_by_name(db, tenant_id, "Accounts Payable")
        vat_account = self.get_account_by_name(db, tenant_id, "VAT Refundable")
        inventory_account = self.get_account_by_name(db, tenant_id, "Inventory")
        
        entries = []
        
        # Debit Inventory/Expense (total)
        entries.append({
            'account_id': inventory_account.id,
            'debit': bill.subtotal,
            'credit': 0,
            'description': f"Purchase - Bill {bill.bill_number}"
        })
        
        # Debit VAT Refundable (if applicable)
        if bill.vat_amount > 0:
            entries.append({
                'account_id': vat_account.id,
                'debit': bill.vat_amount,
                'credit': 0,
                'description': f"VAT - Bill {bill.bill_number}"
            })
        
        # Credit Accounts Payable
        entries.append({
            'account_id': ap_account.id,
            'debit': 0,
            'credit': bill.total_amount,
            'description': f"Bill {bill.bill_number} - {bill.vendor.name}"
        })
        
        return self.post_journal_entry(
            db,
            tenant_id=tenant_id,
            branch_id=branch_id,
            entries=entries,
            description=f"Purchase Bill {bill.bill_number}",
            reference=bill.bill_number,
            transaction_date=bill.bill_date,
            source_type='purchase_bill',
            source_id=bill.id
        )
    
    # ============================================
    # EXPENSE POSTING
    # ============================================
    
    def post_expense(self, db: Session, expense: Expense) -> JournalVoucher:
        """Post expense to ledger"""
        entries = [
            {
                'account_id': expense.expense_account_id,
                'debit': expense.total_amount,
                'credit': 0,
                'description': f"{expense.category} - {expense.description or expense.expense_number}"
            },
            {
                'account_id': expense.paid_from_account_id,
                'debit': 0,
                'credit': expense.total_amount,
                'description': f"Payment for {expense.expense_number}"
            }
        ]
        
        return self.post_journal_entry(
            db,
            tenant_id=expense.tenant_id,
            branch_id=expense.branch_id,
            entries=entries,
            description=f"Expense {expense.expense_number}",
            reference=expense.expense_number,
            transaction_date=expense.expense_date,
            source_type='expense',
            source_id=expense.id
        )
    
    # ============================================
    # OTHER INCOME POSTING
    # ============================================
    
    def post_other_income(self, db: Session, income: OtherIncome) -> JournalVoucher:
        """Post other income to ledger"""
        entries = [
            {
                'account_id': income.deposited_to_account_id,
                'debit': income.amount,
                'credit': 0,
                'description': f"Income - {income.description or income.income_number}"
            },
            {
                'account_id': income.income_account_id,
                'debit': 0,
                'credit': income.amount,
                'description': f"Income received - {income.income_number}"
            }
        ]
        
        return self.post_journal_entry(
            db,
            tenant_id=income.tenant_id,
            branch_id=income.branch_id,
            entries=entries,
            description=f"Other Income {income.income_number}",
            reference=income.income_number,
            transaction_date=income.income_date,
            source_type='other_income',
            source_id=income.id
        )
    
    # ============================================
    # FUND TRANSFER POSTING
    # ============================================
    
    def post_fund_transfer(self, db: Session, transfer: FundTransfer) -> JournalVoucher:
        """Post fund transfer to ledger"""
        entries = [
            {
                'account_id': transfer.to_account_id,
                'debit': transfer.amount,
                'credit': 0,
                'description': f"Transfer from - {transfer.description or ''}"
            },
            {
                'account_id': transfer.from_account_id,
                'debit': 0,
                'credit': transfer.amount,
                'description': f"Transfer to - {transfer.description or ''}"
            }
        ]
        
        return self.post_journal_entry(
            db,
            tenant_id=transfer.tenant_id,
            branch_id=transfer.branch_id,
            entries=entries,
            description=f"Fund Transfer",
            transaction_date=transfer.transfer_date,
            source_type='fund_transfer',
            source_id=transfer.id
        )
    
    # ============================================
    # TRIAL BALANCE
    # ============================================
    
    def get_trial_balance(
        self,
        db: Session,
        tenant_id: int,
        branch_id: int = None,
        as_of_date: date = None
    ) -> Dict:
        """Generate trial balance"""
        if not as_of_date:
            as_of_date = date.today()
        
        # Get all accounts
        query = db.query(Account).filter(
            Account.tenant_id == tenant_id,
            Account.is_active == True
        )
        
        if branch_id:
            query = query.filter(Account.branch_id == branch_id)
        
        accounts = query.order_by(Account.code).all()
        
        trial_balance = []
        total_debit = 0
        total_credit = 0
        
        for account in accounts:
            balance = self.get_account_balance(db, account.id, as_of_date)
            
            if abs(balance) > 0.01:  # Only show accounts with balance
                debit = 0
                credit = 0
                
                if account.type in [AccountType.ASSET, AccountType.EXPENSE]:
                    if balance > 0:
                        debit = balance
                    else:
                        credit = abs(balance)
                else:
                    if balance > 0:
                        credit = balance
                    else:
                        debit = abs(balance)
                
                trial_balance.append({
                    'code': account.code,
                    'name': account.name,
                    'type': account.type.value,
                    'debit': debit,
                    'credit': credit
                })
                
                total_debit += debit
                total_credit += credit
        
        return {
            'as_of_date': as_of_date,
            'accounts': trial_balance,
            'total_debit': total_debit,
            'total_credit': total_credit,
            'is_balanced': abs(total_debit - total_credit) < 0.01
        }
    
    # ============================================
    # PROFIT & LOSS
    # ============================================
    
    def get_profit_and_loss(
        self,
        db: Session,
        tenant_id: int,
        branch_id: int = None,
        start_date: date = None,
        end_date: date = None
    ) -> Dict:
        """Generate Profit & Loss statement"""
        if not end_date:
            end_date = date.today()
        if not start_date:
            start_date = date(end_date.year, 1, 1)  # Start of year
        
        # Get revenue accounts
        revenue_accounts = self.get_accounts_by_type(db, tenant_id, AccountType.REVENUE)
        expense_accounts = self.get_accounts_by_type(db, tenant_id, AccountType.EXPENSE)
        
        revenue = []
        total_revenue = 0
        
        for account in revenue_accounts:
            # Calculate period movement
            balance = self.get_account_balance_for_period(
                db, account.id, start_date, end_date
            )
            if abs(balance) > 0.01:
                revenue.append({
                    'code': account.code,
                    'name': account.name,
                    'amount': balance
                })
                total_revenue += balance
        
        expenses = []
        total_expenses = 0
        
        for account in expense_accounts:
            balance = self.get_account_balance_for_period(
                db, account.id, start_date, end_date
            )
            if abs(balance) > 0.01:
                expenses.append({
                    'code': account.code,
                    'name': account.name,
                    'amount': balance
                })
                total_expenses += balance
        
        gross_profit = total_revenue
        net_profit = total_revenue - total_expenses
        
        return {
            'start_date': start_date,
            'end_date': end_date,
            'revenue': revenue,
            'total_revenue': total_revenue,
            'expenses': expenses,
            'total_expenses': total_expenses,
            'gross_profit': gross_profit,
            'net_profit': net_profit
        }
    
    def get_account_balance_for_period(
        self,
        db: Session,
        account_id: int,
        start_date: date,
        end_date: date
    ) -> float:
        """Get account movement for a period"""
        result = db.query(
            func.coalesce(func.sum(LedgerEntry.debit), 0).label('total_debit'),
            func.coalesce(func.sum(LedgerEntry.credit), 0).label('total_credit')
        ).filter(
            LedgerEntry.account_id == account_id,
            LedgerEntry.transaction_date >= start_date,
            LedgerEntry.transaction_date <= end_date
        ).first()
        
        account = db.query(Account).get(account_id)
        
        total_debit = float(result.total_debit or 0)
        total_credit = float(result.total_credit or 0)
        
        if account.type in [AccountType.ASSET, AccountType.EXPENSE]:
            return total_debit - total_credit
        else:
            return total_credit - total_debit
    
    # ============================================
    # BALANCE SHEET
    # ============================================
    
    def get_balance_sheet(
        self,
        db: Session,
        tenant_id: int,
        branch_id: int = None,
        as_of_date: date = None
    ) -> Dict:
        """Generate Balance Sheet"""
        if not as_of_date:
            as_of_date = date.today()
        
        # Get accounts by type
        asset_accounts = self.get_accounts_by_type(db, tenant_id, AccountType.ASSET)
        liability_accounts = self.get_accounts_by_type(db, tenant_id, AccountType.LIABILITY)
        equity_accounts = self.get_accounts_by_type(db, tenant_id, AccountType.EQUITY)
        
        assets = {'current': [], 'non_current': [], 'total': 0}
        liabilities = {'current': [], 'non_current': [], 'total': 0}
        equity = {'accounts': [], 'total': 0}
        
        # Current asset codes (1000-1499)
        current_asset_codes = ['1000', '1100', '1200', '1300', '1400']
        
        for account in asset_accounts:
            balance = self.get_account_balance(db, account.id, as_of_date)
            if abs(balance) > 0.01:
                item = {
                    'code': account.code,
                    'name': account.name,
                    'amount': balance
                }
                if account.code[:2] in ['10', '11', '12', '13', '14']:
                    assets['current'].append(item)
                else:
                    assets['non_current'].append(item)
                assets['total'] += balance
        
        # Current liability codes (2000-2499)
        for account in liability_accounts:
            balance = self.get_account_balance(db, account.id, as_of_date)
            if abs(balance) > 0.01:
                item = {
                    'code': account.code,
                    'name': account.name,
                    'amount': balance
                }
                if account.code[:2] in ['20', '21', '22', '23', '24']:
                    liabilities['current'].append(item)
                else:
                    liabilities['non_current'].append(item)
                liabilities['total'] += balance
        
        for account in equity_accounts:
            balance = self.get_account_balance(db, account.id, as_of_date)
            if abs(balance) > 0.01:
                equity['accounts'].append({
                    'code': account.code,
                    'name': account.name,
                    'amount': balance
                })
                equity['total'] += balance
        
        # Calculate retained earnings (net profit)
        start_of_year = date(as_of_date.year, 1, 1)
        pnl = self.get_profit_and_loss(db, tenant_id, branch_id, start_of_year, as_of_date)
        
        # Add retained earnings
        if pnl['net_profit'] != 0:
            equity['accounts'].append({
                'code': '3100',
                'name': 'Retained Earnings',
                'amount': pnl['net_profit']
            })
            equity['total'] += pnl['net_profit']
        
        return {
            'as_of_date': as_of_date,
            'assets': assets,
            'liabilities': liabilities,
            'equity': equity,
            'total_assets': assets['total'],
            'total_liabilities_equity': liabilities['total'] + equity['total'],
            'is_balanced': abs(assets['total'] - (liabilities['total'] + equity['total'])) < 0.01
        }


# Singleton instance
accounting_service = AccountingService()
