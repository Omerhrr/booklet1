"""
Expense CRUD Operations
"""

from typing import Optional, List
from sqlalchemy.orm import Session
from datetime import datetime

from ..models.expense import Expense, OtherIncome


class CRUDExpense:
    
    def get(self, db: Session, expense_id: int) -> Optional[Expense]:
        return db.query(Expense).filter(Expense.id == expense_id).first()
    
    def get_multi(
        self,
        db: Session,
        tenant_id: int,
        skip: int = 0,
        limit: int = 100,
        category: str = None,
        start_date: datetime = None,
        end_date: datetime = None
    ) -> List[Expense]:
        query = db.query(Expense).filter(Expense.tenant_id == tenant_id)
        if category:
            query = query.filter(Expense.category == category)
        if start_date:
            query = query.filter(Expense.date >= start_date)
        if end_date:
            query = query.filter(Expense.date <= end_date)
        return query.offset(skip).limit(limit).all()
    
    def create(
        self,
        db: Session,
        tenant_id: int,
        branch_id: int,
        user_id: int,
        date: datetime,
        category: str,
        description: str,
        amount: float,
        payment_method: str = "cash",
        account_id: int = None,
        reference: str = None
    ) -> Expense:
        expense = Expense(
            tenant_id=tenant_id,
            branch_id=branch_id,
            user_id=user_id,
            date=date,
            category=category,
            description=description,
            amount=amount,
            payment_method=payment_method,
            account_id=account_id,
            reference=reference
        )
        db.add(expense)
        db.commit()
        db.refresh(expense)
        return expense
    
    def delete(self, db: Session, expense_id: int) -> bool:
        expense = self.get(db, expense_id)
        if expense:
            db.delete(expense)
            db.commit()
            return True
        return False
    
    def get_by_category(
        self,
        db: Session,
        tenant_id: int,
        start_date: datetime = None,
        end_date: datetime = None
    ) -> dict:
        from sqlalchemy import func
        query = db.query(
            Expense.category,
            func.sum(Expense.amount).label('total'),
            func.count(Expense.id).label('count')
        ).filter(Expense.tenant_id == tenant_id)
        
        if start_date:
            query = query.filter(Expense.date >= start_date)
        if end_date:
            query = query.filter(Expense.date <= end_date)
        
        results = query.group_by(Expense.category).all()
        return {r.category: {'total': r.total, 'count': r.count} for r in results}


expense = CRUDExpense()


class CRUDOtherIncome:
    
    def get(self, db: Session, income_id: int) -> Optional[OtherIncome]:
        return db.query(OtherIncome).filter(OtherIncome.id == income_id).first()
    
    def get_multi(
        self,
        db: Session,
        tenant_id: int,
        skip: int = 0,
        limit: int = 100
    ) -> List[OtherIncome]:
        return db.query(OtherIncome).filter(
            OtherIncome.tenant_id == tenant_id
        ).offset(skip).limit(limit).all()
    
    def create(
        self,
        db: Session,
        tenant_id: int,
        branch_id: int,
        date: datetime,
        category: str,
        description: str,
        amount: float,
        account_id: int = None,
        reference: str = None
    ) -> OtherIncome:
        income = OtherIncome(
            tenant_id=tenant_id,
            branch_id=branch_id,
            date=date,
            category=category,
            description=description,
            amount=amount,
            account_id=account_id,
            reference=reference
        )
        db.add(income)
        db.commit()
        db.refresh(income)
        return income


other_income = CRUDOtherIncome()
