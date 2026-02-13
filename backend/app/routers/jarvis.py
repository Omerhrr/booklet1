"""
Jarvis Router - AI Analyst for Business Intelligence
Natural language queries for business data
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional
import json

from ..database import get_db
from ..security import get_current_user

router = APIRouter(prefix="/jarvis", tags=["AI Analyst"])


class QueryRequest(BaseModel):
    query: str
    context: Optional[dict] = None


class ChatMessage(BaseModel):
    role: str  # user, assistant
    content: str
    timestamp: str


@router.post("/query")
async def process_query(
    request: QueryRequest,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """
    Process natural language query and return business insights
    
    Examples:
    - "What were my sales last month?"
    - "Who are my top 5 customers?"
    - "What's my cash position?"
    - "Show me expenses by category"
    - "Which products are low in stock?"
    """
    tenant_id = current_user["tenant_id"]
    query = request.query.lower()

    # Intent detection and response generation
    response = await analyze_query(query, tenant_id, db)

    return response


async def analyze_query(query: str, tenant_id: int, db: Session) -> dict:
    """Analyze query and return appropriate response"""

    # Sales queries
    if any(keyword in query for keyword in ['sales', 'revenue', 'income']):
        return await handle_sales_query(query, tenant_id, db)

    # Purchase queries
    elif any(keyword in query for keyword in ['purchase', 'buy', 'supplier', 'vendor']):
        return await handle_purchase_query(query, tenant_id, db)

    # Customer queries
    elif any(keyword in query for keyword in ['customer', 'client']):
        return await handle_customer_query(query, tenant_id, db)

    # Product/Inventory queries
    elif any(keyword in query for keyword in ['product', 'inventory', 'stock', 'item']):
        return await handle_inventory_query(query, tenant_id, db)

    # Cash/Banking queries
    elif any(keyword in query for keyword in ['cash', 'bank', 'money', 'balance']):
        return await handle_cash_query(query, tenant_id, db)

    # Expense queries
    elif any(keyword in query for keyword in ['expense', 'spending', 'cost']):
        return await handle_expense_query(query, tenant_id, db)

    # Employee/Payroll queries
    elif any(keyword in query for keyword in ['employee', 'staff', 'payroll', 'salary']):
        return handle_payroll_query(query, tenant_id, db)

    # Help
    elif any(keyword in query for keyword in ['help', 'what can', 'how to']):
        return {
            "type": "help",
            "message": "I can help you with:\n\n" +
                      "📊 **Sales & Revenue**\n" +
                      "- 'What were my sales last month?'\n" +
                      "- 'Who are my top customers?'\n\n" +
                      "💰 **Financial**\n" +
                      "- 'What's my cash position?'\n" +
                      "- 'Show expenses by category'\n\n" +
                      "📦 **Inventory**\n" +
                      "- 'Which products are low in stock?'\n" +
                      "- 'List all products'\n\n" +
                      "👥 **Customers & Vendors**\n" +
                      "- 'List customers with unpaid invoices'\n" +
                      "- 'Show vendor balances'",
            "data": None
        }

    # Default response
    else:
        return {
            "type": "unknown",
            "message": "I'm not sure how to help with that. Try asking about sales, expenses, customers, inventory, or cash position.",
            "data": None
        }


async def handle_sales_query(query: str, tenant_id: int, db: Session) -> dict:
    """Handle sales-related queries"""
    from ..models.sales import SalesInvoice, InvoicePaymentStatus
    from ..models.customer import Customer
    from datetime import datetime, timedelta

    # Total sales
    if 'total' in query or 'all' in query:
        total = db.query(SalesInvoice).filter(
            SalesInvoice.tenant_id == tenant_id
        ).with_entities(
            db.func.sum(SalesInvoice.total_amount)
        ).scalar() or 0

        return {
            "type": "metric",
            "message": f"Your total sales to date is **₦{total:,.2f}**",
            "data": {"total_sales": total}
        }

    # This month
    elif 'month' in query:
        start_of_month = datetime.now().replace(day=1, hour=0, minute=0, second=0, microsecond=0)

        invoices = db.query(SalesInvoice).filter(
            SalesInvoice.tenant_id == tenant_id,
            SalesInvoice.invoice_date >= start_of_month
        ).all()

        total = sum(inv.total_amount for inv in invoices)
        count = len(invoices)

        return {
            "type": "metric",
            "message": f"This month you've made **{count} sales** totaling **₦{total:,.2f}**",
            "data": {"month_sales": total, "invoice_count": count}
        }

    # Top customers
    elif 'top' in query or 'best' in query:
        invoices = db.query(SalesInvoice).filter(
            SalesInvoice.tenant_id == tenant_id
        ).all()

        customer_totals = {}
        for inv in invoices:
            customer_totals[inv.customer_id] = customer_totals.get(inv.customer_id, 0) + inv.total_amount

        customer_ids = list(customer_totals.keys())
        customers = {c.id: c for c in db.query(Customer).filter(Customer.id.in_(customer_ids)).all()}

        top_customers = sorted(
            [{"name": customers.get(cid, Customer(name="Unknown")).name, "total": total}
             for cid, total in customer_totals.items()],
            key=lambda x: x["total"],
            reverse=True
        )[:5]

        return {
            "type": "list",
            "message": "Here are your top 5 customers by revenue:",
            "data": {"top_customers": top_customers}
        }

    # Unpaid/Receivables
    elif 'unpaid' in query or 'receivable' in query or 'owing' in query:
        invoices = db.query(SalesInvoice).filter(
            SalesInvoice.tenant_id == tenant_id,
            SalesInvoice.status != InvoicePaymentStatus.PAID
        ).all()

        total_owing = sum(inv.total_amount - inv.paid_amount for inv in invoices)

        return {
            "type": "metric",
            "message": f"You have **{len(invoices)} unpaid invoices** totaling **₦{total_owing:,.2f}**",
            "data": {"unpaid_count": len(invoices), "total_owing": total_owing}
        }

    return {"type": "info", "message": "I can show you total sales, this month's sales, top customers, or unpaid invoices.", "data": None}


async def handle_purchase_query(query: str, tenant_id: int, db: Session) -> dict:
    """Handle purchase-related queries"""
    from ..models.purchase import PurchaseBill
    from ..models.vendor import Vendor
    from datetime import datetime

    if 'total' in query or 'all' in query:
        total = db.query(PurchaseBill).filter(
            PurchaseBill.tenant_id == tenant_id
        ).with_entities(
            db.func.sum(PurchaseBill.total_amount)
        ).scalar() or 0

        return {
            "type": "metric",
            "message": f"Your total purchases to date is **₦{total:,.2f}**",
            "data": {"total_purchases": total}
        }

    elif 'month' in query:
        start_of_month = datetime.now().replace(day=1, hour=0, minute=0, second=0, microsecond=0)

        bills = db.query(PurchaseBill).filter(
            PurchaseBill.tenant_id == tenant_id,
            PurchaseBill.bill_date >= start_of_month
        ).all()

        total = sum(bill.total_amount for bill in bills)

        return {
            "type": "metric",
            "message": f"This month you've made purchases totaling **₦{total:,.2f}**",
            "data": {"month_purchases": total}
        }

    elif 'vendor' in query or 'supplier' in query or 'payable' in query or 'owing' in query:
        bills = db.query(PurchaseBill).filter(
            PurchaseBill.tenant_id == tenant_id,
            PurchaseBill.is_paid == False
        ).all()

        total_owing = sum(bill.total_amount - bill.paid_amount for bill in bills)

        return {
            "type": "metric",
            "message": f"You owe vendors **₦{total_owing:,.2f}** across **{len(bills)} unpaid bills**",
            "data": {"unpaid_count": len(bills), "total_payables": total_owing}
        }

    return {"type": "info", "message": "I can show you total purchases, this month's purchases, or vendor payables.", "data": None}


async def handle_customer_query(query: str, tenant_id: int, db: Session) -> dict:
    """Handle customer-related queries"""
    from ..models.customer import Customer

    customers = db.query(Customer).filter(
        Customer.tenant_id == tenant_id,
        Customer.is_active == True
    ).all()

    if 'list' in query or 'all' in query or 'how many' in query:
        return {
            "type": "list",
            "message": f"You have **{len(customers)} active customers**",
            "data": {"customers": [{"name": c.name, "email": c.email, "phone": c.phone} for c in customers[:10]]}
        }

    return {"type": "info", "message": "I can list your customers or show customer-related statistics.", "data": None}


async def handle_inventory_query(query: str, tenant_id: int, db: Session) -> dict:
    """Handle inventory-related queries"""
    from ..models.product import Product

    if 'low' in query or 'reorder' in query:
        products = db.query(Product).filter(
            Product.tenant_id == tenant_id,
            Product.is_active == True,
            Product.track_inventory == True
        ).all()

        low_stock = [{
            "name": p.name,
            "sku": p.sku,
            "quantity": p.stock_quantity,
            "reorder_point": p.reorder_point
        } for p in products if p.reorder_point and p.stock_quantity <= p.reorder_point]

        return {
            "type": "alert",
            "message": f"You have **{len(low_stock)} products** below reorder point:",
            "data": {"low_stock_products": low_stock[:10]}
        }

    elif 'out' in query or 'zero' in query:
        products = db.query(Product).filter(
            Product.tenant_id == tenant_id,
            Product.is_active == True,
            Product.stock_quantity <= 0
        ).all()

        return {
            "type": "alert",
            "message": f"You have **{len(products)} products** out of stock",
            "data": {"out_of_stock": [{"name": p.name, "sku": p.sku} for p in products[:10]]}
        }

    else:
        products = db.query(Product).filter(
            Product.tenant_id == tenant_id,
            Product.is_active == True
        ).count()

        return {
            "type": "metric",
            "message": f"You have **{products} active products** in your inventory",
            "data": {"product_count": products}
        }


async def handle_cash_query(query: str, tenant_id: int, db: Session) -> dict:
    """Handle cash/banking queries"""
    from ..models.banking import BankAccount
    from ..models.sales import SalesInvoice, InvoicePaymentStatus
    from ..models.purchase import PurchaseBill

    accounts = db.query(BankAccount).filter(
        BankAccount.tenant_id == tenant_id,
        BankAccount.is_active == True
    ).all()

    total_cash = sum(a.current_balance for a in accounts)

    if 'position' in query or 'balance' in query:
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
            "type": "financial",
            "message": f"**Cash Position Summary**\n\n" +
                      f"💰 Bank Balance: **₦{total_cash:,.2f}**\n" +
                      f"📈 Receivables: **₦{receivables:,.2f}**\n" +
                      f"📉 Payables: **₦{payables:,.2f}**\n" +
                      f"✨ Net Position: **₦{(total_cash + receivables - payables):,.2f}**",
            "data": {
                "cash": total_cash,
                "receivables": receivables,
                "payables": payables,
                "net_position": total_cash + receivables - payables
            }
        }

    return {
        "type": "metric",
        "message": f"Your total bank balance is **₦{total_cash:,.2f}** across **{len(accounts)} account(s)**",
        "data": {"total_cash": total_cash, "accounts": len(accounts)}
    }


async def handle_expense_query(query: str, tenant_id: int, db: Session) -> dict:
    """Handle expense queries"""
    from ..models.expense import Expense
    from datetime import datetime

    if 'category' in query or 'breakdown' in query:
        expenses = db.query(Expense).filter(
            Expense.tenant_id == tenant_id
        ).all()

        by_category = {}
        for exp in expenses:
            by_category[exp.category] = by_category.get(exp.category, 0) + exp.amount

        sorted_categories = sorted(by_category.items(), key=lambda x: x[1], reverse=True)

        return {
            "type": "breakdown",
            "message": "**Expenses by Category:**",
            "data": {"categories": [{"name": k, "amount": v} for k, v in sorted_categories[:10]]}
        }

    elif 'month' in query:
        start_of_month = datetime.now().replace(day=1, hour=0, minute=0, second=0, microsecond=0)

        expenses = db.query(Expense).filter(
            Expense.tenant_id == tenant_id,
            Expense.date >= start_of_month
        ).all()

        total = sum(e.amount for e in expenses)

        return {
            "type": "metric",
            "message": f"This month you've spent **₦{total:,.2f}** on **{len(expenses)} expense(s)**",
            "data": {"month_expenses": total, "count": len(expenses)}
        }

    return {"type": "info", "message": "I can show expenses by category or this month's expenses.", "data": None}


def handle_payroll_query(query: str, tenant_id: int, db: Session) -> dict:
    """Handle payroll queries"""
    from ..models.hr import Employee, Payslip
    from datetime import datetime

    employees = db.query(Employee).filter(
        Employee.tenant_id == tenant_id,
        Employee.is_active == True
    ).count()

    if 'count' in query or 'how many' in query or 'staff' in query:
        return {
            "type": "metric",
            "message": f"You have **{employees} active employees**",
            "data": {"employee_count": employees}
        }

    current_month = datetime.now().month
    current_year = datetime.now().year

    payroll = db.query(Payslip).filter(
        Payslip.tenant_id == tenant_id,
        Payslip.pay_period_month == current_month,
        Payslip.pay_period_year == current_year
    ).all()

    total_payroll = sum(p.net_pay for p in payroll)

    return {
        "type": "metric",
        "message": f"This month's payroll is **₦{total_payroll:,.2f}** for **{len(payroll)} employee(s)**",
        "data": {"month_payroll": total_payroll, "employee_count": employees}
    }


@router.get("/suggestions")
async def get_query_suggestions():
    """Get suggested queries for the user"""
    return {
        "suggestions": [
            "What were my sales last month?",
            "What's my cash position?",
            "Which products are low in stock?",
            "Who are my top customers?",
            "Show expenses by category",
            "How much do I owe vendors?",
            "List unpaid invoices",
            "How many employees do I have?"
        ]
    }
