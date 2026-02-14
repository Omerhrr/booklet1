"""
Reports Router - Financial Reports
Profit & Loss, Balance Sheet, Trial Balance, Aging Reports
"""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import Optional
from datetime import datetime, timedelta
from collections import defaultdict

from ..database import get_db
from ..security import get_current_user
from ..models.account import Account, AccountType, LedgerEntry
from ..models.sales import SalesInvoice, SalesInvoiceItem, InvoicePaymentStatus
from ..models.purchase import PurchaseBill, PurchaseBillItem
from ..models.customer import Customer
from ..models.vendor import Vendor

router = APIRouter(prefix="/reports", tags=["Reports"])


@router.get("/profit-loss")
async def get_profit_loss(
    start_date: datetime = Query(...),
    end_date: datetime = Query(...),
    compare_previous: bool = Query(False),
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """
    Generate Profit & Loss Statement
    
    Nigerian GAAP compliant report showing:
    - Revenue (sales, other income)
    - Cost of Sales
    - Gross Profit
    - Operating Expenses
    - Net Profit
    """
    tenant_id = current_user["tenant_id"]

    # Get revenue accounts
    revenue_accounts = db.query(Account).filter(
        Account.tenant_id == tenant_id,
        Account.type == AccountType.REVENUE,
        Account.is_active == True
    ).all()

    # Get expense accounts
    expense_accounts = db.query(Account).filter(
        Account.tenant_id == tenant_id,
        Account.type == AccountType.EXPENSE,
        Account.is_active == True
    ).all()

    # Calculate revenue
    revenue = []
    total_revenue = 0

    for account in revenue_accounts:
        entries = db.query(LedgerEntry).filter(
            LedgerEntry.account_id == account.id,
            LedgerEntry.tenant_id == tenant_id,
            LedgerEntry.transaction_date >= start_date,
            LedgerEntry.transaction_date <= end_date
        ).all()

        # Revenue increases with credits
        balance = sum(e.credit - e.debit for e in entries)

        if abs(balance) > 0.01:
            revenue.append({
                "code": account.code,
                "name": account.name,
                "amount": balance
            })
            total_revenue += balance

    # Calculate expenses
    expenses = []
    total_expenses = 0

    for account in expense_accounts:
        entries = db.query(LedgerEntry).filter(
            LedgerEntry.account_id == account.id,
            LedgerEntry.tenant_id == tenant_id,
            LedgerEntry.transaction_date >= start_date,
            LedgerEntry.transaction_date <= end_date
        ).all()

        # Expenses increase with debits
        balance = sum(e.debit - e.credit for e in entries)

        if abs(balance) > 0.01:
            expenses.append({
                "code": account.code,
                "name": account.name,
                "amount": balance
            })
            total_expenses += balance

    gross_profit = total_revenue - total_expenses

    # Previous period comparison
    previous_period = None
    if compare_previous:
        period_length = (end_date - start_date).days
        prev_start = start_date - timedelta(days=period_length + 1)
        prev_end = start_date - timedelta(days=1)

        # Calculate previous period revenue
        prev_revenue = 0
        for account in revenue_accounts:
            entries = db.query(LedgerEntry).filter(
                LedgerEntry.account_id == account.id,
                LedgerEntry.tenant_id == tenant_id,
                LedgerEntry.transaction_date >= prev_start,
                LedgerEntry.transaction_date <= prev_end
            ).all()
            prev_revenue += sum(e.credit - e.debit for e in entries)

        # Calculate previous period expenses
        prev_expenses = 0
        for account in expense_accounts:
            entries = db.query(LedgerEntry).filter(
                LedgerEntry.account_id == account.id,
                LedgerEntry.tenant_id == tenant_id,
                LedgerEntry.transaction_date >= prev_start,
                LedgerEntry.transaction_date <= prev_end
            ).all()
            prev_expenses += sum(e.debit - e.credit for e in entries)

        previous_period = {
            "start_date": prev_start.isoformat(),
            "end_date": prev_end.isoformat(),
            "revenue": prev_revenue,
            "expenses": prev_expenses,
            "net_profit": prev_revenue - prev_expenses
        }

    return {
        "report_title": "Profit & Loss Statement",
        "period": {
            "start_date": start_date.isoformat(),
            "end_date": end_date.isoformat()
        },
        "currency": "NGN",
        "revenue": revenue,
        "total_revenue": round(total_revenue, 2),
        "expenses": expenses,
        "total_expenses": round(total_expenses, 2),
        "gross_profit": round(gross_profit, 2),
        "net_profit": round(gross_profit, 2),  # Simplified - no tax calculation
        "previous_period": previous_period
    }


@router.get("/balance-sheet")
async def get_balance_sheet(
    as_of_date: datetime = Query(...),
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """
    Generate Balance Sheet
    
    Shows:
    - Assets (Current & Non-current)
    - Liabilities (Current & Non-current)
    - Equity
    """
    tenant_id = current_user["tenant_id"]

    # Get all accounts
    accounts = db.query(Account).filter(
        Account.tenant_id == tenant_id,
        Account.is_active == True
    ).all()

    assets = {"current": [], "non_current": [], "total": 0}
    liabilities = {"current": [], "non_current": [], "total": 0}
    equity = {"items": [], "total": 0}

    for account in accounts:
        # Calculate balance from ledger entries
        entries = db.query(LedgerEntry).filter(
            LedgerEntry.account_id == account.id,
            LedgerEntry.tenant_id == tenant_id,
            LedgerEntry.transaction_date <= as_of_date
        ).all()

        if account.type == AccountType.ASSET:
            balance = account.opening_balance + sum(e.debit - e.credit for e in entries)
            if abs(balance) > 0.01:
                item = {"code": account.code, "name": account.name, "amount": balance}
                # Simplified classification - could be enhanced with account codes
                if account.code and account.code.startswith("1"):
                    assets["current"].append(item)
                else:
                    assets["non_current"].append(item)
                assets["total"] += balance

        elif account.type == AccountType.LIABILITY:
            balance = account.opening_balance + sum(e.credit - e.debit for e in entries)
            if abs(balance) > 0.01:
                item = {"code": account.code, "name": account.name, "amount": balance}
                if account.code and account.code.startswith("2"):
                    liabilities["current"].append(item)
                else:
                    liabilities["non_current"].append(item)
                liabilities["total"] += balance

        elif account.type == AccountType.EQUITY:
            balance = account.opening_balance + sum(e.credit - e.debit for e in entries)
            if abs(balance) > 0.01:
                equity["items"].append({
                    "code": account.code,
                    "name": account.name,
                    "amount": balance
                })
                equity["total"] += balance

    # Calculate retained earnings from P&L
    retained_earnings = assets["total"] - liabilities["total"] - equity["total"]
    if abs(retained_earnings) > 0.01:
        equity["items"].append({
            "code": "RE",
            "name": "Retained Earnings",
            "amount": retained_earnings
        })
        equity["total"] += retained_earnings

    return {
        "report_title": "Balance Sheet",
        "as_of_date": as_of_date.isoformat(),
        "currency": "NGN",
        "assets": assets,
        "liabilities": liabilities,
        "equity": equity,
        "total_assets": round(assets["total"], 2),
        "total_liabilities_and_equity": round(liabilities["total"] + equity["total"], 2),
        "is_balanced": abs(assets["total"] - (liabilities["total"] + equity["total"])) < 0.01
    }


@router.get("/trial-balance")
async def get_trial_balance_report(
    as_of_date: Optional[datetime] = None,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Generate Trial Balance"""
    tenant_id = current_user["tenant_id"]

    if not as_of_date:
        as_of_date = datetime.now()

    accounts = db.query(Account).filter(
        Account.tenant_id == tenant_id,
        Account.is_active == True
    ).order_by(Account.code).all()

    trial_balance = []

    for account in accounts:
        entries = db.query(LedgerEntry).filter(
            LedgerEntry.account_id == account.id,
            LedgerEntry.tenant_id == tenant_id,
            LedgerEntry.transaction_date <= as_of_date
        ).all()

        total_debit = sum(e.debit for e in entries)
        total_credit = sum(e.credit for e in entries)

        # Account for opening balance and type
        if account.type in [AccountType.ASSET, AccountType.EXPENSE]:
            debit_balance = account.opening_balance + total_debit - total_credit
            credit_balance = 0
            if debit_balance < 0:
                credit_balance = abs(debit_balance)
                debit_balance = 0
        else:
            credit_balance = account.opening_balance + total_credit - total_debit
            debit_balance = 0
            if credit_balance < 0:
                debit_balance = abs(credit_balance)
                credit_balance = 0

        if abs(debit_balance) > 0.01 or abs(credit_balance) > 0.01:
            trial_balance.append({
                "code": account.code,
                "name": account.name,
                "type": account.type.value,
                "debit": round(debit_balance, 2),
                "credit": round(credit_balance, 2)
            })

    total_debits = sum(t["debit"] for t in trial_balance)
    total_credits = sum(t["credit"] for t in trial_balance)

    return {
        "report_title": "Trial Balance",
        "as_of_date": as_of_date.isoformat(),
        "currency": "NGN",
        "accounts": trial_balance,
        "total_debits": round(total_debits, 2),
        "total_credits": round(total_credits, 2),
        "is_balanced": abs(total_debits - total_credits) < 0.01
    }


@router.get("/receivables-aging")
async def get_receivables_aging(
    as_of_date: Optional[datetime] = None,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """
    Accounts Receivable Aging Report
    
    Buckets: Current, 1-30, 31-60, 61-90, 90+ days
    """
    tenant_id = current_user["tenant_id"]

    if not as_of_date:
        as_of_date = datetime.now()

    # Get unpaid invoices
    invoices = db.query(SalesInvoice).filter(
        SalesInvoice.tenant_id == tenant_id,
        SalesInvoice.status != InvoicePaymentStatus.PAID
    ).all()

    customer_ids = list(set(i.customer_id for i in invoices))
    customers = {c.id: c for c in db.query(Customer).filter(Customer.id.in_(customer_ids)).all()}

    aging = {
        "current": [],
        "1-30": [],
        "31-60": [],
        "61-90": [],
        "90+": []
    }

    summary = {
        "current": 0,
        "1-30": 0,
        "31-60": 0,
        "61-90": 0,
        "90+": 0
    }

    for invoice in invoices:
        balance = invoice.total_amount - invoice.paid_amount
        if balance <= 0:
            continue

        days_overdue = (as_of_date - invoice.due_date).days if invoice.due_date else 0

        customer = customers.get(invoice.customer_id)
        customer_name = customer.name if customer else "Unknown"

        item = {
            "invoice_id": invoice.id,
            "invoice_number": invoice.invoice_number,
            "customer_name": customer_name,
            "amount": balance,
            "due_date": invoice.due_date.isoformat() if invoice.due_date else None,
            "days_overdue": max(0, days_overdue)
        }

        if days_overdue <= 0:
            aging["current"].append(item)
            summary["current"] += balance
        elif days_overdue <= 30:
            aging["1-30"].append(item)
            summary["1-30"] += balance
        elif days_overdue <= 60:
            aging["31-60"].append(item)
            summary["31-60"] += balance
        elif days_overdue <= 90:
            aging["61-90"].append(item)
            summary["61-90"] += balance
        else:
            aging["90+"].append(item)
            summary["90+"] += balance

    return {
        "report_title": "Accounts Receivable Aging",
        "as_of_date": as_of_date.isoformat(),
        "currency": "NGN",
        "aging": aging,
        "summary": {k: round(v, 2) for k, v in summary.items()},
        "total": round(sum(summary.values()), 2)
    }


@router.get("/payables-aging")
async def get_payables_aging(
    as_of_date: Optional[datetime] = None,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """
    Accounts Payable Aging Report
    
    Buckets: Current, 1-30, 31-60, 61-90, 90+ days
    """
    tenant_id = current_user["tenant_id"]

    if not as_of_date:
        as_of_date = datetime.now()

    # Get unpaid bills
    bills = db.query(PurchaseBill).filter(
        PurchaseBill.tenant_id == tenant_id,
        PurchaseBill.is_paid == False
    ).all()

    vendor_ids = list(set(b.vendor_id for b in bills))
    vendors = {v.id: v for v in db.query(Vendor).filter(Vendor.id.in_(vendor_ids)).all()}

    aging = {
        "current": [],
        "1-30": [],
        "31-60": [],
        "61-90": [],
        "90+": []
    }

    summary = {
        "current": 0,
        "1-30": 0,
        "31-60": 0,
        "61-90": 0,
        "90+": 0
    }

    for bill in bills:
        balance = bill.total_amount - bill.paid_amount
        if balance <= 0:
            continue

        days_overdue = (as_of_date - bill.due_date).days if bill.due_date else 0

        vendor = vendors.get(bill.vendor_id)
        vendor_name = vendor.name if vendor else "Unknown"

        item = {
            "bill_id": bill.id,
            "bill_number": bill.bill_number,
            "vendor_name": vendor_name,
            "amount": balance,
            "due_date": bill.due_date.isoformat() if bill.due_date else None,
            "days_overdue": max(0, days_overdue)
        }

        if days_overdue <= 0:
            aging["current"].append(item)
            summary["current"] += balance
        elif days_overdue <= 30:
            aging["1-30"].append(item)
            summary["1-30"] += balance
        elif days_overdue <= 60:
            aging["31-60"].append(item)
            summary["31-60"] += balance
        elif days_overdue <= 90:
            aging["61-90"].append(item)
            summary["61-90"] += balance
        else:
            aging["90+"].append(item)
            summary["90+"] += balance

    return {
        "report_title": "Accounts Payable Aging",
        "as_of_date": as_of_date.isoformat(),
        "currency": "NGN",
        "aging": aging,
        "summary": {k: round(v, 2) for k, v in summary.items()},
        "total": round(sum(summary.values()), 2)
    }


@router.get("/sales-summary")
async def get_sales_summary(
    start_date: datetime = Query(...),
    end_date: datetime = Query(...),
    group_by: str = Query("day", pattern="^(day|week|month|customer|product)$"),
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Sales summary report with grouping options"""
    tenant_id = current_user["tenant_id"]

    invoices = db.query(SalesInvoice).filter(
        SalesInvoice.tenant_id == tenant_id,
        SalesInvoice.invoice_date >= start_date,
        SalesInvoice.invoice_date <= end_date,
        SalesInvoice.is_posted == True
    ).all()

    if group_by == "day":
        grouped = defaultdict(lambda: {"count": 0, "total": 0})
        for inv in invoices:
            key = inv.invoice_date.strftime("%Y-%m-%d")
            grouped[key]["count"] += 1
            grouped[key]["total"] += inv.total_amount

        result = [{"date": k, "invoice_count": v["count"], "total": v["total"]}
                  for k, v in sorted(grouped.items())]

    elif group_by == "month":
        grouped = defaultdict(lambda: {"count": 0, "total": 0})
        for inv in invoices:
            key = inv.invoice_date.strftime("%Y-%m")
            grouped[key]["count"] += 1
            grouped[key]["total"] += inv.total_amount

        result = [{"month": k, "invoice_count": v["count"], "total": v["total"]}
                  for k, v in sorted(grouped.items())]

    elif group_by == "customer":
        grouped = defaultdict(lambda: {"count": 0, "total": 0, "name": ""})
        customer_ids = list(set(i.customer_id for i in invoices))
        customers = {c.id: c for c in db.query(Customer).filter(Customer.id.in_(customer_ids)).all()}

        for inv in invoices:
            grouped[inv.customer_id]["count"] += 1
            grouped[inv.customer_id]["total"] += inv.total_amount
            grouped[inv.customer_id]["name"] = customers.get(inv.customer_id, Customer(name="Unknown")).name

        result = [{"customer_id": k, "customer_name": v["name"],
                   "invoice_count": v["count"], "total": v["total"]}
                  for k, v in sorted(grouped.items(), key=lambda x: x[1]["total"], reverse=True)]

    else:  # product
        # Get all invoice items
        invoice_ids = [i.id for i in invoices]
        items = db.query(SalesInvoiceItem).filter(
            SalesInvoiceItem.sales_invoice_id.in_(invoice_ids)
        ).all()

        grouped = defaultdict(lambda: {"quantity": 0, "total": 0, "name": ""})
        product_ids = list(set(i.product_id for i in items if i.product_id))

        from ..models.product import Product
        products = {p.id: p for p in db.query(Product).filter(Product.id.in_(product_ids)).all()}

        for item in items:
            if item.product_id:
                grouped[item.product_id]["quantity"] += item.quantity
                grouped[item.product_id]["total"] += item.line_total
                grouped[item.product_id]["name"] = products.get(item.product_id, Product(name="Unknown")).name

        result = [{"product_id": k, "product_name": v["name"],
                   "quantity": v["quantity"], "total": v["total"]}
                  for k, v in sorted(grouped.items(), key=lambda x: x[1]["total"], reverse=True)]

    return {
        "report_title": "Sales Summary",
        "period": {
            "start_date": start_date.isoformat(),
            "end_date": end_date.isoformat()
        },
        "group_by": group_by,
        "currency": "NGN",
        "data": result,
        "grand_total": sum(inv.total_amount for inv in invoices)
    }


@router.get("/cash-flow")
async def get_cash_flow(
    start_date: datetime = Query(...),
    end_date: datetime = Query(...),
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Cash flow statement (simplified)"""
    tenant_id = current_user["tenant_id"]

    # Get cash/bank accounts
    from ..models.account import Account
    cash_accounts = db.query(Account).filter(
        Account.tenant_id == tenant_id,
        Account.type == AccountType.ASSET,
        Account.is_active == True
    ).all()

    # Calculate cash movements
    opening_balance = 0
    closing_balance = 0
    receipts = []
    payments = []

    for account in cash_accounts:
        # Opening balance
        opening_entries = db.query(LedgerEntry).filter(
            LedgerEntry.account_id == account.id,
            LedgerEntry.tenant_id == tenant_id,
            LedgerEntry.transaction_date < start_date
        ).all()
        opening_balance += account.opening_balance + sum(e.debit - e.credit for e in opening_entries)

        # Period transactions
        period_entries = db.query(LedgerEntry).filter(
            LedgerEntry.account_id == account.id,
            LedgerEntry.tenant_id == tenant_id,
            LedgerEntry.transaction_date >= start_date,
            LedgerEntry.transaction_date <= end_date
        ).all()

        for entry in period_entries:
            if entry.debit > 0:
                receipts.append({
                    "date": entry.transaction_date.isoformat(),
                    "description": entry.description,
                    "amount": entry.debit
                })
            elif entry.credit > 0:
                payments.append({
                    "date": entry.transaction_date.isoformat(),
                    "description": entry.description,
                    "amount": entry.credit
                })

        # Closing balance
        closing_balance += opening_balance + sum(e.debit - e.credit for e in period_entries)

    total_receipts = sum(r["amount"] for r in receipts)
    total_payments = sum(p["amount"] for p in payments)

    return {
        "report_title": "Cash Flow Statement",
        "period": {
            "start_date": start_date.isoformat(),
            "end_date": end_date.isoformat()
        },
        "currency": "NGN",
        "opening_balance": round(opening_balance, 2),
        "receipts": receipts[:50],  # Limit for response size
        "total_receipts": round(total_receipts, 2),
        "payments": payments[:50],
        "total_payments": round(total_payments, 2),
        "net_cash_flow": round(total_receipts - total_payments, 2),
        "closing_balance": round(closing_balance, 2)
    }
