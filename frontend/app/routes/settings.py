"""Settings Frontend Routes"""
from flask import Blueprint, render_template, request, redirect, url_for, flash, session
import requests

settings_bp = Blueprint('settings', __name__, url_prefix='/settings')
API_BASE = 'http://localhost:8000/api/v1'

def get_headers():
    token = session.get('access_token')
    return {'Authorization': f'Bearer {token}'} if token else {}

@settings_bp.route('/')
def index():
    try:
        company_resp = requests.get(f'{API_BASE}/settings/company', headers=get_headers())
        company = company_resp.json() if company_resp.status_code == 200 else {}
    except:
        company = {}
    try:
        invoice_resp = requests.get(f'{API_BASE}/settings/invoice', headers=get_headers())
        invoice = invoice_resp.json() if invoice_resp.status_code == 200 else {}
    except:
        invoice = {}
    return render_template('settings/index.html', company=company, invoice=invoice)

@settings_bp.route('/company', methods=['GET', 'POST'])
def company():
    if request.method == 'POST':
        data = {
            'business_name': request.form.get('business_name'),
            'trading_name': request.form.get('trading_name'),
            'industry': request.form.get('industry'),
            'address': request.form.get('address'),
            'city': request.form.get('city'),
            'state': request.form.get('state'),
            'phone': request.form.get('phone'),
            'email': request.form.get('email'),
            'website': request.form.get('website'),
            'tax_id': request.form.get('tax_id'),
            'rc_number': request.form.get('rc_number')
        }
        try:
            response = requests.put(f'{API_BASE}/settings/company', json=data, headers=get_headers())
            if response.status_code == 200:
                flash('Company settings updated', 'success')
            else:
                flash(response.json().get('detail', 'Error'), 'error')
        except Exception as e:
            flash(f'Error: {str(e)}', 'error')
    try:
        response = requests.get(f'{API_BASE}/settings/company', headers=get_headers())
        settings = response.json() if response.status_code == 200 else {}
    except:
        settings = {}
    try:
        states_resp = requests.get(f'{API_BASE}/settings/nigerian-states', headers=get_headers())
        states = states_resp.json().get('states', []) if states_resp.status_code == 200 else []
    except:
        states = []
    try:
        industries_resp = requests.get(f'{API_BASE}/settings/industries', headers=get_headers())
        industries = industries_resp.json().get('industries', []) if industries_resp.status_code == 200 else []
    except:
        industries = []
    return render_template('settings/company.html', settings=settings, states=states, industries=industries)

@settings_bp.route('/invoice', methods=['GET', 'POST'])
def invoice():
    if request.method == 'POST':
        data = {
            'invoice_prefix': request.form.get('invoice_prefix'),
            'quote_prefix': request.form.get('quote_prefix'),
            'credit_note_prefix': request.form.get('credit_note_prefix'),
            'default_payment_terms': int(request.form.get('default_payment_terms', 30)),
            'default_vat_rate': float(request.form.get('default_vat_rate', 7.5))
        }
        try:
            response = requests.put(f'{API_BASE}/settings/invoice', json=data, headers=get_headers())
            if response.status_code == 200:
                flash('Invoice settings updated', 'success')
        except Exception as e:
            flash(f'Error: {str(e)}', 'error')
    try:
        response = requests.get(f'{API_BASE}/settings/invoice', headers=get_headers())
        settings = response.json() if response.status_code == 200 else {}
    except:
        settings = {}
    return render_template('settings/invoice.html', settings=settings)

@settings_bp.route('/subscription')
def subscription():
    try:
        response = requests.get(f'{API_BASE}/auth/me', headers=get_headers())
        user_data = response.json() if response.status_code == 200 else {}
    except:
        user_data = {}
    return render_template('settings/subscription.html', subscription=user_data.get('subscription', {}))
