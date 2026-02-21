#!/usr/bin/env python3
"""
Test Script to Verify Registration Flow
Run this after resetting the database to ensure everything works
"""

import os
import sys
from pathlib import Path

# Add backend to path
BACKEND_DIR = Path(__file__).parent / "backend"
sys.path.insert(0, str(BACKEND_DIR))

def test_database():
    """Test database connection and data"""
    from sqlalchemy import create_engine
    from app.database import Base, SessionLocal
    from app.models.tenant import Tenant, SubscriptionPlan
    from app.models.user import User
    from app.models.branch import Branch
    from app.models.permission import Permission, Role
    
    print("=" * 50)
    print("  Testing Database Setup")
    print("=" * 50)
    
    db = SessionLocal()
    try:
        # Check permissions
        perm_count = db.query(Permission).count()
        print(f"✓ Permissions count: {perm_count}")
        if perm_count == 0:
            print("  WARNING: No permissions found. Run reset_db.py first!")
        
        # Check subscription plans
        plan_count = db.query(SubscriptionPlan).count()
        print(f"✓ Subscription plans count: {plan_count}")
        if plan_count == 0:
            print("  WARNING: No subscription plans found. Run reset_db.py first!")
        
        # Check tenants
        tenant_count = db.query(Tenant).count()
        print(f"✓ Tenants count: {tenant_count}")
        
        # Check users
        user_count = db.query(User).count()
        print(f"✓ Users count: {user_count}")
        
        # Check branches
        branch_count = db.query(Branch).count()
        print(f"✓ Branches count: {branch_count}")
        
        # Check roles
        role_count = db.query(Role).count()
        print(f"✓ Roles count: {role_count}")
        
        print("\n" + "=" * 50)
        
        if tenant_count > 0:
            print("\nExisting Tenants:")
            for t in db.query(Tenant).all():
                print(f"  - {t.business_name} (subdomain: {t.subdomain})")
                branches = db.query(Branch).filter(Branch.tenant_id == t.id).all()
                print(f"    Branches: {[b.name for b in branches]}")
                users = db.query(User).filter(User.tenant_id == t.id).all()
                print(f"    Users: {[u.email for u in users]}")
        
        return perm_count > 0 and plan_count > 0
        
    finally:
        db.close()


def test_signup_flow():
    """Test the signup flow manually"""
    import requests
    import random
    
    print("\n" + "=" * 50)
    print("  Testing Signup Flow")
    print("=" * 50)
    
    API_BASE = "http://localhost:8000/api/v1"
    
    # Generate unique test data
    random_suffix = random.randint(1000, 9999)
    test_data = {
        "business_name": f"Test Business {random_suffix}",
        "email": f"test{random_suffix}@example.com",
        "username": f"testuser{random_suffix}",
        "password": "TestPass123!",
        "subdomain": f"test-{random_suffix}",
        "first_name": "Test",
        "last_name": "User"
    }
    
    print(f"\nAttempting signup with:")
    print(f"  Business: {test_data['business_name']}")
    print(f"  Email: {test_data['email']}")
    print(f"  Subdomain: {test_data['subdomain']}")
    
    try:
        response = requests.post(
            f"{API_BASE}/auth/signup",
            json=test_data,
            timeout=10
        )
        
        if response.status_code == 201:
            data = response.json()
            print("\n✓ Signup successful!")
            print(f"  Access token received: {data.get('access_token', '')[:20]}...")
            
            # Test getting session
            token = data.get('access_token')
            session_resp = requests.get(
                f"{API_BASE}/auth/session",
                headers={"Authorization": f"Bearer {token}"},
                timeout=10
            )
            
            if session_resp.status_code == 200:
                session_data = session_resp.json()
                print("\n✓ Session retrieved successfully!")
                print(f"  Tenant: {session_data.get('tenant', {}).get('business_name')}")
                print(f"  Selected Branch: {session_data.get('selected_branch', {}).get('name')}")
                print(f"  Accessible Branches: {len(session_data.get('accessible_branches', []))}")
                print(f"  Permissions: {len(session_data.get('permissions', []))}")
            else:
                print(f"\n✗ Failed to get session: {session_resp.status_code}")
                print(f"  Response: {session_resp.text}")
            
            # Test settings endpoint
            settings_resp = requests.get(
                f"{API_BASE}/settings/company",
                headers={"Authorization": f"Bearer {token}"},
                timeout=10
            )
            
            if settings_resp.status_code == 200:
                settings_data = settings_resp.json()
                print("\n✓ Company settings retrieved!")
                print(f"  Business Name: {settings_data.get('business_name')}")
                print(f"  Base Currency: {settings_data.get('base_currency')}")
            else:
                print(f"\n✗ Failed to get settings: {settings_resp.status_code}")
            
            # Test branches endpoint
            branches_resp = requests.get(
                f"{API_BASE}/branches",
                headers={"Authorization": f"Bearer {token}"},
                timeout=10
            )
            
            if branches_resp.status_code == 200:
                branches_data = branches_resp.json()
                print("\n✓ Branches retrieved!")
                print(f"  Branches: {[b['name'] for b in branches_data.get('items', [])]}")
            else:
                print(f"\n✗ Failed to get branches: {branches_resp.status_code}")
            
            return True
        else:
            print(f"\n✗ Signup failed with status {response.status_code}")
            print(f"  Response: {response.text}")
            return False
            
    except requests.exceptions.ConnectionError:
        print("\n✗ Cannot connect to backend. Is it running?")
        print("  Start the backend with: cd backend && python main.py")
        return False
    except Exception as e:
        print(f"\n✗ Error: {e}")
        return False


if __name__ == "__main__":
    print("\n" + "=" * 50)
    print("  Booklet ERP - Registration Flow Test")
    print("=" * 50 + "\n")
    
    # Test database first
    db_ok = test_database()
    
    if not db_ok:
        print("\n❌ Database not properly seeded. Run: python reset_db.py")
        sys.exit(1)
    
    # Test signup flow
    print("\n" + "-" * 50)
    print("  Make sure the backend is running on port 8000")
    print("  Start with: cd backend && python main.py")
    print("-" * 50)
    
    input("\nPress Enter to test signup flow...")
    signup_ok = test_signup_flow()
    
    print("\n" + "=" * 50)
    if db_ok and signup_ok:
        print("  ✓ All tests passed!")
    else:
        print("  ✗ Some tests failed. Check the output above.")
    print("=" * 50 + "\n")
