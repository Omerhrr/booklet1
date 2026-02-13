"""
Analytics Router - Dashboard Analytics and KPIs
"""
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from typing import Optional

from ..database import get_db
from ..security import get_current_user
from ..models.sales import SalesInvoice, InvoicePaymentStatus
from ..models.purchase import PurchaseBill
from ..models.customer import Customer
from ..models.vendor import Vendor
from ..models.product import Product
from ..models.hr import Employee, Payslip
from ..models.account import Account, AccountType, LedgerEntry

router = APIRouter(prefix="/analytics", tags=["Analytics"])


@router.get("/dashboard")
async def get_dashboard_analytics(
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Get main dashboard analytics"""
    tenant_id = current_user["tenant_id"]

    if not start_date:
        start_date = datetime.now().replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    if not end_date:
        end_date = datetime.now()

    # Sales metrics
    sales_invoices = db.query(SalesInvoice).filter(
        SalesInvoice.tenant_id == tenant_id,
        SalesInvoice.invoice_date >= start_date,
        SalesInvoice.invoice_date <= end_date
    ).all()

    total_sales = sum(inv.total_amount for inv in sales_invoices)
    sales_count = len(sales_invoices)

    # Purchase metrics
    purchase_bills = db.query(PurchaseBill).filter(
        PurchaseBill.tenant_id == tenant_id,
        PurchaseBill.bill_date >= start_date,
        PurchaseBill.bill_date <= end_date
    ).all()

    total_purchases = sum(bill.total_amount for bill in purchase_bills)
    purchase_count = len(purchase_bills)

    # Receivables
    outstanding_receivables = db.query(SalesInvoice).filter(
        SalesInvoice.tenant_id == tenant_id,
        SalesInvoice.status != InvoicePaymentStatus.PAID
    ).all()

    total_receivables = sum(inv.total_amount - inv.paid_amount for inv in outstanding_receivables)

    # Payables
    outstanding_payables = db.query(PurchaseBill).filter(
        PurchaseBill.tenant_id == tenant_id,
        PurchaseBill.is_paid == False
    ).all()

    total_payables = sum(bill.total_amount - bill.paid_amount for bill in outstanding_payables)

    # Counts
    customer_count = db.query(Customer).filter(
        Customer.tenant_id == tenant_id,
        Customer.is_active == True
    ).count()

    vendor_count = db.query(Vendor).filter(
        Vendor.tenant_id == tenant_id,
        Vendor.is_active == True
    ).count()

    product_count = db.query(Product).filter(
        Product.tenant_id == tenant_id,
        Product.is_active == True
    ).count()

    employee_count = db.query(Employee).filter(
        Employee.tenant_id == tenant_id,
        Employee.is_active == True
    ).count()

    return {
        "period": {
            "start": start_date.isoformat(),
            "end": end_date.isoformat()
        },
        "sales": {
            "total": total_sales,
            "count": sales_count,
            "average": total_sales / sales_count if sales_count else 0
        },
        "purchases": {
            "total": total_purchases,
            "count": purchase_count,
            "average": total_purchases / purchase_count if purchase_count else 0
        },
        "receivables": total_receivables,
        "payables": total_payables,
        "gross_profit": total_sales - total_purchases,
        "counts": {
            "customers": customer_count,
            "vendors": vendor_count,
            "products": product_count,
            "employees": employee_count
        }
    }


@router.get("/sales-trend")
async def get_sales_trend(
    months: int = Query(6, ge=1, le=12),
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Get monthly sales trend"""
    tenant_id = current_user["tenant_id"]

    end_date = datetime.now()
    start_date = end_date - timedelta(days=months * 30)

    invoices = db.query(SalesInvoice).filter(
        SalesInvoice.tenant_id == tenant_id,
        SalesInvoice.invoice_date >= start_date,
        SalesInvoice.invoice_date <= end_date
    ).all()

    # Group by month
    monthly_data = {}
    for inv in invoices:
        month_key = inv.invoice_date.strftime("%Y-%m")
        if month_key not in monthly_data:
            monthly_data[month_key] = {"total": 0, "count": 0}
        monthly_data[month_key]["total"] += inv.total_amount
        monthly_data[month_key]["count"] += 1

    # Fill missing months
    result = []
    current = start_date
    while current <= end_date:
        month_key = current.strftime("%Y-%m")
        result.append({
            "month": month_key,
            "label": current.strftime("%b %Y"),
            "total": monthly_data.get(month_key, {}).get("total", 0),
            "count": monthly_data.get(month_key, {}).get("count", 0)
        })
        current = (current.replace(day=1) + timedelta(days=32)).replace(day=1)

    return {"trend": result}


@router.get("/expenses-by-category")
async def get_expenses_by_category(
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Get expenses breakdown by category"""
    tenant_id = current_user["tenant_id"]

    if not start_date:
        start_date = datetime.now().replace(day=1)
    if not end_date:
        end_date = datetime.now()

    from ..models.expense import Expense

    expenses = db.query(Expense).filter(
        Expense.tenant_id == tenant_id,
        Expense.date >= start_date,
        Expense.date <= end_date
    ).all()

    by_category = {}
    for exp in expenses:
        if exp.category not in by_category:
            by_category[exp.category] = 0
        by_category[exp.category] += exp.amount

    return {
        "period": f"{start_date.date()} to {end_date.date()}",
        "categories": [{"name": k, "amount": v} for k, v in sorted(by_category.items(), key=lambda x: x[1], reverse=True)],
        "total": sum(by_category.values())
    }


@router.get("/top-customers")
async def get_top_customers(
    limit: int = Query(10, ge=5, le=50),
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Get top customers by revenue"""
    tenant_id = current_user["tenant_id"]

    invoices = db.query(SalesInvoice).filter(
        SalesInvoice.tenant_id == tenant_id
    ).all()

    customer_totals = {}
    for inv in invoices:
        if inv.customer_id not in customer_totals:
            customer_totals[inv.customer_id] = {"total": 0, "count": 0}
        customer_totals[inv.customer_id]["total"] += inv.total_amount
        customer_totals[inv.customer_id]["count"] += 1

    # Get customer names
    customer_ids = list(customer_totals.keys())
    customers = {c.id: c for c in db.query(Customer).filter(Customer.id.in_(customer_ids)).all()}

    result = [{
        "customer_id": cid,
        "name": customers.get(cid, Customer(name="Unknown")).name,
        "total": data["total"],
        "invoice_count": data["count"]
    } for cid, data in customer_totals.items()]

    result.sort(key=lambda x: x["total"], reverse=True)

    return {"top_customers": result[:limit]}


@router.get("/inventory-alerts")
async def get_inventory_alerts(
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Get inventory alerts (low stock, out of stock)"""
    tenant_id = current_user["tenant_id"]

    products = db.query(Product).filter(
        Product.tenant_id == tenant_id,
        Product.is_active == True,
        Product.track_inventory == True
    ).all()

    low_stock = []
    out_of_stock = []

    for p in products:
        if p.stock_quantity <= 0:
            out_of_stock.append({
                "id": p.id,
                "name": p.name,
                "sku": p.sku,
                "stock_quantity": p.stock_quantity
            })
        elif p.reorder_point and p.stock_quantity <= p.reorder_point:
            low_stock.append({
                "id": p.id,
                "name": p.name,
                "sku": p.sku,
                "stock_quantity": p.stock_quantity,
                "reorder_point": p.reorder_point
            })

    return {
        "low_stock": low_stock,
        "out_of_stock": out_of_stock,
        "alerts_count": len(low_stock) + len(out_of_stock)
    }


@router.get("/cash-position")
async def get_cash_position(
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Get current cash position"""
    tenant_id = current_user["tenant_id"]

    # Get cash/bank accounts
    from ..models.banking import BankAccount

    bank_accounts = db.query(BankAccount).filter(
        BankAccount.tenant_id == tenant_id,
        BankAccount.is_active == True
    ).all()

    total_cash = sum(a.current_balance for a in bank_accounts)

    # Get receivables and payables
    receivables = sum(
        inv.total_amount - inv.paid_amount
        for inv in db.query(SalesInvoice).filter(
            SalesInvoice.tenant_id == tenant_id,
            SalesInvoice.status != InvoicePaymentStatus.PAID
        ).all()
    )

    payables = sum(
        bill.total_amount - bill.paid_amount
        for bill in db.query(PurchaseBill).filter(
            PurchaseBill.tenant_id == tenant_id,
            PurchaseBill.is_paid == False
        ).all()
    )

    return {
        "cash_balance": total_cash,
        "accounts": [{
            "bank_name": a.bank_name,
            "account_number": a.account_number,
            "balance": a.current_balance
        } for a in bank_accounts],
        "receivables": receivables,
        "payables": payables,
        "net_position": total_cash + receivables - payables
    }
