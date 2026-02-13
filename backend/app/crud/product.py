"""
Product and Inventory CRUD Operations
"""

from typing import Optional, List
from sqlalchemy.orm import Session
from sqlalchemy import or_, func
from datetime import datetime

from ..models.product import Product, Category, StockAdjustment


class CRUDProduct:
    
    def get(self, db: Session, product_id: int) -> Optional[Product]:
        """Get product by ID"""
        return db.query(Product).filter(Product.id == product_id).first()
    
    def get_by_sku(self, db: Session, tenant_id: int, sku: str) -> Optional[Product]:
        """Get product by SKU"""
        return db.query(Product).filter(
            Product.tenant_id == tenant_id,
            Product.sku == sku
        ).first()
    
    def get_multi(
        self,
        db: Session,
        tenant_id: int,
        branch_id: int = None,
        category_id: int = None,
        skip: int = 0,
        limit: int = 50,
        search: str = None,
        is_active: bool = None,
        low_stock: bool = False
    ) -> List[Product]:
        """Get multiple products with filters"""
        query = db.query(Product).filter(Product.tenant_id == tenant_id)
        
        if branch_id:
            query = query.filter(Product.branch_id == branch_id)
        
        if category_id:
            query = query.filter(Product.category_id == category_id)
        
        if search:
            search_term = f"%{search}%"
            query = query.filter(
                or_(
                    Product.name.ilike(search_term),
                    Product.sku.ilike(search_term),
                    Product.barcode.ilike(search_term)
                )
            )
        
        if is_active is not None:
            query = query.filter(Product.is_active == is_active)
        
        if low_stock:
            # Products below reorder point
            query = query.filter(
                Product.stock_quantity <= Product.reorder_point
            )
        
        return query.order_by(Product.name).offset(skip).limit(limit).all()
    
    def count(
        self,
        db: Session,
        tenant_id: int,
        branch_id: int = None,
        search: str = None,
        is_active: bool = None
    ) -> int:
        """Count products"""
        query = db.query(func.count(Product.id)).filter(Product.tenant_id == tenant_id)
        
        if branch_id:
            query = query.filter(Product.branch_id == branch_id)
        
        if search:
            search_term = f"%{search}%"
            query = query.filter(Product.name.ilike(search_term))
        
        if is_active is not None:
            query = query.filter(Product.is_active == is_active)
        
        return query.scalar() or 0
    
    def create(
        self,
        db: Session,
        *,
        tenant_id: int,
        branch_id: int,
        name: str,
        sku: str = None,
        barcode: str = None,
        category_id: int = None,
        description: str = None,
        unit: str = "pcs",
        purchase_price: float = 0,
        sales_price: float = 0,
        opening_stock: float = 0,
        reorder_point: float = None,
        max_stock: float = None,
        track_inventory: bool = True,
        user_id: int = None
    ) -> Product:
        """Create new product"""
        product = Product(
            tenant_id=tenant_id,
            branch_id=branch_id,
            name=name,
            sku=sku,
            barcode=barcode,
            category_id=category_id,
            description=description,
            unit=unit,
            purchase_price=purchase_price,
            sales_price=sales_price,
            opening_stock=opening_stock,
            stock_quantity=opening_stock,
            reorder_point=reorder_point,
            max_stock=max_stock,
            track_inventory=track_inventory
        )
        db.add(product)
        db.flush()
        
        # Create initial stock adjustment if opening stock > 0
        if opening_stock > 0 and user_id:
            adjustment = StockAdjustment(
                tenant_id=tenant_id,
                product_id=product.id,
                quantity_change=opening_stock,
                previous_quantity=0,
                new_quantity=opening_stock,
                reason="Opening stock",
                user_id=user_id
            )
            db.add(adjustment)
        
        db.commit()
        db.refresh(product)
        return product
    
    def update(
        self,
        db: Session,
        *,
        product: Product,
        **kwargs
    ) -> Product:
        """Update product"""
        for key, value in kwargs.items():
            if hasattr(product, key) and value is not None:
                setattr(product, key, value)
        db.commit()
        db.refresh(product)
        return product
    
    def delete(self, db: Session, product_id: int) -> bool:
        """Soft delete product"""
        product = self.get(db, product_id)
        if product:
            product.is_active = False
            db.commit()
            return True
        return False
    
    def adjust_stock(
        self,
        db: Session,
        *,
        product_id: int,
        quantity_change: float,
        reason: str,
        user_id: int
    ) -> StockAdjustment:
        """Adjust product stock"""
        product = self.get(db, product_id)
        if not product:
            raise ValueError("Product not found")
        
        previous_quantity = product.stock_quantity
        new_quantity = previous_quantity + quantity_change
        
        if new_quantity < 0:
            raise ValueError("Insufficient stock")
        
        # Update product stock
        product.stock_quantity = new_quantity
        
        # Create adjustment record
        adjustment = StockAdjustment(
            tenant_id=product.tenant_id,
            product_id=product_id,
            quantity_change=quantity_change,
            previous_quantity=previous_quantity,
            new_quantity=new_quantity,
            reason=reason,
            user_id=user_id
        )
        db.add(adjustment)
        db.commit()
        db.refresh(adjustment)
        
        return adjustment
    
    def get_low_stock_products(
        self,
        db: Session,
        tenant_id: int,
        branch_id: int = None
    ) -> List[Product]:
        """Get products below reorder point"""
        query = db.query(Product).filter(
            Product.tenant_id == tenant_id,
            Product.is_active == True,
            Product.track_inventory == True,
            Product.stock_quantity <= Product.reorder_point
        )
        
        if branch_id:
            query = query.filter(Product.branch_id == branch_id)
        
        return query.all()


class CRUDCategory:
    
    def get(self, db: Session, category_id: int) -> Optional[Category]:
        return db.query(Category).filter(Category.id == category_id).first()
    
    def get_multi(
        self,
        db: Session,
        tenant_id: int,
        skip: int = 0,
        limit: int = 50
    ) -> List[Category]:
        return db.query(Category).filter(
            Category.tenant_id == tenant_id,
            Category.is_active == True
        ).order_by(Category.name).offset(skip).limit(limit).all()
    
    def create(
        self,
        db: Session,
        *,
        tenant_id: int,
        name: str,
        description: str = None,
        parent_id: int = None
    ) -> Category:
        category = Category(
            tenant_id=tenant_id,
            name=name,
            description=description,
            parent_id=parent_id
        )
        db.add(category)
        db.commit()
        db.refresh(category)
        return category
    
    def update(self, db: Session, category: Category, **kwargs) -> Category:
        for key, value in kwargs.items():
            if hasattr(category, key) and value is not None:
                setattr(category, key, value)
        db.commit()
        db.refresh(category)
        return category
    
    def delete(self, db: Session, category_id: int) -> bool:
        category = self.get(db, category_id)
        if category:
            category.is_active = False
            db.commit()
            return True
        return False


product = CRUDProduct()
category = CRUDCategory()
