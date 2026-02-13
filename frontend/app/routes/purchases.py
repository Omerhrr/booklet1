"""
Purchases Frontend Routes
"""
from flask import Blueprint, render_template, request, redirect, url_for, flash, session
import requests
from datetime import datetime, timedelta

purchases_bp = Blueprint('purchases', __name__, url_prefix='/purchases')

API_BASE = 'http://localhost:8000/api/v1'


def get_headers():
    token = session.get('access_token')
    return {'Authorization': f'Bearer {token}'} if token else {}


@purchases_bp.route('/')
def index():
    """Purchase bills list"""
    try:
        response = requests.get(f'{API_BASE}/purchases/bills', headers=get_headers())
        bills = response.json() if response.status_code == 200 else {'items': []}
    except:
        bills = {'items': []}

    return render_template('purchases/index.html', bills=bills)


@purchases_bp.route('/create', methods=['GET', 'POST'])
def create():
    """Create new purchase bill"""
    if request.method == 'POST':
        items = []
        for i in range(int(request.form.get('item_count', 0))):
            description = request.form.get(f'description_{i}')
            if description:
                items.append({
                    'product_id': request.form.get(f'product_id_{i}'),
                    'description': description,
                    'quantity': float(request.form.get(f'quantity_{i}', 1)),
                    'unit_price': float(request.form.get(f'unit_price_{i}', 0)),
                    'vat_percent': float(request.form.get(f'vat_{i}', 7.5))
                })

        data = {
            'vendor_id': int(request.form.get('vendor_id')),
            'bill_date': request.form.get('bill_date'),
            'due_date': request.form.get('due_date'),
            'items': items,
            'reference': request.form.get('reference'),
            'notes': request.form.get('notes'),
            'branch_id': session.get('branch_id', 1)
        }

        try:
            response = requests.post(
                f'{API_BASE}/purchases/bills',
                json=data,
                headers=get_headers()
            )
            if response.status_code == 200:
                flash('Purchase bill created successfully', 'success')
                return redirect(url_for('purchases.index'))
            else:
                flash(response.json().get('detail', 'Error creating bill'), 'error')
        except Exception as e:
            flash(f'Error: {str(e)}', 'error')

    # Get vendors and products
    try:
        vendors_resp = requests.get(f'{API_BASE}/vendors', headers=get_headers())
        vendors = vendors_resp.json() if vendors_resp.status_code == 200 else {'items': []}
    except:
        vendors = {'items': []}

    try:
        products_resp = requests.get(f'{API_BASE}/inventory/products', headers=get_headers())
        products = products_resp.json() if products_resp.status_code == 200 else {'items': []}
    except:
        products = {'items': []}

    today = datetime.now().strftime('%Y-%m-%d')
    due = (datetime.now() + timedelta(days=30)).strftime('%Y-%m-%d')

    return render_template('purchases/create.html', vendors=vendors.get('items', []), products=products.get('items', []),  today=today, due_date=due)


@purchases_bp.route('/<int:bill_id>')
def view(bill_id):
    """View purchase bill details"""
    try:
        response = requests.get(f'{API_BASE}/purchases/bills/{bill_id}', headers=get_headers())
        bill = response.json() if response.status_code == 200 else None
    except:
        bill = None

    if not bill:
        flash('Purchase bill not found', 'error')
        return redirect(url_for('purchases.index'))

    return render_template('purchases/view.html', bill=bill)


@purchases_bp.route('/<int:bill_id>/post', methods=['POST'])
def post_bill(bill_id):
    """Post purchase bill to ledger"""
    try:
        response = requests.post(
            f'{API_BASE}/purchases/bills/{bill_id}/post',
            headers=get_headers()
        )
        if response.status_code == 200:
            flash('Bill posted successfully', 'success')
        else:
            flash(response.json().get('detail', 'Error posting bill'), 'error')
    except Exception as e:
        flash(f'Error: {str(e)}', 'error')

    return redirect(url_for('purchases.view', bill_id=bill_id))


@purchases_bp.route('/<int:bill_id>/delete', methods=['POST'])
def delete_bill(bill_id):
    """Delete purchase bill"""
    try:
        response = requests.delete(
            f'{API_BASE}/purchases/bills/{bill_id}',
            headers=get_headers()
        )
        if response.status_code == 200:
            flash('Bill deleted successfully', 'success')
        else:
            flash(response.json().get('detail', 'Error deleting bill'), 'error')
    except Exception as e:
        flash(f'Error: {str(e)}', 'error')

    return redirect(url_for('purchases.index'))
