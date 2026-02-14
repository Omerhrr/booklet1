"""
Inventory Router - Products, Categories, Stock Management
"""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime
from pydantic import BaseModel

from ..database import get_db
from ..security import get_current_user
from ..models.product import Product, Category, StockAdjustment

router = APIRouter(prefix="/inventory", tags=["Inventory"])


# === Pydantic Schemas ===

class CategoryCreate(BaseModel):
    name: str
    description: Optional[str] = None
    parent_id: Optional[int] = None

class CategoryUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    is_active: Optional[bool] = None

class ProductCreate(BaseModel):
    name: str
    sku: Optional[str] = None
    barcode: Optional[str] = None
    category_id: Optional[int] = None
    description: Optional[str] = None
    unit: str = "pcs"
    purchase_price: float = 0
    sales_price: float = 0
    opening_stock: float = 0
    reorder_point: Optional[float] = None
    max_stock: Optional[float] = None
    track_inventory: bool = True
    is_inventory_item: bool = True
    branch_id: int

class ProductUpdate(BaseModel):
    name: Optional[str] = None
    sku: Optional[str] = None
    barcode: Optional[str] = None
    category_id: Optional[int] = None
    description: Optional[str] = None
    unit: Optional[str] = None
    purchase_price: Optional[float] = None
    sales_price: Optional[float] = None
    reorder_point: Optional[float] = None
    max_stock: Optional[float] = None
    track_inventory: Optional[bool] = None
    is_active: Optional[bool] = None

class StockAdjustmentCreate(BaseModel):
    product_id: int
    quantity_change: float
    reason: str
    adjustment_type: str = "manual"  # manual, purchase, sale, return, damage


# === Categories ===

