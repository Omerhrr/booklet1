"""
Inventory Frontend Routes
"""
from flask import Blueprint, render_template, request, redirect, url_for, flash, session
import requests
from datetime import datetime

inventory_bp = Blueprint('inventory', __name__, url_prefix='/inventory')

API_BASE = 'http://localhost:8000/api/v1'


def get_headers():
    token = session.get('access_token')
    return {'Authorization': f'Bearer {token}'} if token else {}


@inventory_bp.route('/')
def index():
    """Products list"""
    search = request.args.get('search', '')
    low_stock = request.args.get('low_stock', '')

    params = {}
    if search:
        params['search'] = search
    if low_stock:
        params['low_stock'] = True

    try:
        response = requests.get(
            f'{API_BASE}/inventory/products',
            params=params,
            headers=get_headers()
        )
        products = response.json() if response.status_code == 200 else {'items': []}
    except:
        products = {'items': []}

    return render_template('inventory/index.html', products=products.get('items', []), search=search)


@inventory_bp.route('/create', methods=['GET', 'POST'])
def create():
    """Create new product"""
    if request.method == 'POST':
        data = {
            'name': request.form.get('name'),
            'sku': request.form.get('sku'),
            'barcode': request.form.get('barcode'),
            'category_id': request.form.get('category_id'),
            'description': request.form.get('description'),
            'unit': request.form.get('unit', 'pcs'),
            'purchase_price': float(request.form.get('purchase_price', 0)),
            'sales_price': float(request.form.get('sales_price', 0)),
            'opening_stock': float(request.form.get('opening_stock', 0)),
            'reorder_point': float(request.form.get('reorder_point', 0)) if request.form.get('reorder_point') else None,
            'track_inventory': request.form.get('track_inventory') == 'on',
            'branch_id': session.get('branch_id', 1)
        }

        try:
            response = requests.post(
                f'{API_BASE}/inventory/products',
                json=data,
                headers=get_headers()
            )
            if response.status_code == 200:
                flash('Product created successfully', 'success')
                return redirect(url_for('inventory.index'))
            else:
                flash(response.json().get('detail', 'Error creating product'), 'error')
        except Exception as e:
            flash(f'Error: {str(e)}', 'error')

    # Get categories
    try:
        categories_resp = requests.get(f'{API_BASE}/inventory/categories', headers=get_headers())
        categories = categories_resp.json() if categories_resp.status_code == 200 else {'items': []}
    except:
        categories = {'items': []}

    return render_template('inventory/product_form.html', product=None, categories=categories)


@inventory_bp.route('/<int:product_id>/edit', methods=['GET', 'POST'])
def edit(product_id):
    """Edit product"""
    if request.method == 'POST':
        data = {
            'name': request.form.get('name'),
            'sku': request.form.get('sku'),
            'barcode': request.form.get('barcode'),
            'category_id': request.form.get('category_id'),
            'description': request.form.get('description'),
            'unit': request.form.get('unit'),
            'purchase_price': float(request.form.get('purchase_price', 0)),
            'sales_price': float(request.form.get('sales_price', 0)),
            'reorder_point': float(request.form.get('reorder_point', 0)) if request.form.get('reorder_point') else None,
            'track_inventory': request.form.get('track_inventory') == 'on',
            'is_active': request.form.get('is_active') == 'on'
        }

        try:
            response = requests.put(
                f'{API_BASE}/inventory/products/{product_id}',
                json=data,
                headers=get_headers()
            )
            if response.status_code == 200:
                flash('Product updated successfully', 'success')
                return redirect(url_for('inventory.index'))
        except Exception as e:
            flash(f'Error: {str(e)}', 'error')

    try:
        product_resp = requests.get(f'{API_BASE}/inventory/products/{product_id}', headers=get_headers())
        product = product_resp.json() if product_resp.status_code == 200 else None
    except:
        product = None

    try:
        categories_resp = requests.get(f'{API_BASE}/inventory/categories', headers=get_headers())
        categories = categories_resp.json() if categories_resp.status_code == 200 else {'items': []}
    except:
        categories = {'items': []}

    return render_template('inventory/product_form.html', product=product, categories=categories)


@inventory_bp.route('/<int:product_id>/delete', methods=['POST'])
def delete(product_id):
    """Delete product"""
    try:
        response = requests.delete(
            f'{API_BASE}/inventory/products/{product_id}',
            headers=get_headers()
        )
        if response.status_code == 200:
            flash('Product deleted successfully', 'success')
        else:
            flash(response.json().get('detail', 'Error deleting product'), 'error')
    except Exception as e:
        flash(f'Error: {str(e)}', 'error')

    return redirect(url_for('inventory.index'))


@inventory_bp.route('/categories')
def categories():
    """Categories list"""
    try:
        response = requests.get(f'{API_BASE}/inventory/categories', headers=get_headers())
        categories = response.json() if response.status_code == 200 else {'items': []}
    except:
        categories = {'items': []}

    return render_template('inventory/categories.html', categories=categories)


@inventory_bp.route('/categories/create', methods=['POST'])
def create_category():
    """Create category via HTMX"""
    data = {
        'name': request.form.get('name'),
        'description': request.form.get('description')
    }

    try:
        response = requests.post(
            f'{API_BASE}/inventory/categories',
            json=data,
            headers=get_headers()
        )
        if response.status_code == 200:
            flash('Category created', 'success')
        else:
            flash(response.json().get('detail', 'Error'), 'error')
    except Exception as e:
        flash(f'Error: {str(e)}', 'error')

    return redirect(url_for('inventory.categories'))


@inventory_bp.route('/adjustments')
def adjustments():
    """Stock adjustments"""
    try:
        response = requests.get(f'{API_BASE}/inventory/stock-adjustments', headers=get_headers())
        adjustments = response.json() if response.status_code == 200 else {'items': []}
    except:
        adjustments = {'items': []}

    return render_template('inventory/adjustments.html', adjustments=adjustments)


@inventory_bp.route('/adjustments/create', methods=['GET', 'POST'])
def create_adjustment():
    """Create stock adjustment"""
    if request.method == 'POST':
        data = {
            'product_id': int(request.form.get('product_id')),
            'quantity_change': float(request.form.get('quantity_change')),
            'reason': request.form.get('reason'),
            'adjustment_type': request.form.get('adjustment_type', 'manual')
        }

        try:
            response = requests.post(
                f'{API_BASE}/inventory/stock-adjustments',
                json=data,
                headers=get_headers()
            )
            if response.status_code == 200:
                flash('Stock adjusted successfully', 'success')
                return redirect(url_for('inventory.adjustments'))
            else:
                flash(response.json().get('detail', 'Error'), 'error')
        except Exception as e:
            flash(f'Error: {str(e)}', 'error')

    # Get products for dropdown
    try:
        products_resp = requests.get(f'{API_BASE}/inventory/products', headers=get_headers())
        products = products_resp.json() if products_resp.status_code == 200 else {'items': []}
    except:
        products = {'items': []}

    return render_template('inventory/adjustment_form.html', products=products)
