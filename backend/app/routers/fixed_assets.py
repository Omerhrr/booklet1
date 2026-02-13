"""
Fixed Assets Router - Asset Management and Depreciation
"""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import Optional, List
from datetime import datetime, date
from pydantic import BaseModel
from enum import Enum

from ..database import get_db
from ..security import get_current_user
from ..models.fixed_assets import FixedAsset, DepreciationEntry

router = APIRouter(prefix="/fixed-assets", tags=["Fixed Assets"])


class AssetStatus(str, Enum):
    ACTIVE = "active"
    DISPOSED = "disposed"
    FULLY_DEPRECIATED = "fully_depreciated"

class DepreciationMethod(str, Enum):
    STRAIGHT_LINE = "straight_line"
    DECLINING_BALANCE = "declining_balance"


class FixedAssetCreate(BaseModel):
    name: str
    asset_code: Optional[str] = None
    category: str
    purchase_date: date
    purchase_price: float
    salvage_value: float = 0
    useful_life_years: int
    depreciation_method: DepreciationMethod = DepreciationMethod.STRAIGHT_LINE
    location: Optional[str] = None
    branch_id: int

class FixedAssetUpdate(BaseModel):
    name: Optional[str] = None
    location: Optional[str] = None
    status: Optional[AssetStatus] = None


ASSET_CATEGORIES = [
    "Land",
    "Buildings",
    "Machinery & Equipment",
    "Motor Vehicles",
    "Furniture & Fixtures",
    "Computer Equipment",
    "Office Equipment",
    "Leasehold Improvements"
]


@router.get("")
async def list_assets(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, le=200),
    category: Optional[str] = None,
    status: Optional[AssetStatus] = None,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """List fixed assets"""
    tenant_id = current_user["tenant_id"]

    query = db.query(FixedAsset).filter(FixedAsset.tenant_id == tenant_id)

    if category:
        query = query.filter(FixedAsset.category == category)
    if status:
        query = query.filter(FixedAsset.status == status)

    assets = query.order_by(FixedAsset.name).offset(skip).limit(limit).all()

    return {
        "items": [{
            "id": a.id,
            "name": a.name,
            "asset_code": a.asset_code,
            "category": a.category,
            "purchase_date": a.purchase_date.isoformat(),
            "purchase_price": a.purchase_price,
            "accumulated_depreciation": a.accumulated_depreciation,
            "book_value": a.purchase_price - a.accumulated_depreciation,
            "status": a.status
        } for a in assets],
        "total": query.count(),
        "categories": ASSET_CATEGORIES
    }


