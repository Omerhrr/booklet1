"""
Branches Frontend Routes
"""
from flask import Blueprint, render_template, request, redirect, url_for, flash, session
import requests

branches_bp = Blueprint('branches', __name__, url_prefix='/branches')

API_BASE = 'http://localhost:8000/api/v1'


def get_headers():
    token = session.get('access_token')
    return {'Authorization': f'Bearer {token}'} if token else {}


@branches_bp.route('/')
def index():
    """Branches list"""
    try:
        response = requests.get(f'{API_BASE}/branches', headers=get_headers())
        branches = response.json() if response.status_code == 200 else {'items': []}
    except:
        branches = {'items': []}

    return render_template('branches/index.html', branches=branches)


@branches_bp.route('/create', methods=['GET', 'POST'])
def create():
    """Create branch"""
    if request.method == 'POST':
        data = {
            'name': request.form.get('name'),
            'code': request.form.get('code'),
            'address': request.form.get('address'),
            'city': request.form.get('city'),
            'state': request.form.get('state'),
            'phone': request.form.get('phone'),
            'email': request.form.get('email'),
            'is_head_office': request.form.get('is_head_office') == 'on'
        }

        try:
            response = requests.post(
                f'{API_BASE}/branches',
                json=data,
                headers=get_headers()
            )
            if response.status_code == 200:
                flash('Branch created successfully', 'success')
                return redirect(url_for('branches.index'))
            else:
                flash(response.json().get('detail', 'Error'), 'error')
        except Exception as e:
            flash(f'Error: {str(e)}', 'error')

    try:
        states_resp = requests.get(f'{API_BASE}/settings/nigerian-states', headers=get_headers())
        states = states_resp.json().get('states', []) if states_resp.status_code == 200 else []
    except:
        states = []

    return render_template('branches/form.html', branch=None, states=states)


@branches_bp.route('/<int:branch_id>/edit', methods=['GET', 'POST'])
def edit(branch_id):
    """Edit branch"""
    if request.method == 'POST':
        data = {
            'name': request.form.get('name'),
            'code': request.form.get('code'),
            'address': request.form.get('address'),
            'city': request.form.get('city'),
            'state': request.form.get('state'),
            'phone': request.form.get('phone'),
            'email': request.form.get('email'),
            'is_active': request.form.get('is_active') == 'on'
        }

        try:
            response = requests.put(
                f'{API_BASE}/branches/{branch_id}',
                json=data,
                headers=get_headers()
            )
            if response.status_code == 200:
                flash('Branch updated successfully', 'success')
                return redirect(url_for('branches.index'))
        except Exception as e:
            flash(f'Error: {str(e)}', 'error')

    try:
        branch_resp = requests.get(f'{API_BASE}/branches/{branch_id}', headers=get_headers())
        branch = branch_resp.json() if branch_resp.status_code == 200 else None
    except:
        branch = None

    try:
        states_resp = requests.get(f'{API_BASE}/settings/nigerian-states', headers=get_headers())
        states = states_resp.json().get('states', []) if states_resp.status_code == 200 else []
    except:
        states = []

    return render_template('branches/form.html', branch=branch, states=states)


@branches_bp.route('/<int:branch_id>/delete', methods=['POST'])
def delete(branch_id):
    """Deactivate branch"""
    try:
        response = requests.delete(
            f'{API_BASE}/branches/{branch_id}',
            headers=get_headers()
        )
        if response.status_code == 200:
            flash('Branch deactivated', 'success')
        else:
            flash(response.json().get('detail', 'Error'), 'error')
    except Exception as e:
        flash(f'Error: {str(e)}', 'error')

    return redirect(url_for('branches.index'))


@branches_bp.route('/<int:branch_id>/set-head-office', methods=['POST'])
def set_head_office(branch_id):
    """Set branch as head office"""
    try:
        response = requests.post(
            f'{API_BASE}/branches/{branch_id}/set-head-office',
            headers=get_headers()
        )
        if response.status_code == 200:
            flash('Head office updated', 'success')
        else:
            flash(response.json().get('detail', 'Error'), 'error')
    except Exception as e:
        flash(f'Error: {str(e)}', 'error')

    return redirect(url_for('branches.index'))
