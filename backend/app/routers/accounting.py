"""
Accounting Router - Chart of Accounts, Journal Vouchers, Ledger
"""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime
from pydantic import BaseModel
from enum import Enum

from ..database import get_db
from ..security import get_current_user
from ..models.account import Account, AccountType, LedgerEntry, JournalVoucher

router = APIRouter(prefix="/accounting", tags=["Accounting"])


# === Pydantic Schemas ===

class AccountCreate(BaseModel):
    code: str
    name: str
    type: AccountType
    description: Optional[str] = None
    parent_id: Optional[int] = None
    opening_balance: float = 0
    branch_id: int

class AccountUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    is_active: Optional[bool] = None

class JournalVoucherCreate(BaseModel):
    transaction_date: datetime
    description: Optional[str] = None
    reference: Optional[str] = None
    entries: List[dict]  # [{account_id, debit, credit, description}]
    branch_id: int

class JournalVoucherUpdate(BaseModel):
    description: Optional[str] = None
    reference: Optional[str] = None


# === Chart of Accounts ===

@router.get("/accounts")
async def list_accounts(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, le=500),
    account_type: Optional[AccountType] = None,
    is_active: Optional[bool] = None,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """List all accounts for tenant"""
    tenant_id = current_user["tenant_id"]

    query = db.query(Account).filter(Account.tenant_id == tenant_id)

    if account_type:
        query = query.filter(Account.type == account_type)
    if is_active is not None:
        query = query.filter(Account.is_active == is_active)

    accounts = query.order_by(Account.code).offset(skip).limit(limit).all()

    return {
        "items": [{
            "id": a.id,
            "code": a.code,
            "name": a.name,
            "type": a.type.value,
            "description": a.description,
            "parent_id": a.parent_id,
            "opening_balance": a.opening_balance,
            "is_active": a.is_active,
            "created_at": a.created_at.isoformat() if a.created_at else None
        } for a in accounts],
        "total": query.count()
    }


