"""
Vendors Frontend Routes
"""
from flask import Blueprint, render_template, request, redirect, url_for, flash, session
import requests

vendors_bp = Blueprint('vendors', __name__, url_prefix='/vendors')

API_BASE = 'http://localhost:8000/api/v1'


def get_headers():
    token = session.get('access_token')
    return {'Authorization': f'Bearer {token}'} if token else {}


def get_items(data):
    if data is None:
        return []
    if isinstance(data, list):
        return data
    if isinstance(data, dict):
        return data.get('items', [])
    return []


@vendors_bp.route('/')
def index():
    """Vendors list"""
    search = request.args.get('search', '')
    params = {}
    if search:
        params['search'] = search
    try:
        response = requests.get(f'{API_BASE}/vendors', params=params, headers=get_headers())
        data = response.json() if response.status_code == 200 else []
    except:
        data = []
    return render_template('vendors/index.html', vendors=get_items(data), search=search)


@vendors_bp.route('/create', methods=['GET', 'POST'])
def create():
    """Create new vendor"""
    if request.method == 'POST':
        data = {
            'name': request.form.get('name'),
            'email': request.form.get('email'),
            'phone': request.form.get('phone'),
            'address': request.form.get('address'),
            'city': request.form.get('city'),
            'state': request.form.get('state'),
            'tax_id': request.form.get('tax_id'),
            'contact_person': request.form.get('contact_person'),
            'payment_terms': request.form.get('payment_terms', 'Net 30'),
            'bank_name': request.form.get('bank_name'),
            'bank_account': request.form.get('bank_account')
        }
        try:
            response = requests.post(f'{API_BASE}/vendors', json=data, headers=get_headers())
            if response.status_code == 200:
                flash('Vendor created successfully', 'success')
                return redirect(url_for('vendors.index'))
            else:
                flash(response.json().get('detail', 'Error'), 'error')
        except Exception as e:
            flash(f'Error: {str(e)}', 'error')
    return render_template('vendors/form.html', vendor=None)


@vendors_bp.route('/<int:vendor_id>/edit', methods=['GET', 'POST'])
def edit(vendor_id):
    """Edit vendor"""
    if request.method == 'POST':
        data = {
            'name': request.form.get('name'),
            'email': request.form.get('email'),
            'phone': request.form.get('phone'),
            'address': request.form.get('address'),
            'city': request.form.get('city'),
            'state': request.form.get('state'),
            'contact_person': request.form.get('contact_person'),
            'payment_terms': request.form.get('payment_terms'),
            'bank_name': request.form.get('bank_name'),
            'bank_account': request.form.get('bank_account'),
            'is_active': request.form.get('is_active') == 'on'
        }
        try:
            response = requests.put(f'{API_BASE}/vendors/{vendor_id}', json=data, headers=get_headers())
            if response.status_code == 200:
                flash('Vendor updated successfully', 'success')
                return redirect(url_for('vendors.index'))
        except Exception as e:
            flash(f'Error: {str(e)}', 'error')
    try:
        response = requests.get(f'{API_BASE}/vendors/{vendor_id}', headers=get_headers())
        vendor = response.json() if response.status_code == 200 else None
    except:
        vendor = None
    return render_template('vendors/form.html', vendor=vendor)


@vendors_bp.route('/<int:vendor_id>/delete', methods=['POST'])
def delete(vendor_id):
    """Delete vendor"""
    try:
        response = requests.delete(f'{API_BASE}/vendors/{vendor_id}', headers=get_headers())
        if response.status_code == 200:
            flash('Vendor deleted successfully', 'success')
        else:
            flash(response.json().get('detail', 'Error'), 'error')
    except Exception as e:
        flash(f'Error: {str(e)}', 'error')
    return redirect(url_for('vendors.index'))
