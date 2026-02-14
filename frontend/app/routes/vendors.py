"""Vendors Frontend Routes"""
from flask import Blueprint, render_template, request, redirect, url_for, flash, session
import requests
import logging

vendors_bp = Blueprint('vendors', __name__, url_prefix='/vendors')
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

@vendors_bp.route('/')
def index():
    search = request.args.get('search', '')
    params = {'search': search} if search else {}
    try:
        response = requests.get(f'{API_BASE}/vendors', params=params, headers=get_headers(), timeout=10)
        if response.status_code == 200:
            data = response.json()
        elif response.status_code == 401:
            flash('Please login again', 'error')
            return redirect('/login')
        else:
            data = []
    except requests.exceptions.ConnectionError:
        flash('Cannot connect to server. Is the backend running?', 'error')
        data = []
    except: data = []
    return render_template('vendors/index.html', vendors=get_items(data), search=search)

@vendors_bp.route('/create', methods=['GET', 'POST'])
def create():
    if request.method == 'POST':
        data = {
            'name': request.form.get('name', '').strip(),
            'email': request.form.get('email', '').strip() or None,
            'phone': request.form.get('phone', '').strip() or None,
            'address': request.form.get('address', '').strip() or None,
            'city': request.form.get('city', '').strip() or None,
            'state': request.form.get('state', '').strip() or None,
            'tax_id': request.form.get('tax_id', '').strip() or None,
            'contact_person': request.form.get('contact_person', '').strip() or None,
            'payment_terms': request.form.get('payment_terms', 'Net 30'),
            'bank_name': request.form.get('bank_name', '').strip() or None,
            'bank_account': request.form.get('bank_account', '').strip() or None
        }
        if not data['name']:
            flash('Vendor name is required', 'error')
            return render_template('vendors/form.html', vendor=None)
        try:
            response = requests.post(f'{API_BASE}/vendors', json=data, headers=get_headers(), timeout=10)
            if response.status_code in [200, 201]:
                flash('Vendor created successfully', 'success')
                return redirect(url_for('vendors.index'))
            else:
                flash(handle_error(response), 'error')
        except requests.exceptions.ConnectionError:
            flash('Cannot connect to server', 'error')
        except Exception as e:
            flash(f'Error: {str(e)}', 'error')
    return render_template('vendors/form.html', vendor=None)

@vendors_bp.route('/<int:vendor_id>/edit', methods=['GET', 'POST'])
def edit(vendor_id):
    if request.method == 'POST':
        data = {
            'name': request.form.get('name', '').strip(),
            'email': request.form.get('email', '').strip() or None,
            'phone': request.form.get('phone', '').strip() or None,
            'address': request.form.get('address', '').strip() or None,
            'city': request.form.get('city', '').strip() or None,
            'state': request.form.get('state', '').strip() or None,
            'contact_person': request.form.get('contact_person', '').strip() or None,
            'payment_terms': request.form.get('payment_terms'),
            'bank_name': request.form.get('bank_name', '').strip() or None,
            'bank_account': request.form.get('bank_account', '').strip() or None,
            'is_active': request.form.get('is_active') == 'on'
        }
        try:
            response = requests.put(f'{API_BASE}/vendors/{vendor_id}', json=data, headers=get_headers(), timeout=10)
            if response.status_code == 200:
                flash('Vendor updated successfully', 'success')
                return redirect(url_for('vendors.index'))
            else:
                flash(handle_error(response), 'error')
        except requests.exceptions.ConnectionError:
            flash('Cannot connect to server', 'error')
        except Exception as e:
            flash(f'Error: {str(e)}', 'error')
    
    try:
        response = requests.get(f'{API_BASE}/vendors/{vendor_id}', headers=get_headers(), timeout=10)
        vendor = response.json() if response.status_code == 200 else None
    except:
        vendor = None
    return render_template('vendors/form.html', vendor=vendor)

@vendors_bp.route('/<int:vendor_id>/delete', methods=['POST'])
def delete(vendor_id):
    try:
        response = requests.delete(f'{API_BASE}/vendors/{vendor_id}', headers=get_headers(), timeout=10)
        if response.status_code == 200:
            flash('Vendor deleted successfully', 'success')
        else:
            flash(handle_error(response), 'error')
    except requests.exceptions.ConnectionError:
        flash('Cannot connect to server', 'error')
    except Exception as e:
        flash(f'Error: {str(e)}', 'error')
    return redirect(url_for('vendors.index'))