@router.post("/accounts")
async def create_account(
    account_data: AccountCreate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Create a new account"""
    tenant_id = current_user["tenant_id"]

    # Check for duplicate code
    existing = db.query(Account).filter(
        Account.tenant_id == tenant_id,
        Account.code == account_data.code
    ).first()

    if existing:
        raise HTTPException(status_code=400, detail="Account code already exists")

    account = Account(
        tenant_id=tenant_id,
        branch_id=account_data.branch_id,
        code=account_data.code,
        name=account_data.name,
        type=account_data.type,
        description=account_data.description,
        parent_id=account_data.parent_id,
        opening_balance=account_data.opening_balance
    )

    db.add(account)
    db.commit()
    db.refresh(account)

    return {"id": account.id, "message": "Account created successfully"}


@router.get("/accounts/{account_id}")
async def get_account(
    account_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Get account details"""
    tenant_id = current_user["tenant_id"]

    account = db.query(Account).filter(
        Account.id == account_id,
        Account.tenant_id == tenant_id
    ).first()

    if not account:
        raise HTTPException(status_code=404, detail="Account not found")

    # Calculate balance from ledger entries
    ledger_balance = db.query(
        db.func.sum(LedgerEntry.debit - LedgerEntry.credit)
    ).filter(
        LedgerEntry.account_id == account_id,
        LedgerEntry.tenant_id == tenant_id
    ).scalar() or 0

    return {
        "id": account.id,
        "code": account.code,
        "name": account.name,
        "type": account.type.value,
        "description": account.description,
        "parent_id": account.parent_id,
        "opening_balance": account.opening_balance,
        "current_balance": account.opening_balance + ledger_balance,
        "is_active": account.is_active,
        "created_at": account.created_at.isoformat() if account.created_at else None
    }


@router.put("/accounts/{account_id}")
async def update_account(
    account_id: int,
    account_data: AccountUpdate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Update account"""
    tenant_id = current_user["tenant_id"]

    account = db.query(Account).filter(
        Account.id == account_id,
        Account.tenant_id == tenant_id
    ).first()

    if not account:
        raise HTTPException(status_code=404, detail="Account not found")

    if account_data.name is not None:
        account.name = account_data.name
    if account_data.description is not None:
        account.description = account_data.description
    if account_data.is_active is not None:
        account.is_active = account_data.is_active

    db.commit()
    return {"message": "Account updated successfully"}


@router.delete("/accounts/{account_id}")
async def delete_account(
    account_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Delete account (soft delete)"""
    tenant_id = current_user["tenant_id"]

    account = db.query(Account).filter(
        Account.id == account_id,
        Account.tenant_id == tenant_id
    ).first()

    if not account:
        raise HTTPException(status_code=404, detail="Account not found")

    # Check if account has ledger entries
    has_entries = db.query(LedgerEntry).filter(
        LedgerEntry.account_id == account_id
    ).first()

    if has_entries:
        # Soft delete - just deactivate
        account.is_active = False
        db.commit()
        return {"message": "Account deactivated (has transactions)"}

    db.delete(account)
    db.commit()
    return {"message": "Account deleted successfully"}


# === Journal Vouchers ===

@router.get("/journal-vouchers")
async def list_journal_vouchers(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, le=200),
    is_posted: Optional[bool] = None,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """List journal vouchers"""
    tenant_id = current_user["tenant_id"]

    query = db.query(JournalVoucher).filter(
        JournalVoucher.tenant_id == tenant_id
    )

    if is_posted is not None:
        query = query.filter(JournalVoucher.is_posted == is_posted)

    vouchers = query.order_by(JournalVoucher.created_at.desc()).offset(skip).limit(limit).all()

    return {
        "items": [{
            "id": v.id,
            "voucher_number": v.voucher_number,
            "transaction_date": v.transaction_date.isoformat(),
            "description": v.description,
            "reference": v.reference,
            "is_posted": v.is_posted,
            "created_at": v.created_at.isoformat() if v.created_at else None
        } for v in vouchers],
        "total": query.count()
    }


@router.post("/journal-vouchers")
async def create_journal_voucher(
    voucher_data: JournalVoucherCreate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Create journal voucher with entries"""
    tenant_id = current_user["tenant_id"]

    # Generate voucher number
    last_voucher = db.query(JournalVoucher).filter(
        JournalVoucher.tenant_id == tenant_id
    ).order_by(JournalVoucher.id.desc()).first()

    voucher_num = f"JV-{datetime.now().year}-{(last_voucher.id + 1) if last_voucher else 1:05d}"

    # Validate entries - must balance
    total_debit = sum(e.get('debit', 0) for e in voucher_data.entries)
    total_credit = sum(e.get('credit', 0) for e in voucher_data.entries)

    if abs(total_debit - total_credit) > 0.01:
        raise HTTPException(
            status_code=400,
            detail=f"Journal entries must balance. Debit: {total_debit}, Credit: {total_credit}"
        )

    # Create voucher
    voucher = JournalVoucher(
        tenant_id=tenant_id,
        branch_id=voucher_data.branch_id,
        voucher_number=voucher_num,
        transaction_date=voucher_data.transaction_date,
        description=voucher_data.description,
        reference=voucher_data.reference
    )

    db.add(voucher)
    db.flush()

    # Create ledger entries
    for entry in voucher_data.entries:
        ledger_entry = LedgerEntry(
            tenant_id=tenant_id,
            branch_id=voucher_data.branch_id,
            account_id=entry['account_id'],
            transaction_date=voucher_data.transaction_date,
            description=entry.get('description'),
            debit=entry.get('debit', 0),
            credit=entry.get('credit', 0),
            journal_voucher_id=voucher.id
        )
        db.add(ledger_entry)

    db.commit()

    return {
        "id": voucher.id,
        "voucher_number": voucher_num,
        "message": "Journal voucher created successfully"
    }


@router.post("/journal-vouchers/{voucher_id}/post")
async def post_journal_voucher(
    voucher_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Post journal voucher to ledger"""
    tenant_id = current_user["tenant_id"]

    voucher = db.query(JournalVoucher).filter(
        JournalVoucher.id == voucher_id,
        JournalVoucher.tenant_id == tenant_id
    ).first()

    if not voucher:
        raise HTTPException(status_code=404, detail="Journal voucher not found")

    if voucher.is_posted:
        raise HTTPException(status_code=400, detail="Journal voucher already posted")

    voucher.is_posted = True
    voucher.posted_at = datetime.utcnow()

    db.commit()

    return {"message": "Journal voucher posted successfully"}


# === Ledger ===

@router.get("/ledger")
async def list_ledger_entries(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, le=500),
    account_id: Optional[int] = None,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """List ledger entries"""
    tenant_id = current_user["tenant_id"]

    query = db.query(LedgerEntry).filter(
        LedgerEntry.tenant_id == tenant_id
    )

    if account_id:
        query = query.filter(LedgerEntry.account_id == account_id)
    if start_date:
        query = query.filter(LedgerEntry.transaction_date >= start_date)
    if end_date:
        query = query.filter(LedgerEntry.transaction_date <= end_date)

    entries = query.order_by(LedgerEntry.transaction_date.desc()).offset(skip).limit(limit).all()

    # Get account names
    account_ids = list(set(e.account_id for e in entries))
    accounts = {a.id: a for a in db.query(Account).filter(Account.id.in_(account_ids)).all()}

    return {
        "items": [{
            "id": e.id,
            "account_id": e.account_id,
            "account_name": accounts.get(e.account_id, {}).name if e.account_id in accounts else "Unknown",
            "transaction_date": e.transaction_date.isoformat(),
            "description": e.description,
            "reference": e.reference,
            "debit": e.debit,
            "credit": e.credit,
            "running_balance": e.running_balance
        } for e in entries],
        "total": query.count()
    }


@router.get("/trial-balance")
async def get_trial_balance(
    as_of_date: Optional[datetime] = None,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Generate trial balance"""
    tenant_id = current_user["tenant_id"]

    # Get all active accounts
    accounts = db.query(Account).filter(
        Account.tenant_id == tenant_id,
        Account.is_active == True
    ).order_by(Account.code).all()

    trial_balance = []

    for account in accounts:
        # Calculate balance from ledger entries
        query = db.query(
            db.func.sum(LedgerEntry.debit).label('total_debit'),
            db.func.sum(LedgerEntry.credit).label('total_credit')
        ).filter(
            LedgerEntry.account_id == account.id,
            LedgerEntry.tenant_id == tenant_id
        )

        if as_of_date:
            query = query.filter(LedgerEntry.transaction_date <= as_of_date)

        result = query.first()

        total_debit = result.total_debit or 0
        total_credit = result.total_credit or 0

        # Calculate balance based on account type
        if account.type in [AccountType.ASSET, AccountType.EXPENSE]:
            balance = account.opening_balance + total_debit - total_credit
            debit_balance = balance if balance > 0 else 0
            credit_balance = abs(balance) if balance < 0 else 0
        else:
            balance = account.opening_balance + total_credit - total_debit
            credit_balance = balance if balance > 0 else 0
            debit_balance = abs(balance) if balance < 0 else 0

        if abs(balance) > 0.01:  # Only show accounts with balance
            trial_balance.append({
                "code": account.code,
                "name": account.name,
                "type": account.type.value,
                "debit": round(debit_balance, 2),
                "credit": round(credit_balance, 2)
            })

    total_debits = sum(t['debit'] for t in trial_balance)
    total_credits = sum(t['credit'] for t in trial_balance)

    return {
        "as_of_date": as_of_date.isoformat() if as_of_date else datetime.now().isoformat(),
        "accounts": trial_balance,
        "total_debits": round(total_debits, 2),
        "total_credits": round(total_credits, 2),
        "is_balanced": abs(total_debits - total_credits) < 0.01
    }
