"""
AI Service - Jarvis Integration using z-ai-web-dev-sdk
"""

from typing import List, Dict, Any, Optional
from sqlalchemy.orm import Session
import json
import logging
import os

# Import z-ai-web-dev-sdk
try:
    import ZAI from 'z-ai-web-dev-sdk'
    ZAI_AVAILABLE = True
except ImportError:
    ZAI_AVAILABLE = False
    logging.warning("z-ai-web-dev-sdk not installed. AI features will be disabled.")

from ..models.tenant import Tenant
from ..models.customer import Customer
from ..models.vendor import Vendor
from ..models.product import Product
from ..models.sales import SalesInvoice
from ..models.purchase import PurchaseBill
from ..security import decrypt_data

logger = logging.getLogger(__name__)


class AIService:
    """AI-powered business analyst service"""
    
    SYSTEM_PROMPT = """You are Jarvis, an expert financial and business analyst assistant for Booklet ERP.
Your purpose is to help business owners understand their financial data and make informed decisions.

Guidelines:
1. Answer questions based ONLY on the JSON data provided
2. Be concise and professional
3. Use simple Markdown for formatting (tables, bold, lists)
4. Perform calculations when asked (totals, averages, comparisons)
5. If you cannot answer from the provided data, say so clearly
6. Provide actionable insights when possible
7. Use Nigerian Naira (₦) for all currency amounts
8. Be helpful with business recommendations

When presenting data:
- Use tables for comparisons
- Highlight important metrics
- Suggest actions for improvement
"""

    def __init__(self):
        self.client = None
    
    async def initialize_client(self, api_key: str):
        """Initialize the AI client"""
        if not ZAI_AVAILABLE:
            raise RuntimeError("z-ai-web-dev-sdk is not installed")
        
        # Initialize ZAI client
        self.client = await ZAI.create(api_key=api_key)
    
    async def ask(
        self,
        db: Session,
        tenant: Tenant,
        question: str,
        context: Dict = None
    ) -> str:
        """
        Ask Jarvis a question about business data
        
        Args:
            db: Database session
            tenant: Tenant/business
            question: User's question
            context: Additional context (branch_id, date range, etc.)
        
        Returns:
            AI-generated response
        """
        # Get and decrypt API key
        if not tenant.encrypted_api_key:
            return "AI is not configured. Please set up your AI API key in Settings."
        
        try:
            api_key = decrypt_data(tenant.encrypted_api_key)
            await self.initialize_client(api_key)
        except Exception as e:
            logger.error(f"Failed to initialize AI client: {e}")
            return "Failed to initialize AI. Please check your API key configuration."
        
        # Gather business data for context
        business_data = await self._gather_business_data(db, tenant, context)
        
        # Build prompt
        full_prompt = f"""{self.SYSTEM_PROMPT}

BUSINESS DATA:
```json
{json.dumps(business_data, indent=2, default=str)}
```

USER QUESTION: {question}

Please analyze the data and provide a helpful response."""

        try:
            # Call AI
            response = await self.client.chat.completions.create(
                model="glm-4-flash",  # Using Zai's model
                messages=[
                    {"role": "system", "content": self.SYSTEM_PROMPT},
                    {"role": "user", "content": f"Here is my business data:\n```json\n{json.dumps(business_data, indent=2, default=str)}\n```\n\nMy question: {question}"}
                ],
                temperature=0.7,
                max_tokens=2048
            )
            
            return response.choices[0].message.content
            
        except Exception as e:
            logger.error(f"AI request failed: {e}")
            return f"Sorry, I encountered an error processing your request. Please try again."
    
    async def _gather_business_data(
        self,
        db: Session,
        tenant: Tenant,
        context: Dict = None
    ) -> Dict:
        """Gather relevant business data for AI context"""
        branch_id = context.get('branch_id') if context else None
        
        data = {
            'business': {
                'name': tenant.business_name,
                'currency': tenant.base_currency,
                'is_vat_registered': tenant.is_vat_registered,
                'vat_rate': tenant.vat_rate
            },
            'summary': {},
            'customers': [],
            'vendors': [],
            'products': [],
            'recent_sales': [],
            'recent_purchases': []
        }
        
        try:
            # Customers (top 20)
            customers = db.query(Customer).filter(
                Customer.tenant_id == tenant.id,
                Customer.is_active == True
            ).limit(20).all()
            
            data['customers'] = [{
                'name': c.name,
                'email': c.email,
                'phone': c.phone
            } for c in customers]
            
            # Vendors (top 20)
            vendors = db.query(Vendor).filter(
                Vendor.tenant_id == tenant.id,
                Vendor.is_active == True
            ).limit(20).all()
            
            data['vendors'] = [{
                'name': v.name,
                'email': v.email
            } for v in vendors]
            
            # Products (top 20)
            products = db.query(Product).filter(
                Product.tenant_id == tenant.id,
                Product.is_active == True
            ).limit(20).all()
            
            data['products'] = [{
                'name': p.name,
                'sku': p.sku,
                'stock_quantity': p.stock_quantity,
                'sales_price': p.sales_price
            } for p in products]
            
            # Recent sales (last 30 days)
            from datetime import datetime, timedelta
            thirty_days_ago = datetime.now() - timedelta(days=30)
            
            sales_query = db.query(SalesInvoice).filter(
                SalesInvoice.tenant_id == tenant.id,
                SalesInvoice.invoice_date >= thirty_days_ago
            )
            
            if branch_id:
                sales_query = sales_query.filter(SalesInvoice.branch_id == branch_id)
            
            recent_sales = sales_query.order_by(SalesInvoice.invoice_date.desc()).limit(20).all()
            
            data['recent_sales'] = [{
                'invoice_number': s.invoice_number,
                'date': s.invoice_date.isoformat(),
                'customer': s.customer.name,
                'total_amount': s.total_amount,
                'status': s.status
            } for s in recent_sales]
            
            # Recent purchases
            purchase_query = db.query(PurchaseBill).filter(
                PurchaseBill.tenant_id == tenant.id,
                PurchaseBill.bill_date >= thirty_days_ago
            )
            
            if branch_id:
                purchase_query = purchase_query.filter(PurchaseBill.branch_id == branch_id)
            
            recent_purchases = purchase_query.order_by(PurchaseBill.bill_date.desc()).limit(20).all()
            
            data['recent_purchases'] = [{
                'bill_number': p.bill_number,
                'date': p.bill_date.isoformat(),
                'vendor': p.vendor.name,
                'total_amount': p.total_amount,
                'status': p.status
            } for p in recent_purchases]
            
            # Summary statistics
            from sqlalchemy import func
            
            # Total sales this month
            month_start = datetime.now().replace(day=1, hour=0, minute=0, second=0, microsecond=0)
            
            total_sales = db.query(func.sum(SalesInvoice.total_amount)).filter(
                SalesInvoice.tenant_id == tenant.id,
                SalesInvoice.invoice_date >= month_start
            ).scalar() or 0
            
            total_receivables = db.query(
                func.sum(SalesInvoice.total_amount - SalesInvoice.paid_amount)
            ).filter(
                SalesInvoice.tenant_id == tenant.id,
                SalesInvoice.status.in_(['unpaid', 'partially_paid'])
            ).scalar() or 0
            
            total_payables = db.query(
                func.sum(PurchaseBill.total_amount - PurchaseBill.paid_amount)
            ).filter(
                PurchaseBill.tenant_id == tenant.id,
                PurchaseBill.status.in_(['unpaid', 'partially_paid'])
            ).scalar() or 0
            
            data['summary'] = {
                'total_sales_this_month': float(total_sales),
                'total_receivables': float(total_receivables),
                'total_payables': float(total_payables),
                'customer_count': len(customers),
                'vendor_count': len(vendors),
                'product_count': len(products)
            }
            
        except Exception as e:
            logger.error(f"Error gathering business data: {e}")
        
        return data
    
    async def suggest_chart_of_accounts(self, industry: str) -> List[Dict]:
        """Suggest chart of accounts based on industry"""
        prompt = f"""Suggest a chart of accounts for a {industry} business in Nigeria.
Return ONLY a JSON array of accounts with format:
[{{"code": "1000", "name": "Account Name", "type": "asset|liability|equity|revenue|expense"}}]

Use Nigerian business context. Include VAT (7.5%) related accounts.
"""
        
        try:
            response = await self.client.chat.completions.create(
                model="glm-4-flash",
                messages=[
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3,
                max_tokens=2048
            )
            
            # Parse JSON from response
            content = response.choices[0].message.content
            # Extract JSON array
            import re
            json_match = re.search(r'\[.*\]', content, re.DOTALL)
            if json_match:
                return json.loads(json_match.group())
            return []
            
        except Exception as e:
            logger.error(f"Failed to generate COA suggestions: {e}")
            return []


# Singleton instance
ai_service = AIService()
