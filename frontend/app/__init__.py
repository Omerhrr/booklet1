"""
Flask Frontend Application
Server-side rendering with Jinja2 templates
"""

from flask import Flask, session, redirect, url_for, request, g
from functools import wraps
import requests
import os

# Configuration
API_BASE_URL = os.getenv("API_BASE_URL", "http://localhost:8000/api/v1")


def create_app(config_name='development'):
    """Flask application factory"""
    app = Flask(__name__,
                template_folder='templates',
                static_folder='static')
    
    app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'dev-secret-key-change-in-production')
    app.config['API_BASE_URL'] = API_BASE_URL
    
    # Register blueprints
    from .routes import auth, dashboard, customers, vendors, sales, purchases, inventory, accounting, hr, reports, settings, branches, team

    app.register_blueprint(auth.bp)
    app.register_blueprint(dashboard.bp)
    app.register_blueprint(customers.customers_bp)
    app.register_blueprint(vendors.vendors_bp)
    app.register_blueprint(sales.sales_bp)
    app.register_blueprint(purchases.purchases_bp)
    app.register_blueprint(inventory.inventory_bp)
    app.register_blueprint(accounting.accounting_bp)
    app.register_blueprint(hr.hr_bp)
    app.register_blueprint(reports.reports_bp)
    app.register_blueprint(settings.settings_bp)
    app.register_blueprint(branches.branches_bp)
    app.register_blueprint(team.team_bp)
    
    # Context processors
    @app.context_processor
    def utility_processor():
        """Make utilities available in templates"""
        return {
            'tenant': lambda: session.get('tenant'),
            'user': lambda: session.get('user'),
            'selected_branch': lambda: session.get('selected_branch'),
            'accessible_branches': lambda: session.get('accessible_branches', []),
            'permissions': lambda: session.get('permissions', []),
            'has_permission': has_permission,
            'format_currency': format_currency,
            'format_date': format_date,
            'format_datetime': format_datetime,
        }
    
    # Before request - check authentication
    @app.before_request
    def load_user():
        """Load user from session before each request"""
        g.user = session.get('user')
        g.tenant = session.get('tenant')
        g.selected_branch = session.get('selected_branch')
        g.permissions = session.get('permissions', [])
    
    # Error handlers
    @app.errorhandler(404)
    def not_found(error):
        return render_template('errors/404.html'), 404
    
    @app.errorhandler(500)
    def internal_error(error):
        return render_template('errors/500.html'), 500
    
    return app


# ============================================
# HELPER FUNCTIONS
# ============================================

def get_api_headers():
    """Get API request headers with auth token"""
    token = session.get('access_token')
    headers = {
        'Content-Type': 'application/json'
    }
    if token:
        headers['Authorization'] = f'Bearer {token}'
    return headers


def api_get(endpoint, params=None):
    """Make GET request to API"""
    try:
        response = requests.get(
            f"{API_BASE_URL}{endpoint}",
            headers=get_api_headers(),
            params=params
        )
        if response.status_code == 401:
            # Token expired, clear session
            session.clear()
            return None
        return response.json() if response.status_code == 200 else None
    except Exception as e:
        print(f"API Error: {e}")
        return None


def api_post(endpoint, data=None):
    """Make POST request to API"""
    try:
        response = requests.post(
            f"{API_BASE_URL}{endpoint}",
            headers=get_api_headers(),
            json=data
        )
        return response.json() if response.status_code in [200, 201] else response.json()
    except Exception as e:
        print(f"API Error: {e}")
        return {'error': str(e)}


def api_put(endpoint, data=None):
    """Make PUT request to API"""
    try:
        response = requests.put(
            f"{API_BASE_URL}{endpoint}",
            headers=get_api_headers(),
            json=data
        )
        return response.json() if response.status_code == 200 else response.json()
    except Exception as e:
        print(f"API Error: {e}")
        return {'error': str(e)}


def api_delete(endpoint):
    """Make DELETE request to API"""
    try:
        response = requests.delete(
            f"{API_BASE_URL}{endpoint}",
            headers=get_api_headers()
        )
        return response.status_code == 200 or response.status_code == 204
    except Exception as e:
        print(f"API Error: {e}")
        return False


def login_required(f):
    """Decorator to require login"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not session.get('user'):
            return redirect(url_for('auth.login'))
        return f(*args, **kwargs)
    return decorated_function


def permission_required(permission):
    """Decorator to check permission"""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not session.get('user'):
                return redirect(url_for('auth.login'))
            
            # Superusers have all permissions
            if session.get('is_superuser'):
                return f(*args, **kwargs)
            
            permissions = session.get('permissions', [])
            if permission not in permissions:
                from flask import abort
                abort(403)
            return f(*args, **kwargs)
        return decorated_function
    return decorator


def has_permission(permission):
    """Check if current user has permission"""
    if session.get('is_superuser'):
        return True
    permissions = session.get('permissions', [])
    if 'all' in permissions:
        return True
    return permission in permissions


# Currency formatting (Nigerian Naira as default)
def format_currency(amount, currency='NGN'):
    """Format amount as currency"""
    if amount is None:
        return '-'
    
    symbols = {
        'NGN': '₦',
        'USD': '$',
        'EUR': '€',
        'GBP': '£'
    }
    
    symbol = symbols.get(currency, currency)
    
    try:
        return f"{symbol}{float(amount):,.2f}"
    except (ValueError, TypeError):
        return '-'


def format_date(date_str):
    """Format date string"""
    if not date_str:
        return '-'
    from datetime import datetime
    try:
        if isinstance(date_str, str):
            dt = datetime.fromisoformat(date_str.replace('Z', '+00:00'))
        else:
            dt = date_str
        return dt.strftime('%d/%m/%Y')
    except:
        return str(date_str)


def format_datetime(datetime_str):
    """Format datetime string"""
    if not datetime_str:
        return '-'
    from datetime import datetime
    try:
        if isinstance(datetime_str, str):
            dt = datetime.fromisoformat(datetime_str.replace('Z', '+00:00'))
        else:
            dt = datetime_str
        return dt.strftime('%d/%m/%Y %H:%M')
    except:
        return str(datetime_str)


# Import render_template for error handlers
from flask import render_template
