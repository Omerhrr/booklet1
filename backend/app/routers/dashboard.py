"""
Dashboard Router - KPIs and Summary Data
"""

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import Optional
from datetime import datetime, timedelta

from ..database import get_db
from ..routers.auth import get_current_active_user

router = APIRouter()


@router.get("")
async def get_dashboard(
    session: dict = Depends(get_current_active_user),
    db: Session = Depends(get_db),
    branch_id: Optional[int] = None,
    period: str = "this_month"
):
    """Get dashboard KPIs and summary data"""
    user = session["user"]
    tenant = session["tenant"]
    
    # Determine date range
    now = datetime.utcnow()
    if period == "this_month":
        start_date = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        end_date = now
    elif period == "last_month":
        start_date = (now.replace(day=1) - timedelta(days=1)).replace(day=1)
        end_date = now.replace(day=1) - timedelta(days=1)
    elif period == "this_year":
        start_date = now.replace(month=1, day=1, hour=0, minute=0, second=0, microsecond=0)
        end_date = now
    else:
        start_date = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        end_date = now
    
    # Get selected branch
    selected_branch = branch_id or session.get("selected_branch", {}).get("id")
    
    # TODO: Calculate actual KPIs from database
    # For now, return placeholder data
    
    return {
        "period": period,
        "start_date": start_date.isoformat(),
        "end_date": end_date.isoformat(),
        "branch_id": selected_branch,
        "kpis": {
            "total_sales": 0.0,
            "total_purchases": 0.0,
            "total_expenses": 0.0,
            "net_profit": 0.0,
            "receivables": 0.0,
            "payables": 0.0,
            "bank_balance": 0.0,
            "cash_balance": 0.0,
        },
        "recent_transactions": [],
        "sales_chart": [],
        "top_customers": [],
        "top_products": [],
        "aging_summary": {
            "receivables": {"current": 0, "1_30": 0, "31_60": 0, "61_90": 0, "over_90": 0},
            "payables": {"current": 0, "1_30": 0, "31_60": 0, "61_90": 0, "over_90": 0}
        }
    }
