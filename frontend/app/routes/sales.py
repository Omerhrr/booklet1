"""Sales Frontend Routes"""
from flask import Blueprint, render_template, request, redirect, url_for, flash, session
import requests
from datetime import datetime, timedelta
import logging

sales_bp = Blueprint('sales', __name__, url_prefix='/sales')
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

@sales_bp.route('/')
def index():
    try:
        response = requests.get(f'{API_BASE}/sales/invoices', headers=get_headers(), timeout=10)
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
    return render_template('sales/index.html', invoices=get_items(data))

@sales_bp.route('/create', methods=['GET', 'POST'])
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
                    'discount_percent': float(request.form.get(f'discount_{i}', 0)),
                    'vat_percent': 7.5
                })
        data = {
            'customer_id': int(request.form.get('customer_id', 0)),
            'invoice_date': request.form.get('invoice_date'),
            'due_date': request.form.get('due_date'),
            'items': items,
            'notes': request.form.get('notes'),
            'terms': request.form.get('terms'),
            'branch_id': session.get('branch_id', 1)
        }
        if not data['customer_id']:
            flash('Please select a customer', 'error')
        else:
            try:
                response = requests.post(f'{API_BASE}/sales/invoices', json=data, headers=get_headers(), timeout=10)
                if response.status_code in [200, 201]:
                    flash('Invoice created successfully', 'success')
                    return redirect(url_for('sales.index'))
                else:
                    flash(handle_error(response), 'error')
            except requests.exceptions.ConnectionError:
                flash('Cannot connect to server', 'error')
            except Exception as e:
                flash(f'Error: {str(e)}', 'error')
    
    customers, products = [], []
    try:
        r = requests.get(f'{API_BASE}/customers', headers=get_headers(), timeout=5)
        if r.status_code == 200: customers = get_items(r.json())
    except: pass
    try:
        r = requests.get(f'{API_BASE}/inventory/products', headers=get_headers(), timeout=5)
        if r.status_code == 200: products = get_items(r.json())
    except: pass
    
    today = datetime.now().strftime('%Y-%m-%d')
    due = (datetime.now() + timedelta(days=30)).strftime('%Y-%m-%d')
    return render_template('sales/create.html', customers=customers, products=products, today=today, due_date=due)

@sales_bp.route('/<int:invoice_id>')
def view(invoice_id):
    try:
        response = requests.get(f'{API_BASE}/sales/invoices/{invoice_id}', headers=get_headers(), timeout=10)
        invoice = response.json() if response.status_code == 200 else None
    except:
        invoice = None
    if not invoice:
        flash('Invoice not found', 'error')
        return redirect(url_for('sales.index'))
    return render_template('sales/view.html', invoice=invoice)

@sales_bp.route('/<int:invoice_id>/post', methods=['POST'])
def post_invoice(invoice_id):
    try:
        response = requests.post(f'{API_BASE}/sales/invoices/{invoice_id}/post', headers=get_headers(), timeout=10)
        if response.status_code == 200:
            flash('Invoice posted successfully', 'success')
        else:
            flash(handle_error(response), 'error')
    except requests.exceptions.ConnectionError:
        flash('Cannot connect to server', 'error')
    except Exception as e:
        flash(f'Error: {str(e)}', 'error')
    return redirect(url_for('sales.view', invoice_id=invoice_id))

@sales_bp.route('/<int:invoice_id>/delete', methods=['POST'])
def delete_invoice(invoice_id):
    try:
        response = requests.delete(f'{API_BASE}/sales/invoices/{invoice_id}', headers=get_headers(), timeout=10)
        if response.status_code == 200:
            flash('Invoice deleted successfully', 'success')
        else:
            flash(handle_error(response), 'error')
    except requests.exceptions.ConnectionError:
        flash('Cannot connect to server', 'error')
    except Exception as e:
        flash(f'Error: {str(e)}', 'error')
    return redirect(url_for('sales.index'))

@sales_bp.route('/credit-notes')
def credit_notes():
    try:
        response = requests.get(f'{API_BASE}/sales/credit-notes', headers=get_headers(), timeout=10)
        data = response.json() if response.status_code == 200 else []
    except:
        data = []
    return render_template('sales/credit_notes.html', credit_notes=get_items(data))

@sales_bp.route('/credit-notes/create', methods=['GET', 'POST'])
def create_credit_note():
    if request.method == 'POST':
        items = []
        for i in range(int(request.form.get('item_count', 0))):
            if request.form.get(f'description_{i}'):
                items.append({
                    'product_id': request.form.get(f'product_id_{i}') or None,
                    'description': request.form.get(f'description_{i}'),
                    'quantity': float(request.form.get(f'quantity_{i}', 1)),
                    'unit_price': float(request.form.get(f'unit_price_{i}', 0))
                })
        data = {
            'customer_id': int(request.form.get('customer_id', 0)),
            'sales_invoice_id': request.form.get('invoice_id') or None,
            'credit_note_date': request.form.get('credit_note_date'),
            'items': items,
            'reason': request.form.get('reason'),
            'branch_id': session.get('branch_id', 1)
        }
        if not data['customer_id']:
            flash('Please select a customer', 'error')
        else:
            try:
                response = requests.post(f'{API_BASE}/sales/credit-notes', json=data, headers=get_headers(), timeout=10)
                if response.status_code in [200, 201]:
                    flash('Credit note created successfully', 'success')
                    return redirect(url_for('sales.credit_notes'))
                else:
                    flash(handle_error(response), 'error')
            except requests.exceptions.ConnectionError:
                flash('Cannot connect to server', 'error')
            except Exception as e:
                flash(f'Error: {str(e)}', 'error')
    
    customers = []
    try:
        r = requests.get(f'{API_BASE}/customers', headers=get_headers(), timeout=5)
        if r.status_code == 200: customers = get_items(r.json())
    except: pass
    
    return render_template('sales/credit_note_form.html', customers=customers)
