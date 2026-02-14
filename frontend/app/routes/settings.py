"""Settings Frontend Routes"""
from flask import Blueprint, render_template, request, redirect, url_for, flash, session
import requests
import logging

settings_bp = Blueprint('settings', __name__, url_prefix='/settings')
API_BASE = 'http://localhost:8000/api/v1'
logger = logging.getLogger(__name__)

def get_headers():
    token = session.get('access_token')
    return {'Authorization': f'Bearer {token}', 'Content-Type': 'application/json'} if token else {'Content-Type': 'application/json'}

def handle_error(response):
    try:
        data = response.json()
        return data.get('detail', data.get('message', f'Error (HTTP {response.status_code})'))
    except: return f'Error - HTTP {response.status_code}'

@settings_bp.route('/')
def index():
    company, invoice = {}, {}
    try:
        r = requests.get(f'{API_BASE}/settings/company', headers=get_headers(), timeout=5)
        if r.status_code == 200: company = r.json()
    except: pass
    try:
        r = requests.get(f'{API_BASE}/settings/invoice', headers=get_headers(), timeout=5)
        if r.status_code == 200: invoice = r.json()
    except: pass
    return render_template('settings/index.html', company=company, invoice=invoice)

@settings_bp.route('/company', methods=['GET', 'POST'])
def company():
    if request.method == 'POST':
        data = {
            'business_name': request.form.get('business_name', '').strip(),
            'trading_name': request.form.get('trading_name', '').strip() or None,
            'industry': request.form.get('industry', '').strip() or None,
            'address': request.form.get('address', '').strip() or None,
            'city': request.form.get('city', '').strip() or None,
            'state': request.form.get('state', '').strip() or None,
            'phone': request.form.get('phone', '').strip() or None,
            'email': request.form.get('email', '').strip() or None,
            'website': request.form.get('website', '').strip() or None,
            'tax_id': request.form.get('tax_id', '').strip() or None,
            'rc_number': request.form.get('rc_number', '').strip() or None
        }
        try:
            response = requests.put(f'{API_BASE}/settings/company', json=data, headers=get_headers(), timeout=10)
            if response.status_code == 200:
                flash('Company settings updated', 'success')
            else:
                flash(handle_error(response), 'error')
        except requests.exceptions.ConnectionError:
            flash('Cannot connect to server', 'error')
        except Exception as e:
            flash(f'Error: {str(e)}', 'error')
    
    settings, states, industries = {}, [], []
    try:
        r = requests.get(f'{API_BASE}/settings/company', headers=get_headers(), timeout=5)
        if r.status_code == 200: settings = r.json()
    except: pass
    try:
        r = requests.get(f'{API_BASE}/settings/nigerian-states', headers=get_headers(), timeout=5)
        if r.status_code == 200: states = r.json().get('states', [])
    except: pass
    try:
        r = requests.get(f'{API_BASE}/settings/industries', headers=get_headers(), timeout=5)
        if r.status_code == 200: industries = r.json().get('industries', [])
    except: pass
    
    return render_template('settings/company.html', settings=settings, states=states, industries=industries)

@settings_bp.route('/invoice', methods=['GET', 'POST'])
def invoice():
    if request.method == 'POST':
        data = {
            'invoice_prefix': request.form.get('invoice_prefix', 'INV-'),
            'quote_prefix': request.form.get('quote_prefix', 'QT-'),
            'credit_note_prefix': request.form.get('credit_note_prefix', 'CN-'),
            'default_payment_terms': int(request.form.get('default_payment_terms', 30)),
            'default_vat_rate': float(request.form.get('default_vat_rate', 7.5))
        }
        try:
            response = requests.put(f'{API_BASE}/settings/invoice', json=data, headers=get_headers(), timeout=10)
            if response.status_code == 200:
                flash('Invoice settings updated', 'success')
            else:
                flash(handle_error(response), 'error')
        except requests.exceptions.ConnectionError:
            flash('Cannot connect to server', 'error')
        except Exception as e:
            flash(f'Error: {str(e)}', 'error')
    
    settings = {}
    try:
        r = requests.get(f'{API_BASE}/settings/invoice', headers=get_headers(), timeout=5)
        if r.status_code == 200: settings = r.json()
    except: pass
    
    return render_template('settings/invoice.html', settings=settings)

@settings_bp.route('/subscription')
def subscription():
    subscription = {}
    try:
        response = requests.get(f'{API_BASE}/auth/me', headers=get_headers(), timeout=10)
        if response.status_code == 200:
            user_data = response.json()
            subscription = user_data.get('subscription', {})
    except:
        pass
    return render_template('settings/subscription.html', subscription=subscription)
