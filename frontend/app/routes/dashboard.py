"""
Dashboard Routes
"""

from flask import Blueprint, render_template, session
from .. import api_get, login_required

bp = Blueprint('dashboard', __name__)


@bp.route('/')
@login_required
def index():
    """Main dashboard"""
    # Get dashboard data from API
    dashboard_data = api_get('/dashboard')
    
    return render_template('dashboard/index.html', dashboard=dashboard_data)
