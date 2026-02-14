"""Branches Frontend Routes"""
from flask import Blueprint, render_template, request, redirect, url_for, flash, session
import requests

branches_bp = Blueprint('branches', __name__, url_prefix='/branches')
API_BASE = 'http://localhost:8000/api/v1'

def get_headers():
    token = session.get('access_token')
    return {'Authorization': f'Bearer {token}'} if token else {}

def get_items(data):
    if data is None: return []
    if isinstance(data, list): return data
    if isinstance(data, dict): return data.get('items', [])
    return []

@branches_bp.route('/')
def index():
    try:
        response = requests.get(f'{API_BASE}/branches', headers=get_headers())
        data = response.json() if response.status_code == 200 else []
    except:
        data = []
    return render_template('branches/index.html', branches=get_items(data))

@branches_bp.route('/create', methods=['GET', 'POST'])
def create():
    if request.method == 'POST':
        data = {
            'name': request.form.get('name'),
            'code': request.form.get('code'),
            'address': request.form.get('address'),
            'city': request.form.get('city'),
            'state': request.form.get('state'),
            'phone': request.form.get('phone'),
            'email': request.form.get('email'),
            'manager_id': request.form.get('manager_id')
        }
        try:
            response = requests.post(f'{API_BASE}/branches', json=data, headers=get_headers())
            if response.status_code == 200:
                flash('Branch created successfully', 'success')
                return redirect(url_for('branches.index'))
            else:
                flash(response.json().get('detail', 'Error'), 'error')
        except Exception as e:
            flash(f'Error: {str(e)}', 'error')
    return render_template('branches/form.html', branch=None)

@branches_bp.route('/<int:branch_id>/edit', methods=['GET', 'POST'])
def edit(branch_id):
    if request.method == 'POST':
        data = {
            'name': request.form.get('name'),
            'address': request.form.get('address'),
            'city': request.form.get('city'),
            'state': request.form.get('state'),
            'phone': request.form.get('phone'),
            'email': request.form.get('email'),
            'is_active': request.form.get('is_active') == 'on'
        }
        try:
            response = requests.put(f'{API_BASE}/branches/{branch_id}', json=data, headers=get_headers())
            if response.status_code == 200:
                flash('Branch updated successfully', 'success')
                return redirect(url_for('branches.index'))
        except Exception as e:
            flash(f'Error: {str(e)}', 'error')
    try:
        response = requests.get(f'{API_BASE}/branches/{branch_id}', headers=get_headers())
        branch = response.json() if response.status_code == 200 else None
    except:
        branch = None
    return render_template('branches/form.html', branch=branch)
