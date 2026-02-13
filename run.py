#!/usr/bin/env python3
"""
Booklet ERP - Production Runner
Runs both FastAPI backend and Flask frontend servers
"""

import os
import sys
import subprocess
import threading
import time
import webbrowser
from pathlib import Path

# Project root
PROJECT_ROOT = Path(__file__).parent
BACKEND_DIR = PROJECT_ROOT / "backend"
FRONTEND_DIR = PROJECT_ROOT / "frontend"

# Add to path
sys.path.insert(0, str(BACKEND_DIR))
sys.path.insert(0, str(FRONTEND_DIR))




def check_env_file():
    """Check if .env file exists"""
    env_file = PROJECT_ROOT / ".env"
    env_example = PROJECT_ROOT / ".env.example"
    
    if not env_file.exists():
        if env_example.exists():
            print("⚠️  .env file not found. Creating from .env.example...")
            with open(env_example) as f:
                content = f.read()
            with open(env_file, 'w') as f:
                f.write(content)
            print("✅ Created .env file. Please edit with your settings.")
        else:
            print("❌ No .env file found. Please create one.")
            return False
    
    return True


def init_database():
    """Initialize database with tables and seed data"""
    print("\n📦 Initializing database...")
    
    os.chdir(BACKEND_DIR)
    
    # Run initialization
    init_script = '''
import asyncio
import sys
sys.path.insert(0, '.')

from app.database import engine, SessionLocal
from app.models import *
from app.models.tenant import SubscriptionPlan
from app.models.permission import Permission
from app.crud.permission import DEFAULT_PERMISSIONS
from app.crud.tenant import DEFAULT_PLANS

def init():
    from sqlalchemy import create_engine
    from app.database import Base
    
    # Create all tables
    print("Creating tables...")
    Base.metadata.create_all(bind=engine)
    
    db = SessionLocal()
    
    try:
        # Check if permissions exist
        existing = db.query(Permission).first()
        if not existing:
            print("Seeding permissions...")
            for perm in DEFAULT_PERMISSIONS:
                p = Permission(**perm)
                db.add(p)
            db.commit()
            print(f"✅ Seeded {len(DEFAULT_PERMISSIONS)} permissions")
        
        # Check if plans exist
        existing_plan = db.query(SubscriptionPlan).first()
        if not existing_plan:
            print("Seeding subscription plans...")
            for plan in DEFAULT_PLANS:
                sp = SubscriptionPlan(**plan)
                db.add(sp)
            db.commit()
            print(f"✅ Seeded {len(DEFAULT_PLANS)} subscription plans")
        
        print("✅ Database initialized successfully!")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    init()
'''
    
    result = subprocess.run(
        [sys.executable, "-c", init_script],
        cwd=BACKEND_DIR,
        capture_output=True,
        text=True
    )
    
    print(result.stdout)
    if result.returncode != 0:
        print(result.stderr)
        return False
    
    return True


def run_backend():
    """Run FastAPI backend server"""
    import sys

    # Add backend to path
    sys.path.insert(0, str(BACKEND_DIR))

    # Run backend directly
    import subprocess
    subprocess.run([sys.executable, str(BACKEND_DIR / "main.py")])


def run_frontend():
    """Run Flask frontend server"""
    os.chdir(FRONTEND_DIR)
    
    # Set Flask environment
    os.environ["FLASK_APP"] = "app:create_app()"
    os.environ["FLASK_ENV"] = "development"
    os.environ["FLASK_DEBUG"] = "1"
    
    subprocess.run([
        sys.executable, "-m", "flask", "run",
        "--host", "0.0.0.0",
        "--port", "5000",
        "--debug"
    ])


def run_tests():
    """Run test suite"""
    print("\n🧪 Running tests...\n")
    
    os.chdir(PROJECT_ROOT)
    
    result = subprocess.run(
        [sys.executable, "-m", "pytest", "tests/", "-v", "--tb=short"],
        cwd=PROJECT_ROOT
    )
    
    return result.returncode == 0


def main():
    """Main entry point"""
    import argparse
    
    parser = argparse.ArgumentParser(
        description="Booklet ERP - Multi-Tenant SaaS Platform",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python run.py init       Initialize database
  python run.py run        Start both servers
  python run.py backend    Start only backend API
  python run.py frontend   Start only frontend
  python run.py test       Run test suite
        """
    )
    
    parser.add_argument(
        "command",
        choices=["run", "backend", "frontend", "init", "test", "install"],
        help="Command to run"
    )
    
    parser.add_argument(
        "--no-browser",
        action="store_true",
        help="Don't open browser automatically"
    )
    
    parser.add_argument(
        "--port",
        type=int,
        default=5000,
        help="Frontend port (default: 5000)"
    )
    
    parser.add_argument(
        "--api-port",
        type=int,
        default=8000,
        help="Backend API port (default: 8000)"
    )
    
    args = parser.parse_args()
    
    # Header
    print("\n" + "=" * 60)
    print("  📚 Booklet ERP - Multi-Tenant SaaS Platform")
    print("  🇳🇬 Nigerian Naira (₦) Default Currency")
    print("=" * 60 + "\n")
    
    # Handle commands
    if args.command == "install":
        print("📦 Installing dependencies...\n")
        subprocess.run([
            sys.executable, "-m", "pip", "install",
            "-r", str(PROJECT_ROOT / "requirements.txt")
        ])
        print("\n✅ Dependencies installed!")
        return
    
    if args.command == "test":
        success = run_tests()
        sys.exit(0 if success else 1)
        return
    

    
    if not check_env_file():
        sys.exit(1)
    
    if args.command == "init":
        success = init_database()
        sys.exit(0 if success else 1)
        return
    
    if args.command == "backend":
        print("🚀 Starting Backend API...")
        print(f"   URL: http://localhost:{args.api_port}")
        print(f"   Docs: http://localhost:{args.api_port}/api/docs\n")
        run_backend()
        return
    
    if args.command == "frontend":
        print("🚀 Starting Frontend...")
        print(f"   URL: http://localhost:{args.port}\n")
        os.environ["API_BASE_URL"] = f"http://localhost:{args.api_port}/api/v1"
        run_frontend()
        return
    
    if args.command == "run":
        print("🚀 Starting Booklet ERP...\n")
        print(f"   Frontend:    http://localhost:{args.port}")
        print(f"   Backend API: http://localhost:{args.api_port}")
        print(f"   API Docs:    http://localhost:{args.api_port}/api/docs")
        print(f"   Health:      http://localhost:{args.api_port}/health\n")
        
        # Set environment
        os.environ["API_BASE_URL"] = f"http://localhost:{args.api_port}/api/v1"
        os.environ["FLASK_APP"] = "app:create_app()"
        os.environ["FLASK_ENV"] = "development"
        
        # Start backend in thread
        backend_thread = threading.Thread(
            target=run_backend,
            daemon=True
        )
        backend_thread.start()
        
        # Wait for backend to start
        print("⏳ Waiting for backend to start...")
        time.sleep(3)
        
        # Open browser
        if not args.no_browser:
            print("🌐 Opening browser...")
            webbrowser.open(f"http://localhost:{args.port}")
        
        print("\n✅ Servers running! Press Ctrl+C to stop.\n")
        
        try:
            # Run frontend in main thread
            run_frontend()
        except KeyboardInterrupt:
            print("\n\n👋 Shutting down servers...")
            print("Goodbye!")


if __name__ == "__main__":
    main()
