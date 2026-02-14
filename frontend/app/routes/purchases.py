"""Purchases Frontend Routes"""
from flask import Blueprint, render_template, request, redirect, url_for, flash, session
import requests
from datetime import datetime, timedelta
import logging

purchases_bp = Blueprint('purchases', __name__, url_prefix='/purchases')
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

@purchases_bp.route('/')
def index():
    try:
        response = requests.get(f'{API_BASE}/purchases/bills', headers=get_headers(), timeout=10)
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
    return render_template('purchases/index.html', bills=get_items(data))

@purchases_bp.route('/create', methods=['GET', 'POST'])
def create():
    if request.method == 'POST':
        items = []
        for i in range(int(request.form.get('item_count', 0))):
            if request.form.get(f'description_{i}'):
                items.append({
                    'product_id': request.form.get(f'product_id_{i}') or None,
                    'description': request.form.get(f'description_{i}'),
                    'quantity': float(request.form.get(f'quantity_{i}', 1)),
                    'unit_price': float(request.form.get(f'unit_price_{i}', 0)),
                    'vat_percent': float(request.form.get(f'vat_{i}', 7.5))
                })
        data = {
            'vendor_id': int(request.form.get('vendor_id', 0)),
            'bill_date': request.form.get('bill_date'),
            'due_date': request.form.get('due_date'),
            'items': items,
            'reference': request.form.get('reference'),
            'notes': request.form.get('notes'),
            'branch_id': session.get('branch_id', 1)
        }
        if not data['vendor_id']:
            flash('Please select a vendor', 'error')
        else:
            try:
                response = requests.post(f'{API_BASE}/purchases/bills', json=data, headers=get_headers(), timeout=10)
                if response.status_code in [200, 201]:
                    flash('Purchase bill created successfully', 'success')
                    return redirect(url_for('purchases.index'))
                else:
                    flash(handle_error(response), 'error')
            except requests.exceptions.ConnectionError:
                flash('Cannot connect to server', 'error')
            except Exception as e:
                flash(f'Error: {str(e)}', 'error')
    
    vendors, products = [], []
    try:
        r = requests.get(f'{API_BASE}/vendors', headers=get_headers(), timeout=5)
        if r.status_code == 200: vendors = get_items(r.json())
    except: pass
    try:
        r = requests.get(f'{API_BASE}/inventory/products', headers=get_headers(), timeout=5)
        if r.status_code == 200: products = get_items(r.json())
    except: pass
    
    today = datetime.now().strftime('%Y-%m-%d')
    due = (datetime.now() + timedelta(days=30)).strftime('%Y-%m-%d')
    return render_template('purchases/create.html', vendors=vendors, products=products, today=today, due_date=due)

@purchases_bp.route('/<int:bill_id>')
def view(bill_id):
    try:
        response = requests.get(f'{API_BASE}/purchases/bills/{bill_id}', headers=get_headers(), timeout=10)
        bill = response.json() if response.status_code == 200 else None
    except:
        bill = None
    if not bill:
        flash('Purchase bill not found', 'error')
        return redirect(url_for('purchases.index'))
    return render_template('purchases/view.html', bill=bill)

@purchases_bp.route('/<int:bill_id>/post', methods=['POST'])
def post_bill(bill_id):
    try:
        response = requests.post(f'{API_BASE}/purchases/bills/{bill_id}/post', headers=get_headers(), timeout=10)
        if response.status_code == 200:
            flash('Bill posted successfully', 'success')
        else:
            flash(handle_error(response), 'error')
    except requests.exceptions.ConnectionError:
        flash('Cannot connect to server', 'error')
    except Exception as e:
        flash(f'Error: {str(e)}', 'error')
    return redirect(url_for('purchases.view', bill_id=bill_id))

@purchases_bp.route('/<int:bill_id>/delete', methods=['POST'])
def delete_bill(bill_id):
    try:
        response = requests.delete(f'{API_BASE}/purchases/bills/{bill_id}', headers=get_headers(), timeout=10)
        if response.status_code == 200:
            flash('Bill deleted successfully', 'success')
        else:
            flash(handle_error(response), 'error')
    except requests.exceptions.ConnectionError:
        flash('Cannot connect to server', 'error')
    except Exception as e:
        flash(f'Error: {str(e)}', 'error')
    return redirect(url_for('purchases.index'))