@router.post("")
async def create_asset(
    asset_data: FixedAssetCreate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Create fixed asset"""
    tenant_id = current_user["tenant_id"]

    # Generate asset code if not provided
    if not asset_data.asset_code:
        last_asset = db.query(FixedAsset).filter(
            FixedAsset.tenant_id == tenant_id
        ).order_by(FixedAsset.id.desc()).first()

        code_num = (last_asset.id + 1) if last_asset else 1
        asset_data.asset_code = f"FA-{code_num:04d}"

    asset = FixedAsset(
        tenant_id=tenant_id,
        branch_id=asset_data.branch_id,
        name=asset_data.name,
        asset_code=asset_data.asset_code,
        category=asset_data.category,
        purchase_date=asset_data.purchase_date,
        purchase_price=asset_data.purchase_price,
        salvage_value=asset_data.salvage_value,
        useful_life_years=asset_data.useful_life_years,
        depreciation_method=asset_data.depreciation_method.value,
        location=asset_data.location,
        status="active"
    )

    db.add(asset)
    db.commit()
    db.refresh(asset)

    return {"id": asset.id, "asset_code": asset.asset_code, "message": "Asset created successfully"}


@router.get("/{asset_id}")
async def get_asset(
    asset_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Get asset details"""
    tenant_id = current_user["tenant_id"]

    asset = db.query(FixedAsset).filter(
        FixedAsset.id == asset_id,
        FixedAsset.tenant_id == tenant_id
    ).first()

    if not asset:
        raise HTTPException(status_code=404, detail="Asset not found")

    # Get depreciation history
    depreciation = db.query(DepreciationEntry).filter(
        DepreciationEntry.asset_id == asset_id
    ).order_by(DepreciationEntry.depreciation_date).all()

    return {
        "id": asset.id,
        "name": asset.name,
        "asset_code": asset.asset_code,
        "category": asset.category,
        "purchase_date": asset.purchase_date.isoformat(),
        "purchase_price": asset.purchase_price,
        "salvage_value": asset.salvage_value,
        "useful_life_years": asset.useful_life_years,
        "depreciation_method": asset.depreciation_method,
        "accumulated_depreciation": asset.accumulated_depreciation,
        "book_value": asset.purchase_price - asset.accumulated_depreciation,
        "location": asset.location,
        "status": asset.status,
        "depreciation_history": [{
            "date": d.depreciation_date.isoformat(),
            "amount": d.amount,
            "accumulated": d.accumulated_amount
        } for d in depreciation]
    }


@router.post("/{asset_id}/depreciate")
async def calculate_depreciation(
    asset_id: int,
    depreciation_date: date,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Calculate and record depreciation for an asset"""
    tenant_id = current_user["tenant_id"]

    asset = db.query(FixedAsset).filter(
        FixedAsset.id == asset_id,
        FixedAsset.tenant_id == tenant_id
    ).first()

    if not asset:
        raise HTTPException(status_code=404, detail="Asset not found")

    if asset.status != "active":
        raise HTTPException(status_code=400, detail="Cannot depreciate non-active asset")

    # Calculate depreciation
    depreciable_amount = asset.purchase_price - asset.salvage_value
    annual_depreciation = depreciable_amount / asset.useful_life_years
    monthly_depreciation = annual_depreciation / 12

    # Check if already depreciated for this period
    existing = db.query(DepreciationEntry).filter(
        DepreciationEntry.asset_id == asset_id,
        DepreciationEntry.depreciation_date == depreciation_date
    ).first()

    if existing:
        raise HTTPException(status_code=400, detail="Depreciation already recorded for this period")

    # Create depreciation entry
    entry = DepreciationEntry(
        tenant_id=tenant_id,
        asset_id=asset_id,
        depreciation_date=depreciation_date,
        amount=monthly_depreciation,
        accumulated_amount=asset.accumulated_depreciation + monthly_depreciation
    )

    db.add(entry)

    # Update asset
    asset.accumulated_depreciation += monthly_depreciation

    # Check if fully depreciated
    if asset.accumulated_depreciation >= depreciable_amount:
        asset.status = "fully_depreciated"
        asset.accumulated_depreciation = depreciable_amount

    db.commit()

    return {
        "depreciation_amount": monthly_depreciation,
        "accumulated_depreciation": asset.accumulated_depreciation,
        "book_value": asset.purchase_price - asset.accumulated_depreciation,
        "status": asset.status
    }


@router.post("/{asset_id}/dispose")
async def dispose_asset(
    asset_id: int,
    disposal_date: date,
    disposal_value: float,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Dispose of an asset"""
    tenant_id = current_user["tenant_id"]

    asset = db.query(FixedAsset).filter(
        FixedAsset.id == asset_id,
        FixedAsset.tenant_id == tenant_id
    ).first()

    if not asset:
        raise HTTPException(status_code=404, detail="Asset not found")

    if asset.status == "disposed":
        raise HTTPException(status_code=400, detail="Asset already disposed")

    book_value = asset.purchase_price - asset.accumulated_depreciation
    gain_loss = disposal_value - book_value

    asset.status = "disposed"
    asset.disposal_date = disposal_date
    asset.disposal_value = disposal_value

    db.commit()

    return {
        "book_value": book_value,
        "disposal_value": disposal_value,
        "gain_loss": gain_loss,
        "message": f"Asset disposed. {'Gain' if gain_loss > 0 else 'Loss'}: {abs(gain_loss):,.2f}"
    }


@router.get("/dashboard/summary")
async def get_assets_summary(
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Get fixed assets summary"""
    tenant_id = current_user["tenant_id"]

    assets = db.query(FixedAsset).filter(
        FixedAsset.tenant_id == tenant_id,
        FixedAsset.status == "active"
    ).all()

    total_cost = sum(a.purchase_price for a in assets)
    total_depreciation = sum(a.accumulated_depreciation for a in assets)
    total_book_value = total_cost - total_depreciation

    by_category = {}
    for asset in assets:
        if asset.category not in by_category:
            by_category[asset.category] = {"count": 0, "cost": 0, "book_value": 0}
        by_category[asset.category]["count"] += 1
        by_category[asset.category]["cost"] += asset.purchase_price
        by_category[asset.category]["book_value"] += asset.purchase_price - asset.accumulated_depreciation

    return {
        "total_assets": len(assets),
        "total_cost": total_cost,
        "total_depreciation": total_depreciation,
        "total_book_value": total_book_value,
        "by_category": by_category
    }