@router.get("/categories")
async def list_categories(
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """List all categories"""
    tenant_id = current_user["tenant_id"]

    categories = db.query(Category).filter(
        Category.tenant_id == tenant_id,
        Category.is_active == True
    ).order_by(Category.name).all()

    return {
        "items": [{
            "id": c.id,
            "name": c.name,
            "description": c.description,
            "parent_id": c.parent_id,
            "product_count": len(c.products) if hasattr(c, 'products') else 0
        } for c in categories]
    }


@router.post("/categories")
async def create_category(
    category_data: CategoryCreate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Create new category"""
    tenant_id = current_user["tenant_id"]

    # Check for duplicate name
    existing = db.query(Category).filter(
        Category.tenant_id == tenant_id,
        Category.name == category_data.name
    ).first()

    if existing:
        raise HTTPException(status_code=400, detail="Category name already exists")

    category = Category(
        tenant_id=tenant_id,
        name=category_data.name,
        description=category_data.description,
        parent_id=category_data.parent_id
    )

    db.add(category)
    db.commit()
    db.refresh(category)

    return {"id": category.id, "message": "Category created successfully"}


@router.put("/categories/{category_id}")
async def update_category(
    category_id: int,
    category_data: CategoryUpdate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Update category"""
    tenant_id = current_user["tenant_id"]

    category = db.query(Category).filter(
        Category.id == category_id,
        Category.tenant_id == tenant_id
    ).first()

    if not category:
        raise HTTPException(status_code=404, detail="Category not found")

    for field, value in category_data.dict(exclude_unset=True).items():
        setattr(category, field, value)

    db.commit()
    return {"message": "Category updated successfully"}


@router.delete("/categories/{category_id}")
async def delete_category(
    category_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Delete category"""
    tenant_id = current_user["tenant_id"]

    category = db.query(Category).filter(
        Category.id == category_id,
        Category.tenant_id == tenant_id
    ).first()

    if not category:
        raise HTTPException(status_code=404, detail="Category not found")

    # Check for products in category
    products = db.query(Product).filter(Product.category_id == category_id).count()
    if products > 0:
        category.is_active = False
        db.commit()
        return {"message": "Category deactivated (has products)"}

    db.delete(category)
    db.commit()
    return {"message": "Category deleted successfully"}


# === Products ===

@router.get("/products")
async def list_products(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, le=200),
    category_id: Optional[int] = None,
    is_active: Optional[bool] = None,
    low_stock: Optional[bool] = None,
    search: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """List products"""
    tenant_id = current_user["tenant_id"]

    query = db.query(Product).filter(Product.tenant_id == tenant_id)

    if category_id:
        query = query.filter(Product.category_id == category_id)
    if is_active is not None:
        query = query.filter(Product.is_active == is_active)
    if search:
        query = query.filter(
            (Product.name.ilike(f"%{search}%")) |
            (Product.sku.ilike(f"%{search}%")) |
            (Product.barcode.ilike(f"%{search}%"))
        )

    products = query.order_by(Product.name).offset(skip).limit(limit).all()

    # Filter low stock after query
    if low_stock:
        products = [p for p in products if p.reorder_point and p.stock_quantity <= p.reorder_point]

    return {
        "items": [{
            "id": p.id,
            "name": p.name,
            "sku": p.sku,
            "barcode": p.barcode,
            "category_id": p.category_id,
            "unit": p.unit,
            "purchase_price": p.purchase_price,
            "sales_price": p.sales_price,
            "stock_quantity": p.stock_quantity,
            "reorder_point": p.reorder_point,
            "is_low_stock": p.reorder_point and p.stock_quantity <= p.reorder_point if p.reorder_point else False,
            "is_active": p.is_active
        } for p in products],
        "total": query.count()
    }


@router.post("/products")
async def create_product(
    product_data: ProductCreate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Create new product"""
    tenant_id = current_user["tenant_id"]

    # Check for duplicate SKU
    if product_data.sku:
        existing = db.query(Product).filter(
            Product.tenant_id == tenant_id,
            Product.sku == product_data.sku
        ).first()
        if existing:
            raise HTTPException(status_code=400, detail="Product SKU already exists")

    product = Product(
        tenant_id=tenant_id,
        branch_id=product_data.branch_id,
        name=product_data.name,
        sku=product_data.sku,
        barcode=product_data.barcode,
        category_id=product_data.category_id,
        description=product_data.description,
        unit=product_data.unit,
        purchase_price=product_data.purchase_price,
        sales_price=product_data.sales_price,
        opening_stock=product_data.opening_stock,
        stock_quantity=product_data.opening_stock,
        reorder_point=product_data.reorder_point,
        max_stock=product_data.max_stock,
        track_inventory=product_data.track_inventory,
        is_inventory_item=product_data.is_inventory_item
    )

    db.add(product)
    db.commit()
    db.refresh(product)

    # Create opening stock adjustment if applicable
    if product_data.opening_stock > 0:
        adjustment = StockAdjustment(
            tenant_id=tenant_id,
            product_id=product.id,
            quantity_change=product_data.opening_stock,
            previous_quantity=0,
            new_quantity=product_data.opening_stock,
            reason="Opening stock",
            user_id=current_user["user_id"]
        )
        db.add(adjustment)
        db.commit()

    return {"id": product.id, "message": "Product created successfully"}


@router.get("/products/{product_id}")
async def get_product(
    product_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Get product details"""
    tenant_id = current_user["tenant_id"]

    product = db.query(Product).filter(
        Product.id == product_id,
        Product.tenant_id == tenant_id
    ).first()

    if not product:
        raise HTTPException(status_code=404, detail="Product not found")

    category = None
    if product.category_id:
        category = db.query(Category).filter(Category.id == product.category_id).first()

    # Get recent adjustments
    adjustments = db.query(StockAdjustment).filter(
        StockAdjustment.product_id == product_id
    ).order_by(StockAdjustment.created_at.desc()).limit(10).all()

    return {
        "id": product.id,
        "name": product.name,
        "sku": product.sku,
        "barcode": product.barcode,
        "category": {
            "id": category.id,
            "name": category.name
        } if category else None,
        "description": product.description,
        "unit": product.unit,
        "purchase_price": product.purchase_price,
        "sales_price": product.sales_price,
        "opening_stock": product.opening_stock,
        "stock_quantity": product.stock_quantity,
        "reorder_point": product.reorder_point,
        "max_stock": product.max_stock,
        "track_inventory": product.track_inventory,
        "is_inventory_item": product.is_inventory_item,
        "is_active": product.is_active,
        "is_low_stock": product.reorder_point and product.stock_quantity <= product.reorder_point if product.reorder_point else False,
        "recent_adjustments": [{
            "id": a.id,
            "quantity_change": a.quantity_change,
            "previous_quantity": a.previous_quantity,
            "new_quantity": a.new_quantity,
            "reason": a.reason,
            "created_at": a.created_at.isoformat()
        } for a in adjustments]
    }


@router.put("/products/{product_id}")
async def update_product(
    product_id: int,
    product_data: ProductUpdate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Update product"""
    tenant_id = current_user["tenant_id"]

    product = db.query(Product).filter(
        Product.id == product_id,
        Product.tenant_id == tenant_id
    ).first()

    if not product:
        raise HTTPException(status_code=404, detail="Product not found")

    for field, value in product_data.dict(exclude_unset=True).items():
        setattr(product, field, value)

    db.commit()
    return {"message": "Product updated successfully"}


@router.delete("/products/{product_id}")
async def delete_product(
    product_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Delete product (soft delete)"""
    tenant_id = current_user["tenant_id"]

    product = db.query(Product).filter(
        Product.id == product_id,
        Product.tenant_id == tenant_id
    ).first()

    if not product:
        raise HTTPException(status_code=404, detail="Product not found")

    product.is_active = False
    db.commit()

    return {"message": "Product deactivated successfully"}


# === Stock Adjustments ===

@router.post("/stock-adjustments")
async def create_stock_adjustment(
    adjustment_data: StockAdjustmentCreate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Create stock adjustment"""
    tenant_id = current_user["tenant_id"]

    product = db.query(Product).filter(
        Product.id == adjustment_data.product_id,
        Product.tenant_id == tenant_id
    ).first()

    if not product:
        raise HTTPException(status_code=404, detail="Product not found")

    if not product.track_inventory:
        raise HTTPException(status_code=400, detail="Inventory tracking disabled for this product")

    previous_quantity = product.stock_quantity
    new_quantity = previous_quantity + adjustment_data.quantity_change

    if new_quantity < 0:
        raise HTTPException(status_code=400, detail="Insufficient stock")

    # Update product stock
    product.stock_quantity = new_quantity

    # Create adjustment record
    adjustment = StockAdjustment(
        tenant_id=tenant_id,
        product_id=adjustment_data.product_id,
        quantity_change=adjustment_data.quantity_change,
        previous_quantity=previous_quantity,
        new_quantity=new_quantity,
        reason=adjustment_data.reason,
        user_id=current_user["user_id"]
    )

    db.add(adjustment)
    db.commit()

    return {
        "id": adjustment.id,
        "previous_quantity": previous_quantity,
        "new_quantity": new_quantity,
        "message": "Stock adjusted successfully"
    }


@router.get("/stock-adjustments")
async def list_stock_adjustments(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, le=200),
    product_id: Optional[int] = None,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """List stock adjustments"""
    tenant_id = current_user["tenant_id"]

    query = db.query(StockAdjustment).filter(
        StockAdjustment.tenant_id == tenant_id
    )

    if product_id:
        query = query.filter(StockAdjustment.product_id == product_id)

    adjustments = query.order_by(StockAdjustment.created_at.desc()).offset(skip).limit(limit).all()

    # Get product names
    product_ids = list(set(a.product_id for a in adjustments))
    products = {p.id: p for p in db.query(Product).filter(Product.id.in_(product_ids)).all()}

    return {
        "items": [{
            "id": a.id,
            "product_id": a.product_id,
            "product_name": products.get(a.product_id, Product(name="Unknown")).name,
            "quantity_change": a.quantity_change,
            "previous_quantity": a.previous_quantity,
            "new_quantity": a.new_quantity,
            "reason": a.reason,
            "created_at": a.created_at.isoformat()
        } for a in adjustments],
        "total": query.count()
    }


# === Dashboard Stats ===

@router.get("/dashboard")
async def get_inventory_dashboard(
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Get inventory dashboard statistics"""
    tenant_id = current_user["tenant_id"]

    # Total products
    total_products = db.query(Product).filter(
        Product.tenant_id == tenant_id,
        Product.is_active == True
    ).count()

    # Low stock items
    products = db.query(Product).filter(
        Product.tenant_id == tenant_id,
        Product.is_active == True,
        Product.track_inventory == True
    ).all()

    low_stock_count = sum(
        1 for p in products
        if p.reorder_point and p.stock_quantity <= p.reorder_point
    )

    # Total inventory value
    total_value = sum(
        p.stock_quantity * p.purchase_price
        for p in products
        if p.stock_quantity and p.purchase_price
    )

    # Out of stock
    out_of_stock = sum(1 for p in products if p.stock_quantity <= 0)

    return {
        "total_products": total_products,
        "low_stock_count": low_stock_count,
        "out_of_stock_count": out_of_stock,
        "total_inventory_value": total_value
    }
