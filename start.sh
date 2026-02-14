#!/usr/bin/env bash
# Booklet ERP - Quick Start Script

set -e

echo "=============================================="
echo "  Booklet ERP - Multi-Tenant SaaS Platform"
echo "=============================================="
echo ""


# Check for .env file
if [ ! -f ".env" ]; then
    echo "Creating .env file from template..."
    cp .env.example .env
    echo "✓ Created .env file - please review and update settings"
fi

# Initialize database
echo "Initializing database..."
python run.py init

echo ""
echo "=============================================="
echo "  ✓ Setup Complete!"
echo "=============================================="
echo ""
echo "To start the application:"
echo "  python run.py run"
echo ""
echo "Access the application:"
echo "  Frontend: http://localhost:5000"
echo "  API Docs: http://localhost:8000/api/docs"
echo ""
