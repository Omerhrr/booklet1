"""
Banking Router - Bank Accounts, Fund Transfers, Reconciliation
"""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime
from pydantic import BaseModel

from ..database import get_db
from ..security import get_current_user
from ..models.banking import BankAccount, FundTransfer, BankReconciliation

router = APIRouter(prefix="/banking", tags=["Banking"])


# === Pydantic Schemas ===

class BankAccountCreate(BaseModel):
    bank_name: str
    account_name: str
    account_number: str
    currency: str = "NGN"
    account_type: str = "current"  # current, savings
    opening_balance: float = 0
    branch_id: int

class BankAccountUpdate(BaseModel):
    account_name: Optional[str] = None
    is_active: Optional[bool] = None

class FundTransferCreate(BaseModel):
    from_account_id: int
    to_account_id: int
    amount: float
    transfer_date: datetime
    reference: Optional[str] = None
    notes: Optional[str] = None
    branch_id: int


# === Bank Accounts ===

@router.get("/accounts")
async def list_bank_accounts(
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """List bank accounts"""
    tenant_id = current_user["tenant_id"]

    accounts = db.query(BankAccount).filter(
        BankAccount.tenant_id == tenant_id,
        BankAccount.is_active == True
    ).order_by(BankAccount.bank_name).all()

    return {
        "items": [{
            "id": a.id,
            "bank_name": a.bank_name,
            "account_name": a.account_name,
            "account_number": a.account_number,
            "currency": a.currency,
            "account_type": a.account_type,
            "opening_balance": a.opening_balance,
            "current_balance": a.current_balance,
            "is_active": a.is_active
        } for a in accounts]
    }


@router.post("/accounts")
async def create_bank_account(
    account_data: BankAccountCreate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Create bank account"""
    tenant_id = current_user["tenant_id"]

    account = BankAccount(
        tenant_id=tenant_id,
        branch_id=account_data.branch_id,
        bank_name=account_data.bank_name,
        account_name=account_data.account_name,
        account_number=account_data.account_number,
        currency=account_data.currency,
        account_type=account_data.account_type,
        opening_balance=account_data.opening_balance,
        current_balance=account_data.opening_balance
    )

    db.add(account)
    db.commit()
    db.refresh(account)

    return {"id": account.id, "message": "Bank account created successfully"}


@router.get("/accounts/{account_id}")
async def get_bank_account(
    account_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Get bank account details"""
    tenant_id = current_user["tenant_id"]

    account = db.query(BankAccount).filter(
        BankAccount.id == account_id,
        BankAccount.tenant_id == tenant_id
    ).first()

    if not account:
        raise HTTPException(status_code=404, detail="Bank account not found")

    # Get recent transactions
    transfers = db.query(FundTransfer).filter(
        (FundTransfer.from_account_id == account_id) |
        (FundTransfer.to_account_id == account_id)
    ).order_by(FundTransfer.transfer_date.desc()).limit(10).all()

    return {
        "id": account.id,
        "bank_name": account.bank_name,
        "account_name": account.account_name,
        "account_number": account.account_number,
        "currency": account.currency,
        "account_type": account.account_type,
        "opening_balance": account.opening_balance,
        "current_balance": account.current_balance,
        "is_active": account.is_active,
        "recent_transactions": [{
            "id": t.id,
            "type": "out" if t.from_account_id == account_id else "in",
            "amount": t.amount,
            "reference": t.reference,
            "date": t.transfer_date.isoformat()
        } for t in transfers]
    }


# === Fund Transfers ===

@router.get("/transfers")
async def list_transfers(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, le=200),
    account_id: Optional[int] = None,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """List fund transfers"""
    tenant_id = current_user["tenant_id"]

    query = db.query(FundTransfer).filter(FundTransfer.tenant_id == tenant_id)

    if account_id:
        query = query.filter(
            (FundTransfer.from_account_id == account_id) |
            (FundTransfer.to_account_id == account_id)
        )

    transfers = query.order_by(FundTransfer.transfer_date.desc()).offset(skip).limit(limit).all()

    # Get account names
    account_ids = set()
    for t in transfers:
        account_ids.add(t.from_account_id)
        account_ids.add(t.to_account_id)

    accounts = {a.id: a for a in db.query(BankAccount).filter(BankAccount.id.in_(account_ids)).all()}

    return {
        "items": [{
            "id": t.id,
            "from_account": accounts.get(t.from_account_id, BankAccount(bank_name="Unknown")).bank_name,
            "to_account": accounts.get(t.to_account_id, BankAccount(bank_name="Unknown")).bank_name,
            "amount": t.amount,
            "transfer_date": t.transfer_date.isoformat(),
            "reference": t.reference,
            "status": t.status
        } for t in transfers],
        "total": query.count()
    }


@router.post("/transfers")
async def create_transfer(
    transfer_data: FundTransferCreate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Create fund transfer"""
    tenant_id = current_user["tenant_id"]

    # Verify accounts exist
    from_account = db.query(BankAccount).filter(
        BankAccount.id == transfer_data.from_account_id,
        BankAccount.tenant_id == tenant_id
    ).first()

    to_account = db.query(BankAccount).filter(
        BankAccount.id == transfer_data.to_account_id,
        BankAccount.tenant_id == tenant_id
    ).first()

    if not from_account or not to_account:
        raise HTTPException(status_code=404, detail="Bank account not found")

    if from_account.current_balance < transfer_data.amount:
        raise HTTPException(status_code=400, detail="Insufficient funds")

    # Create transfer
    transfer = FundTransfer(
        tenant_id=tenant_id,
        branch_id=transfer_data.branch_id,
        from_account_id=transfer_data.from_account_id,
        to_account_id=transfer_data.to_account_id,
        amount=transfer_data.amount,
        transfer_date=transfer_data.transfer_date,
        reference=transfer_data.reference,
        notes=transfer_data.notes,
        status="completed"
    )

    db.add(transfer)

    # Update balances
    from_account.current_balance -= transfer_data.amount
    to_account.current_balance += transfer_data.amount

    db.commit()

    return {
        "id": transfer.id,
        "message": "Transfer completed successfully"
    }


# === Dashboard ===

@router.get("/dashboard")
async def get_banking_dashboard(
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Get banking dashboard statistics"""
    tenant_id = current_user["tenant_id"]

    accounts = db.query(BankAccount).filter(
        BankAccount.tenant_id == tenant_id,
        BankAccount.is_active == True
    ).all()

    total_balance = sum(a.current_balance for a in accounts)
    account_count = len(accounts)

    # Pending reconciliations
    pending = db.query(BankReconciliation).filter(
        BankReconciliation.tenant_id == tenant_id,
        BankReconciliation.is_reconciled == False
    ).count()

    return {
        "total_balance": total_balance,
        "account_count": account_count,
        "pending_reconciliations": pending,
        "accounts_summary": [{
            "bank_name": a.bank_name,
            "account_number": a.account_number,
            "balance": a.current_balance,
            "currency": a.currency
        } for a in accounts]
    }
