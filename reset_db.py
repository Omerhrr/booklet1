#!/usr/bin/env python3
"""
Database Reset Script - Drops and recreates all tables
Run this when you change model schemas
"""

import os
import sys
from pathlib import Path

# Add backend to path
BACKEND_DIR = Path(__file__).parent / "backend"
sys.path.insert(0, str(BACKEND_DIR))

def reset_database():
    """Drop and recreate all tables"""
    from sqlalchemy import create_engine
    from app.database import Base, SessionLocal
    from app.models import tenant, user, permission, account, branch, customer, vendor, product, sales, purchase, expense, hr, fixed_assets, budget, banking, audit
    from app.models.tenant import SubscriptionPlan
    from app.models.permission import Permission
    from app.crud.permission import DEFAULT_PERMISSIONS
    from app.crud.tenant import DEFAULT_PLANS
    
    # Database path
    db_path = BACKEND_DIR / "booklet.db"
    
    # Delete existing database
    if db_path.exists():
        print(f"Deleting existing database: {db_path}")
        os.remove(db_path)
    
    # Create engine
    DATABASE_URL = f"sqlite:///{db_path}"
    engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
    
    # Create all tables
    print("Creating all tables...")
    Base.metadata.create_all(bind=engine)
    print("✅ Tables created")
    
    # Seed default data
    db = SessionLocal()
    try:
        # Seed permissions
        print("Seeding permissions...")
        for perm in DEFAULT_PERMISSIONS:
            p = Permission(**perm)
            db.add(p)
        db.commit()
        print(f"✅ Seeded {len(DEFAULT_PERMISSIONS)} permissions")
        
        # Seed subscription plans
        print("Seeding subscription plans...")
        for plan in DEFAULT_PLANS:
            sp = SubscriptionPlan(**plan)
            db.add(sp)
        db.commit()
        print(f"✅ Seeded {len(DEFAULT_PLANS)} subscription plans")
        
    except Exception as e:
        print(f"❌ Error seeding data: {e}")
        db.rollback()
        raise
    finally:
        db.close()
    
    print("\n✅ Database reset complete!")
    print(f"   Database location: {db_path}")

if __name__ == "__main__":
    print("=" * 50)
    print("  Booklet ERP - Database Reset")
    print("=" * 50 + "\n")
    
    confirm = input("This will DELETE ALL DATA. Continue? (yes/no): ")
    if confirm.lower() == 'yes':
        reset_database()
    else:
        print("Cancelled.")
