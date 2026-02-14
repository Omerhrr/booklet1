"""
Account CRUD Operations
"""

from typing import Optional, List
from sqlalchemy.orm import Session
from sqlalchemy import func

from ..models.account import Account, AccountType, LedgerEntry, JournalVoucher


class CRUDAccount:
    
    def get(self, db: Session, account_id: int) -> Optional[Account]:
        return db.query(Account).filter(Account.id == account_id).first()
    
    def get_by_code(self, db: Session, tenant_id: int, code: str) -> Optional[Account]:
        return db.query(Account).filter(
            Account.tenant_id == tenant_id,
            Account.code == code
        ).first()
    
    def get_by_name(self, db: Session, tenant_id: int, name: str) -> Optional[Account]:
        return db.query(Account).filter(
            Account.tenant_id == tenant_id,
            Account.name == name
        ).first()
    
    def get_multi(
        self,
        db: Session,
        tenant_id: int,
        branch_id: int = None,
        account_type: AccountType = None,
        is_active: bool = None,
        skip: int = 0,
        limit: int = 100
    ) -> List[Account]:
        query = db.query(Account).filter(Account.tenant_id == tenant_id)
        
        if branch_id:
            query = query.filter(Account.branch_id == branch_id)
        
        if account_type:
            query = query.filter(Account.type == account_type)
        
        if is_active is not None:
            query = query.filter(Account.is_active == is_active)
        
        return query.order_by(Account.code).offset(skip).limit(limit).all()
    
    def get_by_type(self, db: Session, tenant_id: int, account_type: AccountType) -> List[Account]:
        return db.query(Account).filter(
            Account.tenant_id == tenant_id,
            Account.type == account_type,
            Account.is_active == True
        ).order_by(Account.code).all()
    
    def create(
        self,
        db: Session,
        *,
        tenant_id: int,
        branch_id: int,
        code: str,
        name: str,
        account_type: AccountType,
        description: str = None,
        parent_id: int = None,
        is_system_account: bool = False,
        opening_balance: float = 0
    ) -> Account:
        account = Account(
            tenant_id=tenant_id,
            branch_id=branch_id,
            code=code,
            name=name,
            type=account_type,
            description=description,
            parent_id=parent_id,
            is_system_account=is_system_account,
            opening_balance=opening_balance
        )
        db.add(account)
        db.commit()
        db.refresh(account)
        return account
    
    def update(self, db: Session, account: Account, **kwargs) -> Account:
        for key, value in kwargs.items():
            if hasattr(account, key):
                setattr(account, key, value)
        db.commit()
        db.refresh(account)
        return account
    
    def delete(self, db: Session, account_id: int) -> bool:
        account = self.get(db, account_id)
        if account and not account.is_system_account:
            # Check if account has transactions
            has_transactions = db.query(LedgerEntry).filter(
                LedgerEntry.account_id == account_id
            ).first()
            
            if has_transactions:
                # Soft delete
                account.is_active = False
            else:
                db.delete(account)
            
            db.commit()
            return True
        return False


class CRUDLedger:
    
    def get_entries(
        self,
        db: Session,
        tenant_id: int,
        account_id: int = None,
        branch_id: int = None,
        start_date = None,
        end_date = None,
        skip: int = 0,
        limit: int = 100
    ) -> List[LedgerEntry]:
        query = db.query(LedgerEntry).filter(LedgerEntry.tenant_id == tenant_id)
        
        if account_id:
            query = query.filter(LedgerEntry.account_id == account_id)
        
        if branch_id:
            query = query.filter(LedgerEntry.branch_id == branch_id)
        
        if start_date:
            query = query.filter(LedgerEntry.transaction_date >= start_date)
        
        if end_date:
            query = query.filter(LedgerEntry.transaction_date <= end_date)
        
        return query.order_by(LedgerEntry.transaction_date.desc()).offset(skip).limit(limit).all()
    
    def get_account_balance(
        self,
        db: Session,
        account_id: int,
        as_of_date = None
    ) -> float:
        query = db.query(
            func.coalesce(func.sum(LedgerEntry.debit), 0).label('debit'),
            func.coalesce(func.sum(LedgerEntry.credit), 0).label('credit')
        ).filter(LedgerEntry.account_id == account_id)
        
        if as_of_date:
            query = query.filter(LedgerEntry.transaction_date <= as_of_date)
        
        result = query.first()
        account = db.query(Account).get(account_id)
        
        total_debit = float(result.debit or 0)
        total_credit = float(result.credit or 0)
        opening = float(account.opening_balance or 0) if account else 0
        
        if account and account.type in [AccountType.ASSET, AccountType.EXPENSE]:
            return opening + total_debit - total_credit
        else:
            return opening + total_credit - total_debit


class CRUDJournalVoucher:
    
    def get(self, db: Session, voucher_id: int) -> Optional[JournalVoucher]:
        return db.query(JournalVoucher).filter(JournalVoucher.id == voucher_id).first()
    
    def get_multi(
        self,
        db: Session,
        tenant_id: int,
        branch_id: int = None,
        skip: int = 0,
        limit: int = 50
    ) -> List[JournalVoucher]:
        query = db.query(JournalVoucher).filter(JournalVoucher.tenant_id == tenant_id)
        
        if branch_id:
            query = query.filter(JournalVoucher.branch_id == branch_id)
        
        return query.order_by(JournalVoucher.transaction_date.desc()).offset(skip).limit(limit).all()
    
    def create(
        self,
        db: Session,
        *,
        tenant_id: int,
        branch_id: int,
        transaction_date,
        entries: List[dict],
        description: str = None,
        reference: str = None
    ) -> JournalVoucher:
        """Create journal voucher with ledger entries"""
        # Validate balanced
        total_debit = sum(e.get('debit', 0) for e in entries)
        total_credit = sum(e.get('credit', 0) for e in entries)
        
        if abs(total_debit - total_credit) > 0.01:
            raise ValueError(f"Journal entry not balanced: Debit={total_debit}, Credit={total_credit}")
        
        # Generate voucher number
        voucher_number = self._generate_voucher_number(db, tenant_id, transaction_date)
        
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
        db.flush()
        
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
            db.add(ledger_entry)
        
        db.commit()
        db.refresh(voucher)
        return voucher
    
    def _generate_voucher_number(self, db: Session, tenant_id: int, trans_date) -> str:
        from datetime import datetime
        year = trans_date.year if hasattr(trans_date, 'year') else datetime.now().year
        month = trans_date.month if hasattr(trans_date, 'month') else datetime.now().month
        
        last_voucher = db.query(JournalVoucher).filter(
            JournalVoucher.tenant_id == tenant_id,
            JournalVoucher.voucher_number.like(f"JV-{year}{month:02d}-%")
        ).order_by(JournalVoucher.voucher_number.desc()).first()
        
        if last_voucher:
            last_num = int(last_voucher.voucher_number.split('-')[-1])
            new_num = last_num + 1
        else:
            new_num = 1
        
        return f"JV-{year}{month:02d}-{new_num:05d}"


account = CRUDAccount()
ledger = CRUDLedger()
journal_voucher = CRUDJournalVoucher()
