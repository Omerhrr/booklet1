"""
Team Management Frontend Routes
"""
from flask import Blueprint, render_template, request, redirect, url_for, flash, session
import requests

team_bp = Blueprint('team', __name__, url_prefix='/team')

API_BASE = 'http://localhost:8000/api/v1'


def get_headers():
    token = session.get('access_token')
    return {'Authorization': f'Bearer {token}'} if token else {}


@team_bp.route('/')
def index():
    """Team members list"""
    try:
        response = requests.get(f'{API_BASE}/team', headers=get_headers())
        members = response.json() if response.status_code == 200 else {'items': []}
    except:
        members = {'items': []}

    return render_template('team/index.html', members=members)


@team_bp.route('/create', methods=['GET', 'POST'])
def create():
    """Create team member"""
    if request.method == 'POST':
        data = {
            'username': request.form.get('username'),
            'email': request.form.get('email'),
            'password': request.form.get('password'),
            'first_name': request.form.get('first_name'),
            'last_name': request.form.get('last_name'),
            'phone': request.form.get('phone'),
            'role_id': int(request.form.get('role_id')),
            'branch_id': int(request.form.get('branch_id', session.get('branch_id', 1)))
        }

        try:
            response = requests.post(
                f'{API_BASE}/team',
                json=data,
                headers=get_headers()
            )
            if response.status_code == 200:
                flash('Team member created successfully', 'success')
                return redirect(url_for('team.index'))
            else:
                flash(response.json().get('detail', 'Error'), 'error')
        except Exception as e:
            flash(f'Error: {str(e)}', 'error')

    # Get roles and branches
    try:
        roles_resp = requests.get(f'{API_BASE}/roles', headers=get_headers())
        roles = roles_resp.json() if roles_resp.status_code == 200 else {'items': []}
    except:
        roles = {'items': []}

    try:
        branches_resp = requests.get(f'{API_BASE}/branches', headers=get_headers())
        branches = branches_resp.json() if branches_resp.status_code == 200 else {'items': []}
    except:
        branches = {'items': []}

    return render_template('team/form.html', member=None, roles=roles, branches=branches)


@team_bp.route('/<int:user_id>/edit', methods=['GET', 'POST'])
def edit(user_id):
    """Edit team member"""
    if request.method == 'POST':
        data = {
            'first_name': request.form.get('first_name'),
            'last_name': request.form.get('last_name'),
            'email': request.form.get('email'),
            'phone': request.form.get('phone'),
            'role_id': int(request.form.get('role_id')),
            'is_active': request.form.get('is_active') == 'on'
        }

        try:
            response = requests.put(
                f'{API_BASE}/team/{user_id}',
                json=data,
                headers=get_headers()
            )
            if response.status_code == 200:
                flash('Team member updated successfully', 'success')
                return redirect(url_for('team.index'))
        except Exception as e:
            flash(f'Error: {str(e)}', 'error')

    try:
        member_resp = requests.get(f'{API_BASE}/team/{user_id}', headers=get_headers())
        member = member_resp.json() if member_resp.status_code == 200 else None
    except:
        member = None

    try:
        roles_resp = requests.get(f'{API_BASE}/roles', headers=get_headers())
        roles = roles_resp.json() if roles_resp.status_code == 200 else {'items': []}
    except:
        roles = {'items': []}

    return render_template('team/form.html', member=member, roles=roles)


@team_bp.route('/<int:user_id>/delete', methods=['POST'])
def delete(user_id):
    """Deactivate team member"""
    try:
        response = requests.delete(
            f'{API_BASE}/team/{user_id}',
            headers=get_headers()
        )
        if response.status_code == 200:
            flash('Team member deactivated', 'success')
        else:
            flash(response.json().get('detail', 'Error'), 'error')
    except Exception as e:
        flash(f'Error: {str(e)}', 'error')

    return redirect(url_for('team.index'))


@team_bp.route('/roles')
def roles():
    """Roles management"""
    try:
        response = requests.get(f'{API_BASE}/roles', headers=get_headers())
        roles = response.json() if response.status_code == 200 else {'items': []}
    except:
        roles = {'items': []}

    return render_template('team/roles.html', roles=roles)


@team_bp.route('/roles/create', methods=['GET', 'POST'])
def create_role():
    """Create role"""
    if request.method == 'POST':
        permissions = request.form.getlist('permissions')
        data = {
            'name': request.form.get('name'),
            'description': request.form.get('description'),
            'permissions': [int(p) for p in permissions]
        }

        try:
            response = requests.post(
                f'{API_BASE}/roles',
                json=data,
                headers=get_headers()
            )
            if response.status_code == 200:
                flash('Role created successfully', 'success')
                return redirect(url_for('team.roles'))
        except Exception as e:
            flash(f'Error: {str(e)}', 'error')

    try:
        perms_resp = requests.get(f'{API_BASE}/roles/permissions/all', headers=get_headers())
        permissions = perms_resp.json() if perms_resp.status_code == 200 else {}
    except:
        permissions = {}

    return render_template('team/role_form.html', role=None, permissions=permissions)
