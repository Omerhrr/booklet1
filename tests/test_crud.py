"""
Tests for CRUD Operations
"""

import pytest
from datetime import date

from ..app.crud import customer, vendor, product, sales, account
from ..app.models.account import AccountType


class TestCustomerCRUD:
    """Tests for customer CRUD operations"""
    
    def test_create_customer(self, db, tenant, branch):
        """Test creating a customer"""
        cust = customer.create(
            db,
            tenant_id=tenant.id,
            branch_id=branch.id,
            name="Test Customer",
            email="test@customer.com",
            phone="08012345678"
        )
        
        assert cust.id is not None
        assert cust.name == "Test Customer"
        assert cust.customer_number is not None
    
    def test_get_customers(self, db, tenant, branch):
        """Test getting customers list"""
        # Create multiple customers
        for i in range(5):
            customer.create(
                db,
                tenant_id=tenant.id,
                branch_id=branch.id,
                name=f"Customer {i}"
            )
        
        customers = customer.get_multi(db, tenant_id=tenant.id)
        assert len(customers) >= 5
    
    def test_search_customers(self, db, tenant, branch):
        """Test searching customers"""
        customer.create(
            db, tenant_id=tenant.id, branch_id=branch.id,
            name="Acme Corporation"
        )
        customer.create(
            db, tenant_id=tenant.id, branch_id=branch.id,
            name="Beta Industries"
        )
        
        results = customer.get_multi(
            db, tenant_id=tenant.id, search="Acme"
        )
        
        assert len(results) == 1
        assert results[0].name == "Acme Corporation"
    
    def test_update_customer(self, db, tenant, branch):
        """Test updating customer"""
        cust = customer.create(
            db, tenant_id=tenant.id, branch_id=branch.id,
            name="Original Name"
        )
        
        updated = customer.update(
            db, customer=cust, name="Updated Name"
        )
        
        assert updated.name == "Updated Name"


class TestVendorCRUD:
    """Tests for vendor CRUD operations"""
    
    def test_create_vendor(self, db, tenant, branch):
        """Test creating a vendor"""
        vend = vendor.create(
            db,
            tenant_id=tenant.id,
            branch_id=branch.id,
            name="Test Vendor Ltd",
            email="vendor@test.com"
        )
        
        assert vend.id is not None
        assert vend.vendor_number is not None


class TestProductCRUD:
    """Tests for product CRUD operations"""
    
    def test_create_product(self, db, tenant, branch):
        """Test creating a product"""
        prod = product.create(
            db,
            tenant_id=tenant.id,
            branch_id=branch.id,
            name="Test Product",
            sku="TEST-001",
            sales_price=1000.00,
            purchase_price=500.00
        )
        
        assert prod.id is not None
        assert prod.sku == "TEST-001"
    
    def test_create_category(self, db, tenant):
        """Test creating a category"""
        cat = product.category.create(
            db,
            tenant_id=tenant.id,
            name="Electronics"
        )
        
        assert cat.id is not None
        assert cat.name == "Electronics"
    
    def test_adjust_stock(self, db, tenant, branch, user):
        """Test stock adjustment"""
        prod = product.create(
            db,
            tenant_id=tenant.id,
            branch_id=branch.id,
            name="Stock Item",
            opening_stock=100
        )
        
        assert prod.stock_quantity == 100
        
        # Increase stock
        adj = product.adjust_stock(
            db,
            product_id=prod.id,
            quantity_change=50,
            reason="Purchase",
            user_id=user.id
        )
        
        assert adj.new_quantity == 150
        assert adj.quantity_change == 50
    
    def test_get_low_stock_products(self, db, tenant, branch):
        """Test getting low stock products"""
        # Create product with low stock
        product.create(
            db,
            tenant_id=tenant.id,
            branch_id=branch.id,
            name="Low Stock Item",
            opening_stock=5,
            reorder_point=10
        )
        
        low_stock = product.get_low_stock_products(db, tenant.id)
        
        assert len(low_stock) >= 1


class TestAccountCRUD:
    """Tests for account CRUD operations"""
    
    def test_create_account(self, db, tenant, branch):
        """Test creating an account"""
        acc = account.create(
            db,
            tenant_id=tenant.id,
            branch_id=branch.id,
            code="1500",
            name="Office Equipment",
            account_type=AccountType.ASSET
        )
        
        assert acc.id is not None
        assert acc.code == "1500"
    
    def test_get_accounts_by_type(self, db, tenant, branch):
        """Test getting accounts by type"""
        account.create(
            db, tenant_id=tenant.id, branch_id=branch.id,
            code="2000", name="Accounts Payable",
            account_type=AccountType.LIABILITY
        )
        account.create(
            db, tenant_id=tenant.id, branch_id=branch.id,
            code="2100", name="VAT Payable",
            account_type=AccountType.LIABILITY
        )
        
        liabilities = account.get_by_type(db, tenant.id, AccountType.LIABILITY)
        
        assert len(liabilities) >= 2


class TestSalesInvoiceCRUD:
    """Tests for sales invoice CRUD operations"""
    
    def test_create_invoice(self, db, tenant, branch):
        """Test creating a sales invoice"""
        from ..app.models.customer import Customer
    
    def test_create_sales_invoice(self, db, tenant, branch):
        """Test creating a sales invoice"""
        # Create customer first
        from ..app.crud import customer
        
        cust = customer.create(
            db, tenant_id=tenant.id, branch_id=branch.id,
            name="Invoice Customer"
        )
        
        invoice = sales.sales_invoice.create(
            db,
            tenant_id=tenant.id,
            branch_id=branch.id,
            customer_id=cust.id,
            invoice_date=date.today(),
            items=[
                {'description': 'Item 1', 'quantity': 2, 'unit_price': 500},
                {'description': 'Item 2', 'quantity': 1, 'unit_price': 1000}
            ]
        )
        
        assert invoice.id is not None
        assert invoice.subtotal == 2000
        assert invoice.invoice_number is not None
