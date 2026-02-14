"""
Budget Router - Budget Management and Variance Analysis
"""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import Optional, List
from datetime import datetime
from pydantic import BaseModel
from enum import Enum

from ..database import get_db
from ..security import get_current_user
from ..models.budget import Budget, BudgetLine

router = APIRouter(prefix="/budget", tags=["Budget"])


class BudgetPeriod(str, Enum):
    MONTHLY = "monthly"
    QUARTERLY = "quarterly"
    YEARLY = "yearly"


class BudgetLineCreate(BaseModel):
    account_id: int
    amount: float
    notes: Optional[str] = None


class BudgetCreate(BaseModel):
    name: str
    period: BudgetPeriod
    start_date: datetime
    end_date: datetime
    lines: List[BudgetLineCreate]
    branch_id: int


@router.get("")
async def list_budgets(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, le=200),
    is_active: Optional[bool] = None,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """List budgets"""
    tenant_id = current_user["tenant_id"]

    query = db.query(Budget).filter(Budget.tenant_id == tenant_id)

    if is_active is not None:
        query = query.filter(Budget.is_active == is_active)

    budgets = query.order_by(Budget.start_date.desc()).offset(skip).limit(limit).all()

    return {
        "items": [{
            "id": b.id,
            "name": b.name,
            "period": b.period,
            "start_date": b.start_date.isoformat(),
            "end_date": b.end_date.isoformat(),
            "total_budget": b.total_budget,
            "is_active": b.is_active
        } for b in budgets],
        "total": query.count()
    }


@router.post("")
async def create_budget(
    budget_data: BudgetCreate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Create budget"""
    tenant_id = current_user["tenant_id"]

    # Calculate total
    total_budget = sum(line.amount for line in budget_data.lines)

    budget = Budget(
        tenant_id=tenant_id,
        branch_id=budget_data.branch_id,
        name=budget_data.name,
        period=budget_data.period.value,
        start_date=budget_data.start_date,
        end_date=budget_data.end_date,
        total_budget=total_budget
    )

    db.add(budget)
    db.flush()

    # Add budget lines
    for line_data in budget_data.lines:
        line = BudgetLine(
            budget_id=budget.id,
            account_id=line_data.account_id,
            amount=line_data.amount,
            notes=line_data.notes
        )
        db.add(line)

    db.commit()

    return {"id": budget.id, "message": "Budget created successfully"}


@router.get("/{budget_id}")
async def get_budget(
    budget_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Get budget details"""
    tenant_id = current_user["tenant_id"]

    budget = db.query(Budget).filter(
        Budget.id == budget_id,
        Budget.tenant_id == tenant_id
    ).first()

    if not budget:
        raise HTTPException(status_code=404, detail="Budget not found")

    lines = db.query(BudgetLine).filter(BudgetLine.budget_id == budget_id).all()

    return {
        "id": budget.id,
        "name": budget.name,
        "period": budget.period,
        "start_date": budget.start_date.isoformat(),
        "end_date": budget.end_date.isoformat(),
        "total_budget": budget.total_budget,
        "is_active": budget.is_active,
        "lines": [{
            "id": l.id,
            "account_id": l.account_id,
            "amount": l.amount,
            "actual": l.actual_amount,
            "variance": l.amount - (l.actual_amount or 0),
            "notes": l.notes
        } for l in lines]
    }


@router.get("/{budget_id}/variance")
async def get_budget_variance(
    budget_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Get budget variance analysis"""
    tenant_id = current_user["tenant_id"]

    budget = db.query(Budget).filter(
        Budget.id == budget_id,
        Budget.tenant_id == tenant_id
    ).first()

    if not budget:
        raise HTTPException(status_code=404, detail="Budget not found")

    lines = db.query(BudgetLine).filter(BudgetLine.budget_id == budget_id).all()

    from ..models.account import Account, LedgerEntry

    variance_report = []

    for line in lines:
        account = db.query(Account).filter(Account.id == line.account_id).first()

        # Calculate actual from ledger
        entries = db.query(LedgerEntry).filter(
            LedgerEntry.account_id == line.account_id,
            LedgerEntry.tenant_id == tenant_id,
            LedgerEntry.transaction_date >= budget.start_date,
            LedgerEntry.transaction_date <= budget.end_date
        ).all()

        actual = sum(e.debit - e.credit for e in entries)

        # Update budget line
        line.actual_amount = actual
        variance = line.amount - actual
        variance_percent = (variance / line.amount * 100) if line.amount else 0

        variance_report.append({
            "account_id": line.account_id,
            "account_name": account.name if account else "Unknown",
            "budgeted": line.amount,
            "actual": actual,
            "variance": variance,
            "variance_percent": round(variance_percent, 2),
            "status": "over" if variance < 0 else "under" if variance > 0 else "on_track"
        })

    db.commit()

    total_budgeted = sum(v["budgeted"] for v in variance_report)
    total_actual = sum(v["actual"] for v in variance_report)

    return {
        "budget_name": budget.name,
        "period": f"{budget.start_date.date()} to {budget.end_date.date()}",
        "variance_report": variance_report,
        "totals": {
            "budgeted": total_budgeted,
            "actual": total_actual,
            "variance": total_budgeted - total_actual
        }
    }


@router.put("/{budget_id}")
async def update_budget(
    budget_id: int,
    name: Optional[str] = None,
    is_active: Optional[bool] = None,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Update budget"""
    tenant_id = current_user["tenant_id"]

    budget = db.query(Budget).filter(
        Budget.id == budget_id,
        Budget.tenant_id == tenant_id
    ).first()

    if not budget:
        raise HTTPException(status_code=404, detail="Budget not found")

    if name:
        budget.name = name
    if is_active is not None:
        budget.is_active = is_active

    db.commit()
    return {"message": "Budget updated successfully"}


@router.delete("/{budget_id}")
async def delete_budget(
    budget_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Delete budget"""
    tenant_id = current_user["tenant_id"]

    budget = db.query(Budget).filter(
        Budget.id == budget_id,
        Budget.tenant_id == tenant_id
    ).first()

    if not budget:
        raise HTTPException(status_code=404, detail="Budget not found")

    # Delete budget lines first
    db.query(BudgetLine).filter(BudgetLine.budget_id == budget_id).delete()

    db.delete(budget)
    db.commit()

    return {"message": "Budget deleted successfully"}
