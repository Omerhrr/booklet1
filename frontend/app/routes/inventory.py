"""Inventory Frontend Routes"""
from flask import Blueprint, render_template, request, redirect, url_for, flash, session
import requests
from datetime import datetime
import logging

inventory_bp = Blueprint('inventory', __name__, url_prefix='/inventory')
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

@inventory_bp.route('/')
def index():
    search = request.args.get('search', '')
    low_stock = request.args.get('low_stock', '')
    params = {}
    if search: params['search'] = search
    if low_stock: params['low_stock'] = True
    try:
        response = requests.get(f'{API_BASE}/inventory/products', params=params, headers=get_headers(), timeout=10)
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
    return render_template('inventory/index.html', products=get_items(data), search=search)

@inventory_bp.route('/create', methods=['GET', 'POST'])
def create():
    if request.method == 'POST':
        data = {
            'name': request.form.get('name', '').strip(),
            'sku': request.form.get('sku', '').strip(),
            'barcode': request.form.get('barcode', '').strip() or None,
            'category_id': request.form.get('category_id') or None,
            'description': request.form.get('description', '').strip() or None,
            'unit': request.form.get('unit', 'pcs'),
            'purchase_price': float(request.form.get('purchase_price', 0)),
            'sales_price': float(request.form.get('sales_price', 0)),
            'opening_stock': float(request.form.get('opening_stock', 0)),
            'reorder_point': float(request.form.get('reorder_point', 0)) if request.form.get('reorder_point') else None,
            'track_inventory': request.form.get('track_inventory') == 'on',
            'branch_id': session.get('branch_id', 1)
        }
        if not all([data['name'], data['sku']]):
            flash('Product name and SKU are required', 'error')
        else:
            try:
                response = requests.post(f'{API_BASE}/inventory/products', json=data, headers=get_headers(), timeout=10)
                if response.status_code in [200, 201]:
                    flash('Product created successfully', 'success')
                    return redirect(url_for('inventory.index'))
                else:
                    flash(handle_error(response), 'error')
            except requests.exceptions.ConnectionError:
                flash('Cannot connect to server', 'error')
            except Exception as e:
                flash(f'Error: {str(e)}', 'error')
    
    categories = []
    try:
        r = requests.get(f'{API_BASE}/inventory/categories', headers=get_headers(), timeout=5)
        if r.status_code == 200: categories = get_items(r.json())
    except: pass
    
    return render_template('inventory/product_form.html', product=None, categories=categories)

@inventory_bp.route('/<int:product_id>/edit', methods=['GET', 'POST'])
def edit(product_id):
    if request.method == 'POST':
        data = {
            'name': request.form.get('name', '').strip(),
            'sku': request.form.get('sku', '').strip(),
            'barcode': request.form.get('barcode', '').strip() or None,
            'category_id': request.form.get('category_id') or None,
            'description': request.form.get('description', '').strip() or None,
            'unit': request.form.get('unit'),
            'purchase_price': float(request.form.get('purchase_price', 0)),
            'sales_price': float(request.form.get('sales_price', 0)),
            'reorder_point': float(request.form.get('reorder_point', 0)) if request.form.get('reorder_point') else None,
            'track_inventory': request.form.get('track_inventory') == 'on',
            'is_active': request.form.get('is_active') == 'on'
        }
        try:
            response = requests.put(f'{API_BASE}/inventory/products/{product_id}', json=data, headers=get_headers(), timeout=10)
            if response.status_code == 200:
                flash('Product updated successfully', 'success')
                return redirect(url_for('inventory.index'))
            else:
                flash(handle_error(response), 'error')
        except requests.exceptions.ConnectionError:
            flash('Cannot connect to server', 'error')
        except Exception as e:
            flash(f'Error: {str(e)}', 'error')
    
    product, categories = None, []
    try:
        r = requests.get(f'{API_BASE}/inventory/products/{product_id}', headers=get_headers(), timeout=5)
        if r.status_code == 200: product = r.json()
    except: pass
    try:
        r = requests.get(f'{API_BASE}/inventory/categories', headers=get_headers(), timeout=5)
        if r.status_code == 200: categories = get_items(r.json())
    except: pass
    
    return render_template('inventory/product_form.html', product=product, categories=categories)

@inventory_bp.route('/<int:product_id>/delete', methods=['POST'])
def delete(product_id):
    try:
        response = requests.delete(f'{API_BASE}/inventory/products/{product_id}', headers=get_headers(), timeout=10)
        if response.status_code == 200:
            flash('Product deleted successfully', 'success')
        else:
            flash(handle_error(response), 'error')
    except requests.exceptions.ConnectionError:
        flash('Cannot connect to server', 'error')
    except Exception as e:
        flash(f'Error: {str(e)}', 'error')
    return redirect(url_for('inventory.index'))

@inventory_bp.route('/categories')
def categories():
    try:
        response = requests.get(f'{API_BASE}/inventory/categories', headers=get_headers(), timeout=10)
        data = response.json() if response.status_code == 200 else []
    except:
        data = []
    return render_template('inventory/categories.html', categories=get_items(data))

@inventory_bp.route('/categories/create', methods=['POST'])
def create_category():
    data = {
        'name': request.form.get('name', '').strip(),
        'description': request.form.get('description', '').strip() or None
    }
    if not data['name']:
        flash('Category name is required', 'error')
    else:
        try:
            response = requests.post(f'{API_BASE}/inventory/categories', json=data, headers=get_headers(), timeout=10)
            if response.status_code in [200, 201]:
                flash('Category created', 'success')
            else:
                flash(handle_error(response), 'error')
        except requests.exceptions.ConnectionError:
            flash('Cannot connect to server', 'error')
        except Exception as e:
            flash(f'Error: {str(e)}', 'error')
    return redirect(url_for('inventory.categories'))

@inventory_bp.route('/adjustments')
def adjustments():
    try:
        response = requests.get(f'{API_BASE}/inventory/stock-adjustments', headers=get_headers(), timeout=10)
        data = response.json() if response.status_code == 200 else []
    except:
        data = []
    return render_template('inventory/adjustments.html', adjustments=get_items(data))

@inventory_bp.route('/adjustments/create', methods=['GET', 'POST'])
def create_adjustment():
    if request.method == 'POST':
        data = {
            'product_id': int(request.form.get('product_id', 0)),
            'quantity_change': float(request.form.get('quantity_change', 0)),
            'reason': request.form.get('reason', '').strip(),
            'adjustment_type': request.form.get('adjustment_type', 'manual')
        }
        if not data['product_id']:
            flash('Please select a product', 'error')
        else:
            try:
                response = requests.post(f'{API_BASE}/inventory/stock-adjustments', json=data, headers=get_headers(), timeout=10)
                if response.status_code in [200, 201]:
                    flash('Stock adjusted successfully', 'success')
                    return redirect(url_for('inventory.adjustments'))
                else:
                    flash(handle_error(response), 'error')
            except requests.exceptions.ConnectionError:
                flash('Cannot connect to server', 'error')
            except Exception as e:
                flash(f'Error: {str(e)}', 'error')
    
    products = []
    try:
        r = requests.get(f'{API_BASE}/inventory/products', headers=get_headers(), timeout=5)
        if r.status_code == 200: products = get_items(r.json())
    except: pass
    
    return render_template('inventory/adjustment_form.html', products=products)
