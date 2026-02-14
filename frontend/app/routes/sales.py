"""
Sales Frontend Routes
"""
from flask import Blueprint, render_template, request, redirect, url_for, flash, session, jsonify
import requests
from datetime import datetime, timedelta

sales_bp = Blueprint('sales', __name__, url_prefix='/sales')

API_BASE = 'http://localhost:8000/api/v1'


def get_headers():
    token = session.get('access_token')
    return {'Authorization': f'Bearer {token}'} if token else {}


def get_items(data):
    """Extract items from API response - handles both list and dict responses"""
    if data is None:
        return []
    if isinstance(data, list):
        return data
    if isinstance(data, dict):
        return data.get('items', [])
    return []


@sales_bp.route('/')
def index():
    """Sales invoices list"""
    try:
        response = requests.get(f'{API_BASE}/sales/invoices', headers=get_headers())
        data = response.json() if response.status_code == 200 else []
    except:
        data = []

    return render_template('sales/index.html', invoices=get_items(data))


@sales_bp.route('/create', methods=['GET', 'POST'])
def create():
    """Create new invoice"""
    if request.method == 'POST':
        # Build items list
        items = []
        for i in range(int(request.form.get('item_count', 0))):
            description = request.form.get(f'description_{i}')
            if description:
                items.append({
                    'product_id': request.form.get(f'product_id_{i}'),
                    'description': description,
                    'quantity': float(request.form.get(f'quantity_{i}', 1)),
                    'unit_price': float(request.form.get(f'unit_price_{i}', 0)),
                    'discount_percent': float(request.form.get(f'discount_{i}', 0)),
                    'vat_percent': 7.5
                })

        data = {
            'customer_id': int(request.form.get('customer_id')),
            'invoice_date': request.form.get('invoice_date'),
            'due_date': request.form.get('due_date'),
            'items': items,
            'notes': request.form.get('notes'),
            'terms': request.form.get('terms'),
            'branch_id': session.get('branch_id', 1)
        }

        try:
            response = requests.post(
                f'{API_BASE}/sales/invoices',
                json=data,
                headers=get_headers()
            )
            if response.status_code == 200:
                flash('Invoice created successfully', 'success')
                return redirect(url_for('sales.index'))
            else:
                flash(response.json().get('detail', 'Error creating invoice'), 'error')
        except Exception as e:
            flash(f'Error: {str(e)}', 'error')

    # Get customers and products for dropdowns
    try:
        customers_resp = requests.get(f'{API_BASE}/customers', headers=get_headers())
        customers_data = customers_resp.json() if customers_resp.status_code == 200 else []
    except:
        customers_data = []

    try:
        products_resp = requests.get(f'{API_BASE}/inventory/products', headers=get_headers())
        products_data = products_resp.json() if products_resp.status_code == 200 else []
    except:
        products_data = []

    today = datetime.now().strftime('%Y-%m-%d')
    due = (datetime.now() + timedelta(days=30)).strftime('%Y-%m-%d')

    return render_template('sales/create.html', customers=get_items(customers_data), products=get_items(products_data), today=today, due_date=due)


@sales_bp.route('/<int:invoice_id>')
def view(invoice_id):
    """View invoice details"""
    try:
        response = requests.get(f'{API_BASE}/sales/invoices/{invoice_id}', headers=get_headers())
        invoice = response.json() if response.status_code == 200 else None
    except:
        invoice = None

    if not invoice:
        flash('Invoice not found', 'error')
        return redirect(url_for('sales.index'))

    return render_template('sales/view.html', invoice=invoice)


@sales_bp.route('/<int:invoice_id>/post', methods=['POST'])
def post_invoice(invoice_id):
    """Post invoice to ledger"""
    try:
        response = requests.post(
            f'{API_BASE}/sales/invoices/{invoice_id}/post',
            headers=get_headers()
        )
        if response.status_code == 200:
            flash('Invoice posted successfully', 'success')
        else:
            flash(response.json().get('detail', 'Error posting invoice'), 'error')
    except Exception as e:
        flash(f'Error: {str(e)}', 'error')

    return redirect(url_for('sales.view', invoice_id=invoice_id))


@sales_bp.route('/<int:invoice_id>/delete', methods=['POST'])
def delete_invoice(invoice_id):
    """Delete invoice"""
    try:
        response = requests.delete(
            f'{API_BASE}/sales/invoices/{invoice_id}',
            headers=get_headers()
        )
        if response.status_code == 200:
            flash('Invoice deleted successfully', 'success')
        else:
            flash(response.json().get('detail', 'Error deleting invoice'), 'error')
    except Exception as e:
        flash(f'Error: {str(e)}', 'error')

    return redirect(url_for('sales.index'))


@sales_bp.route('/credit-notes')
def credit_notes():
    """Credit notes list"""
    try:
        response = requests.get(f'{API_BASE}/sales/credit-notes', headers=get_headers())
        data = response.json() if response.status_code == 200 else []
    except:
        data = []

    return render_template('sales/credit_notes.html', credit_notes=get_items(data))


@sales_bp.route('/credit-notes/create', methods=['GET', 'POST'])
def create_credit_note():
    """Create credit note"""
    if request.method == 'POST':
        items = []
        for i in range(int(request.form.get('item_count', 0))):
            description = request.form.get(f'description_{i}')
            if description:
                items.append({
                    'product_id': request.form.get(f'product_id_{i}'),
                    'description': description,
                    'quantity': float(request.form.get(f'quantity_{i}', 1)),
                    'unit_price': float(request.form.get(f'unit_price_{i}', 0))
                })

        data = {
            'customer_id': int(request.form.get('customer_id')),
            'sales_invoice_id': request.form.get('invoice_id'),
            'credit_note_date': request.form.get('credit_note_date'),
            'items': items,
            'reason': request.form.get('reason'),
            'branch_id': session.get('branch_id', 1)
        }

        try:
            response = requests.post(
                f'{API_BASE}/sales/credit-notes',
                json=data,
                headers=get_headers()
            )
            if response.status_code == 200:
                flash('Credit note created successfully', 'success')
                return redirect(url_for('sales.credit_notes'))
        except Exception as e:
            flash(f'Error: {str(e)}', 'error')

    # Get customers for dropdown
    try:
        customers_resp = requests.get(f'{API_BASE}/customers', headers=get_headers())
        customers_data = customers_resp.json() if customers_resp.status_code == 200 else []
    except:
        customers_data = []

    return render_template('sales/credit_note_form.html', customers=get_items(customers_data))
