"""Team Management Frontend Routes"""
from flask import Blueprint, render_template, request, redirect, url_for, flash, session
import requests
import logging

team_bp = Blueprint('team', __name__, url_prefix='/team')
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

def handle_error(response):
    try:
        data = response.json()
        return data.get('detail', data.get('message', f'Error (HTTP {response.status_code})'))
    except: return f'Error - HTTP {response.status_code}'

@team_bp.route('/')
def index():
    try:
        response = requests.get(f'{API_BASE}/team', headers=get_headers(), timeout=10)
        if response.status_code == 200:
            data = response.json()
        elif response.status_code == 401:
            flash('Please login again', 'error')
            return redirect('/login')
        else:
            data = []
    except requests.exceptions.ConnectionError:
        flash('Cannot connect to server', 'error')
        data = []
    except: data = []
    return render_template('team/index.html', members=get_items(data))

@team_bp.route('/create', methods=['GET', 'POST'])
def create():
    if request.method == 'POST':
        data = {
            'username': request.form.get('username', '').strip(),
            'email': request.form.get('email', '').strip(),
            'password': request.form.get('password', ''),
            'first_name': request.form.get('first_name', '').strip(),
            'last_name': request.form.get('last_name', '').strip(),
            'phone': request.form.get('phone', '').strip() or None,
            'role_id': int(request.form.get('role_id', 1)),
            'branch_id': int(request.form.get('branch_id', session.get('branch_id', 1)))
        }
        if not all([data['username'], data['email'], data['password']]):
            flash('Username, email and password are required', 'error')
        else:
            try:
                response = requests.post(f'{API_BASE}/team', json=data, headers=get_headers(), timeout=10)
                if response.status_code in [200, 201]:
                    flash('Team member created successfully', 'success')
                    return redirect(url_for('team.index'))
                else:
                    flash(handle_error(response), 'error')
            except requests.exceptions.ConnectionError:
                flash('Cannot connect to server', 'error')
            except Exception as e:
                flash(f'Error: {str(e)}', 'error')
    
    # Get roles and branches
    roles, branches = [], []
    try:
        r = requests.get(f'{API_BASE}/roles', headers=get_headers(), timeout=5)
        if r.status_code == 200: roles = get_items(r.json())
    except: pass
    try:
        r = requests.get(f'{API_BASE}/branches', headers=get_headers(), timeout=5)
        if r.status_code == 200: branches = get_items(r.json())
    except: pass
    
    return render_template('team/form.html', member=None, roles=roles, branches=branches)

@team_bp.route('/<int:user_id>/edit', methods=['GET', 'POST'])
def edit(user_id):
    if request.method == 'POST':
        data = {
            'first_name': request.form.get('first_name', '').strip(),
            'last_name': request.form.get('last_name', '').strip(),
            'email': request.form.get('email', '').strip(),
            'phone': request.form.get('phone', '').strip() or None,
            'role_id': int(request.form.get('role_id', 1)),
            'is_active': request.form.get('is_active') == 'on'
        }
        try:
            response = requests.put(f'{API_BASE}/team/{user_id}', json=data, headers=get_headers(), timeout=10)
            if response.status_code == 200:
                flash('Team member updated successfully', 'success')
                return redirect(url_for('team.index'))
            else:
                flash(handle_error(response), 'error')
        except requests.exceptions.ConnectionError:
            flash('Cannot connect to server', 'error')
        except Exception as e:
            flash(f'Error: {str(e)}', 'error')
    
    member, roles = None, []
    try:
        r = requests.get(f'{API_BASE}/team/{user_id}', headers=get_headers(), timeout=5)
        if r.status_code == 200: member = r.json()
    except: pass
    try:
        r = requests.get(f'{API_BASE}/roles', headers=get_headers(), timeout=5)
        if r.status_code == 200: roles = get_items(r.json())
    except: pass
    
    return render_template('team/form.html', member=member, roles=roles)

@team_bp.route('/<int:user_id>/delete', methods=['POST'])
def delete(user_id):
    try:
        response = requests.delete(f'{API_BASE}/team/{user_id}', headers=get_headers(), timeout=10)
        if response.status_code == 200:
            flash('Team member deactivated', 'success')
        else:
            flash(handle_error(response), 'error')
    except requests.exceptions.ConnectionError:
        flash('Cannot connect to server', 'error')
    except Exception as e:
        flash(f'Error: {str(e)}', 'error')
    return redirect(url_for('team.index'))

@team_bp.route('/roles')
def roles():
    try:
        response = requests.get(f'{API_BASE}/roles', headers=get_headers(), timeout=10)
        data = response.json() if response.status_code == 200 else []
    except:
        data = []
    return render_template('team/roles.html', roles=get_items(data))

@team_bp.route('/roles/create', methods=['GET', 'POST'])
def create_role():
    if request.method == 'POST':
        permissions = request.form.getlist('permissions')
        data = {
            'name': request.form.get('name', '').strip(),
            'description': request.form.get('description', '').strip(),
            'permissions': [int(p) for p in permissions if p]
        }
        try:
            response = requests.post(f'{API_BASE}/roles', json=data, headers=get_headers(), timeout=10)
            if response.status_code in [200, 201]:
                flash('Role created successfully', 'success')
                return redirect(url_for('team.roles'))
            else:
                flash(handle_error(response), 'error')
        except requests.exceptions.ConnectionError:
            flash('Cannot connect to server', 'error')
        except Exception as e:
            flash(f'Error: {str(e)}', 'error')
    return render_template('team/role_form.html', role=None, permissions={})
