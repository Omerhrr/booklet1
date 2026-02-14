"""Customers Frontend Routes"""
from flask import Blueprint, render_template, request, redirect, url_for, flash, session
import requests
import logging

customers_bp = Blueprint('customers', __name__, url_prefix='/customers')
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

@customers_bp.route('/')
def index():
    search = request.args.get('search', '')
    params = {'search': search} if search else {}
    try:
        response = requests.get(f'{API_BASE}/customers', params=params, headers=get_headers(), timeout=10)
        if response.status_code == 200:
            data = response.json()
        elif response.status_code == 401:
            flash('Please login again', 'error')
            return redirect('/login')
        else:
            flash(handle_error(response), 'error')
            data = []
    except requests.exceptions.ConnectionError:
        flash('Cannot connect to server. Is the backend running?', 'error')
        data = []
    except Exception as e:
        flash(f'Error: {str(e)}', 'error')
        data = []
    return render_template('customers/index.html', customers=get_items(data), search=search)

@customers_bp.route('/create', methods=['GET', 'POST'])
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
            'credit_limit': float(request.form.get('credit_limit', 0)) if request.form.get('credit_limit') else None,
            'payment_terms': request.form.get('payment_terms', 'Net 30')
        }
        if not data['name']:
            flash('Customer name is required', 'error')
            return render_template('customers/form.html', customer=None)
        try:
            response = requests.post(f'{API_BASE}/customers', json=data, headers=get_headers(), timeout=10)
            if response.status_code in [200, 201]:
                flash('Customer created successfully', 'success')
                return redirect(url_for('customers.index'))
            elif response.status_code == 401:
                flash('Please login again', 'error')
                return redirect('/login')
            else:
                flash(handle_error(response), 'error')
        except requests.exceptions.ConnectionError:
            flash('Cannot connect to server', 'error')
        except Exception as e:
            flash(f'Error: {str(e)}', 'error')
    return render_template('customers/form.html', customer=None)

@customers_bp.route('/<int:customer_id>')
def view(customer_id):
    try:
        response = requests.get(f'{API_BASE}/customers/{customer_id}', headers=get_headers(), timeout=10)
        customer = response.json() if response.status_code == 200 else None
    except:
        customer = None
    if not customer:
        flash('Customer not found', 'error')
        return redirect(url_for('customers.index'))
    return render_template('customers/view.html', customer=customer)

@customers_bp.route('/<int:customer_id>/edit', methods=['GET', 'POST'])
def edit(customer_id):
    if request.method == 'POST':
        data = {
            'name': request.form.get('name', '').strip(),
            'email': request.form.get('email', '').strip() or None,
            'phone': request.form.get('phone', '').strip() or None,
            'address': request.form.get('address', '').strip() or None,
            'city': request.form.get('city', '').strip() or None,
            'state': request.form.get('state', '').strip() or None,
            'contact_person': request.form.get('contact_person', '').strip() or None,
            'credit_limit': float(request.form.get('credit_limit', 0)) if request.form.get('credit_limit') else None,
            'payment_terms': request.form.get('payment_terms'),
            'is_active': request.form.get('is_active') == 'on'
        }
        try:
            response = requests.put(f'{API_BASE}/customers/{customer_id}', json=data, headers=get_headers(), timeout=10)
            if response.status_code == 200:
                flash('Customer updated successfully', 'success')
                return redirect(url_for('customers.index'))
            elif response.status_code == 401:
                flash('Please login again', 'error')
                return redirect('/login')
            else:
                flash(handle_error(response), 'error')
        except requests.exceptions.ConnectionError:
            flash('Cannot connect to server', 'error')
        except Exception as e:
            flash(f'Error: {str(e)}', 'error')
    
    try:
        response = requests.get(f'{API_BASE}/customers/{customer_id}', headers=get_headers(), timeout=10)
        customer = response.json() if response.status_code == 200 else None
    except:
        customer = None
    
    return render_template('customers/form.html', customer=customer)

@customers_bp.route('/<int:customer_id>/delete', methods=['POST'])
def delete(customer_id):
    try:
        response = requests.delete(f'{API_BASE}/customers/{customer_id}', headers=get_headers(), timeout=10)
        if response.status_code == 200:
            flash('Customer deleted successfully', 'success')
        elif response.status_code == 401:
            flash('Please login again', 'error')
            return redirect('/login')
        else:
            flash(handle_error(response), 'error')
    except requests.exceptions.ConnectionError:
        flash('Cannot connect to server', 'error')
    except Exception as e:
        flash(f'Error: {str(e)}', 'error')
    return redirect(url_for('customers.index'))
