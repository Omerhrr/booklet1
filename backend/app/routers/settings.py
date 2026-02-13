"""
Settings Router - Company Settings and Configuration
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import Optional
from pydantic import BaseModel

from ..database import get_db
from ..security import get_current_user
from ..models.tenant import Tenant

router = APIRouter(prefix="/settings", tags=["Settings"])


class CompanySettingsUpdate(BaseModel):
    business_name: Optional[str] = None
    trading_name: Optional[str] = None
    industry: Optional[str] = None
    address: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    country: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[str] = None
    website: Optional[str] = None
    tax_id: Optional[str] = None  # Nigerian TIN
    rc_number: Optional[str] = None  # Nigerian CAC number
    currency: Optional[str] = None
    fiscal_year_start: Optional[int] = None
    logo_url: Optional[str] = None


class InvoiceSettingsUpdate(BaseModel):
    invoice_prefix: Optional[str] = None
    quote_prefix: Optional[str] = None
    credit_note_prefix: Optional[str] = None
    default_payment_terms: Optional[int] = None
    default_vat_rate: Optional[float] = None


@router.get("/company")
async def get_company_settings(
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Get company settings"""
    tenant_id = current_user["tenant_id"]

    tenant = db.query(Tenant).filter(Tenant.id == tenant_id).first()

    if not tenant:
        raise HTTPException(status_code=404, detail="Company not found")

    return {
        "id": tenant.id,
        "business_name": tenant.business_name,
        "trading_name": tenant.trading_name,
        "industry": tenant.industry,
        "address": tenant.address,
        "city": tenant.city,
        "state": tenant.state,
        "country": tenant.country,
        "phone": tenant.phone,
        "email": tenant.email,
        "website": tenant.website,
        "tax_id": tenant.tax_id,
        "rc_number": tenant.rc_number,
        "currency": tenant.currency,
        "fiscal_year_start": tenant.fiscal_year_start,
        "logo_url": tenant.logo_url,
        "timezone": tenant.timezone,
        "date_format": tenant.date_format,
        "created_at": tenant.created_at.isoformat() if tenant.created_at else None
    }


@router.put("/company")
async def update_company_settings(
    settings_data: CompanySettingsUpdate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Update company settings"""
    tenant_id = current_user["tenant_id"]

    tenant = db.query(Tenant).filter(Tenant.id == tenant_id).first()

    if not tenant:
        raise HTTPException(status_code=404, detail="Company not found")

    for field, value in settings_data.dict(exclude_unset=True).items():
        setattr(tenant, field, value)

    db.commit()
    return {"message": "Company settings updated successfully"}


@router.get("/invoice")
async def get_invoice_settings(
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Get invoice settings"""
    tenant_id = current_user["tenant_id"]

    tenant = db.query(Tenant).filter(Tenant.id == tenant_id).first()

    if not tenant:
        raise HTTPException(status_code=404, detail="Company not found")

    return {
        "invoice_prefix": tenant.invoice_prefix or "INV",
        "quote_prefix": tenant.quote_prefix or "QT",
        "credit_note_prefix": tenant.credit_note_prefix or "CN",
        "default_payment_terms": tenant.default_payment_terms or 30,
        "default_vat_rate": tenant.default_vat_rate or 7.5,
        "invoice_notes": tenant.invoice_notes,
        "invoice_terms": tenant.invoice_terms
    }


@router.put("/invoice")
async def update_invoice_settings(
    settings_data: InvoiceSettingsUpdate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Update invoice settings"""
    tenant_id = current_user["tenant_id"]

    tenant = db.query(Tenant).filter(Tenant.id == tenant_id).first()

    if not tenant:
        raise HTTPException(status_code=404, detail="Company not found")

    if settings_data.invoice_prefix:
        tenant.invoice_prefix = settings_data.invoice_prefix
    if settings_data.quote_prefix:
        tenant.quote_prefix = settings_data.quote_prefix
    if settings_data.credit_note_prefix:
        tenant.credit_note_prefix = settings_data.credit_note_prefix
    if settings_data.default_payment_terms:
        tenant.default_payment_terms = settings_data.default_payment_terms
    if settings_data.default_vat_rate is not None:
        tenant.default_vat_rate = settings_data.default_vat_rate

    db.commit()
    return {"message": "Invoice settings updated successfully"}


@router.get("/nigerian-states")
async def get_nigerian_states():
    """Get list of Nigerian states"""
    states = [
        "Abia", "Adamawa", "Akwa Ibom", "Anambra", "Bauchi", "Bayelsa", "Benue",
        "Borno", "Cross River", "Delta", "Ebonyi", "Edo", "Ekiti", "Enugu",
        "FCT", "Gombe", "Imo", "Jigawa", "Kaduna", "Kano", "Katsina", "Kebbi",
        "Kogi", "Kwara", "Lagos", "Nasarawa", "Niger", "Ogun", "Ondo", "Osun",
        "Oyo", "Plateau", "Rivers", "Sokoto", "Taraba", "Yobe", "Zamfara"
    ]
    return {"states": states}


@router.get("/industries")
async def get_industries():
    """Get list of industries"""
    industries = [
        "Agriculture",
        "Banking & Finance",
        "Construction",
        "Education",
        "Energy & Power",
        "Entertainment",
        "Food & Beverage",
        "Healthcare",
        "Hospitality & Tourism",
        "Information Technology",
        "Legal Services",
        "Manufacturing",
        "Media & Communications",
        "Mining & Quarrying",
        "Non-Profit",
        "Oil & Gas",
        "Pharmaceuticals",
        "Real Estate",
        "Retail & Wholesale",
        "Telecommunications",
        "Transportation & Logistics",
        "Other"
    ]
    return {"industries": industries}
