"""
Expenses Router - Expense Tracking and Other Income
"""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import Optional, List
from datetime import datetime
from pydantic import BaseModel

from ..database import get_db
from ..security import get_current_user
from ..models.expense import Expense, OtherIncome

router = APIRouter(prefix="/expenses", tags=["Expenses"])


class ExpenseCreate(BaseModel):
    date: datetime
    category: str
    description: str
    amount: float
    payment_method: str = "cash"  # cash, bank_transfer, cheque
    account_id: Optional[int] = None
    reference: Optional[str] = None
    branch_id: int

class OtherIncomeCreate(BaseModel):
    date: datetime
    category: str
    description: str
    amount: float
    account_id: Optional[int] = None
    reference: Optional[str] = None
    branch_id: int


# Expense categories
EXPENSE_CATEGORIES = [
    "Office Supplies",
    "Utilities",
    "Rent",
    "Salaries & Wages",
    "Transportation",
    "Marketing & Advertising",
    "Professional Fees",
    "Insurance",
    "Repairs & Maintenance",
    "Communication",
    "Travel & Entertainment",
    "Bank Charges",
    "Taxes & Levies",
    "Depreciation",
    "Other"
]

INCOME_CATEGORIES = [
    "Interest Income",
    "Rental Income",
    "Dividend Income",
    "Gain on Sale of Assets",
    "Commission Income",
    "Other"
]


@router.get("")
async def list_expenses(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, le=200),
    category: Optional[str] = None,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """List expenses"""
    tenant_id = current_user["tenant_id"]

    query = db.query(Expense).filter(Expense.tenant_id == tenant_id)

    if category:
        query = query.filter(Expense.category == category)
    if start_date:
        query = query.filter(Expense.date >= start_date)
    if end_date:
        query = query.filter(Expense.date <= end_date)

    expenses = query.order_by(Expense.date.desc()).offset(skip).limit(limit).all()

    return {
        "items": [{
            "id": e.id,
            "date": e.date.isoformat(),
            "category": e.category,
            "description": e.description,
            "amount": e.amount,
            "payment_method": e.payment_method,
            "reference": e.reference
        } for e in expenses],
        "total": query.count(),
        "categories": EXPENSE_CATEGORIES
    }


@router.post("")
async def create_expense(
    expense_data: ExpenseCreate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Create expense"""
    tenant_id = current_user["tenant_id"]

    expense = Expense(
        tenant_id=tenant_id,
        branch_id=expense_data.branch_id,
        date=expense_data.date,
        category=expense_data.category,
        description=expense_data.description,
        amount=expense_data.amount,
        payment_method=expense_data.payment_method,
        account_id=expense_data.account_id,
        reference=expense_data.reference,
        user_id=current_user["user_id"]
    )

    db.add(expense)
    db.commit()
    db.refresh(expense)

    return {"id": expense.id, "message": "Expense recorded successfully"}


@router.get("/summary")
async def get_expense_summary(
    start_date: datetime = Query(...),
    end_date: datetime = Query(...),
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Get expense summary by category"""
    tenant_id = current_user["tenant_id"]

    expenses = db.query(Expense).filter(
        Expense.tenant_id == tenant_id,
        Expense.date >= start_date,
        Expense.date <= end_date
    ).all()

    by_category = {}
    for exp in expenses:
        if exp.category not in by_category:
            by_category[exp.category] = {"count": 0, "total": 0}
        by_category[exp.category]["count"] += 1
        by_category[exp.category]["total"] += exp.amount

    return {
        "period": {
            "start_date": start_date.isoformat(),
            "end_date": end_date.isoformat()
        },
        "by_category": by_category,
        "total": sum(e.amount for e in expenses),
        "count": len(expenses)
    }


@router.delete("/{expense_id}")
async def delete_expense(
    expense_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Delete expense"""
    tenant_id = current_user["tenant_id"]

    expense = db.query(Expense).filter(
        Expense.id == expense_id,
        Expense.tenant_id == tenant_id
    ).first()

    if not expense:
        raise HTTPException(status_code=404, detail="Expense not found")

    db.delete(expense)
    db.commit()
    return {"message": "Expense deleted successfully"}


# === Other Income ===

@router.get("/other-income")
async def list_other_income(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, le=200),
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """List other income"""
    tenant_id = current_user["tenant_id"]

    income = db.query(OtherIncome).filter(
        OtherIncome.tenant_id == tenant_id
    ).order_by(OtherIncome.date.desc()).offset(skip).limit(limit).all()

    return {
        "items": [{
            "id": i.id,
            "date": i.date.isoformat(),
            "category": i.category,
            "description": i.description,
            "amount": i.amount,
            "reference": i.reference
        } for i in income],
        "total": db.query(OtherIncome).filter(OtherIncome.tenant_id == tenant_id).count(),
        "categories": INCOME_CATEGORIES
    }


@router.post("/other-income")
async def create_other_income(
    income_data: OtherIncomeCreate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Create other income"""
    tenant_id = current_user["tenant_id"]

    income = OtherIncome(
        tenant_id=tenant_id,
        branch_id=income_data.branch_id,
        date=income_data.date,
        category=income_data.category,
        description=income_data.description,
        amount=income_data.amount,
        account_id=income_data.account_id,
        reference=income_data.reference
    )

    db.add(income)
    db.commit()
    db.refresh(income)

    return {"id": income.id, "message": "Other income recorded successfully"}
