"""
Customers Frontend Routes
"""
from flask import Blueprint, render_template, request, redirect, url_for, flash, session
import requests

customers_bp = Blueprint('customers', __name__, url_prefix='/customers')

API_BASE = 'http://localhost:8000/api/v1'


def get_headers():
    token = session.get('access_token')
    return {'Authorization': f'Bearer {token}'} if token else {}


@customers_bp.route('/')
def index():
    """Customers list"""
    search = request.args.get('search', '')

    params = {}
    if search:
        params['search'] = search

    try:
        response = requests.get(
            f'{API_BASE}/customers',
            params=params,
            headers=get_headers()
        )
        customers = response.json() if response.status_code == 200 else {'items': []}
    except:
        customers = {'items': []}

    return render_template('customers/index.html', customers=customers.get('items', []), search=search)


@customers_bp.route('/create', methods=['GET', 'POST'])
def create():
    """Create new customer"""
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
            'credit_limit': float(request.form.get('credit_limit', 0)) if request.form.get('credit_limit') else None,
            'payment_terms': request.form.get('payment_terms', 'Net 30')
        }

        try:
            response = requests.post(
                f'{API_BASE}/customers',
                json=data,
                headers=get_headers()
            )
            if response.status_code == 200:
                flash('Customer created successfully', 'success')
                return redirect(url_for('customers.index'))
            else:
                flash(response.json().get('detail', 'Error'), 'error')
        except Exception as e:
            flash(f'Error: {str(e)}', 'error')

    return render_template('customers/form.html', customer=None)


@customers_bp.route('/<int:customer_id>')
def view(customer_id):
    """View customer details"""
    try:
        response = requests.get(f'{API_BASE}/customers/{customer_id}', headers=get_headers())
        customer = response.json() if response.status_code == 200 else None
    except:
        customer = None

    if not customer:
        flash('Customer not found', 'error')
        return redirect(url_for('customers.index'))

    return render_template('customers/view.html', customer=customer)


@customers_bp.route('/<int:customer_id>/edit', methods=['GET', 'POST'])
def edit(customer_id):
    """Edit customer"""
    if request.method == 'POST':
        data = {
            'name': request.form.get('name'),
            'email': request.form.get('email'),
            'phone': request.form.get('phone'),
            'address': request.form.get('address'),
            'city': request.form.get('city'),
            'state': request.form.get('state'),
            'contact_person': request.form.get('contact_person'),
            'credit_limit': float(request.form.get('credit_limit', 0)) if request.form.get('credit_limit') else None,
            'payment_terms': request.form.get('payment_terms'),
            'is_active': request.form.get('is_active') == 'on'
        }

        try:
            response = requests.put(
                f'{API_BASE}/customers/{customer_id}',
                json=data,
                headers=get_headers()
            )
            if response.status_code == 200:
                flash('Customer updated successfully', 'success')
                return redirect(url_for('customers.index'))
        except Exception as e:
            flash(f'Error: {str(e)}', 'error')

    try:
        response = requests.get(f'{API_BASE}/customers/{customer_id}', headers=get_headers())
        customer = response.json() if response.status_code == 200 else None
    except:
        customer = None

    return render_template('customers/form.html', customer=customer)


@customers_bp.route('/<int:customer_id>/delete', methods=['POST'])
def delete(customer_id):
    """Delete customer"""
    try:
        response = requests.delete(
            f'{API_BASE}/customers/{customer_id}',
            headers=get_headers()
        )
        if response.status_code == 200:
            flash('Customer deleted successfully', 'success')
        else:
            flash(response.json().get('detail', 'Error'), 'error')
    except Exception as e:
        flash(f'Error: {str(e)}', 'error')

    return redirect(url_for('customers.index'))
