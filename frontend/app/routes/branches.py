"""Branches Frontend Routes"""
from flask import Blueprint, render_template, request, redirect, url_for, flash, session
import requests
import logging

branches_bp = Blueprint('branches', __name__, url_prefix='/branches')
API_BASE = 'http://localhost:8000/api/v1'
logger = logging.getLogger(__name__)

def get_headers():
    token = session.get('access_token')
    return {'Authorization': f'Bearer {token}', 'Content-Type': 'application/json'} if token else {'Content-Type': 'application/json'}

def get_items(data):
    if data is None: return []
    if isinstance(data, list): return data
    if isinstance(data, dict): return data.get('items', [])
    return []

def handle_api_error(response, action="operation"):
    """Extract error message from API response"""
    try:
        data = response.json()
        if isinstance(data, dict):
            return data.get('detail') or data.get('message') or f"{action} failed (status {response.status_code})"
        return f"{action} failed (status {response.status_code})"
    except:
        return f"{action} failed - server returned status {response.status_code}"

@branches_bp.route('/')
def index():
    try:
        response = requests.get(f'{API_BASE}/branches', headers=get_headers(), timeout=10)
        if response.status_code == 200:
            data = response.json()
        elif response.status_code == 401:
            flash('Please login again', 'error')
            return redirect('/login')
        else:
            flash(handle_api_error(response, 'Loading branches'), 'error')
            data = []
    except requests.exceptions.ConnectionError:
        flash('Cannot connect to server. Please ensure the backend is running.', 'error')
        data = []
    except Exception as e:
        logger.error(f"Error loading branches: {e}")
        flash(f'Error: {str(e)}', 'error')
        data = []
    return render_template('branches/index.html', branches=get_items(data))

@branches_bp.route('/create', methods=['GET', 'POST'])
def create():
    if request.method == 'POST':
        data = {
            'name': request.form.get('name', '').strip(),
            'code': request.form.get('code', '').strip() or None,
            'address': request.form.get('address', '').strip() or None,
            'city': request.form.get('city', '').strip() or None,
            'state': request.form.get('state', '').strip() or None,
            'phone': request.form.get('phone', '').strip() or None,
            'email': request.form.get('email', '').strip() or None
        }
        
        if not data['name']:
            flash('Branch name is required', 'error')
            return render_template('branches/form.html', branch=None)
        
        try:
            response = requests.post(f'{API_BASE}/branches', json=data, headers=get_headers(), timeout=10)
            if response.status_code in [200, 201]:
                flash('Branch created successfully', 'success')
                return redirect(url_for('branches.index'))
            elif response.status_code == 401:
                flash('Please login again', 'error')
                return redirect('/login')
            else:
                flash(handle_api_error(response, 'Creating branch'), 'error')
        except requests.exceptions.ConnectionError:
            flash('Cannot connect to server. Please ensure the backend is running.', 'error')
        except Exception as e:
            logger.error(f"Error creating branch: {e}")
            flash(f'Error: {str(e)}', 'error')
    
    return render_template('branches/form.html', branch=None)

@branches_bp.route('/<int:branch_id>/edit', methods=['GET', 'POST'])
def edit(branch_id):
    if request.method == 'POST':
        data = {
            'name': request.form.get('name', '').strip(),
            'address': request.form.get('address', '').strip() or None,
            'city': request.form.get('city', '').strip() or None,
            'state': request.form.get('state', '').strip() or None,
            'phone': request.form.get('phone', '').strip() or None,
            'email': request.form.get('email', '').strip() or None,
            'is_active': request.form.get('is_active') == 'on'
        }
        try:
            response = requests.put(f'{API_BASE}/branches/{branch_id}', json=data, headers=get_headers(), timeout=10)
            if response.status_code == 200:
                flash('Branch updated successfully', 'success')
                return redirect(url_for('branches.index'))
            elif response.status_code == 401:
                flash('Please login again', 'error')
                return redirect('/login')
            else:
                flash(handle_api_error(response, 'Updating branch'), 'error')
        except requests.exceptions.ConnectionError:
            flash('Cannot connect to server', 'error')
        except Exception as e:
            flash(f'Error: {str(e)}', 'error')
    
    try:
        response = requests.get(f'{API_BASE}/branches/{branch_id}', headers=get_headers(), timeout=10)
        branch = response.json() if response.status_code == 200 else None
    except:
        branch = None
    
    if not branch:
        flash('Branch not found', 'error')
        return redirect(url_for('branches.index'))
    
    return render_template('branches/form.html', branch=branch)
