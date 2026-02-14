"""Accounting Frontend Routes"""
from flask import Blueprint, render_template, request, redirect, url_for, flash, session
import requests
from datetime import datetime
import logging

accounting_bp = Blueprint('accounting', __name__, url_prefix='/accounting')
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

@accounting_bp.route('/')
def index():
    try:
        response = requests.get(f'{API_BASE}/accounting/accounts', headers=get_headers(), timeout=10)
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
    return render_template('accounting/chart_of_accounts.html', accounts=get_items(data))

@accounting_bp.route('/accounts/create', methods=['GET', 'POST'])
def create_account():
    if request.method == 'POST':
        data = {
            'code': request.form.get('code', '').strip(),
            'name': request.form.get('name', '').strip(),
            'type': request.form.get('type', 'asset'),
            'description': request.form.get('description', '').strip() or None,
            'opening_balance': float(request.form.get('opening_balance', 0)),
            'branch_id': session.get('branch_id', 1)
        }
        if not all([data['code'], data['name']]):
            flash('Account code and name are required', 'error')
        else:
            try:
                response = requests.post(f'{API_BASE}/accounting/accounts', json=data, headers=get_headers(), timeout=10)
                if response.status_code in [200, 201]:
                    flash('Account created successfully', 'success')
                    return redirect(url_for('accounting.index'))
                else:
                    flash(handle_error(response), 'error')
            except requests.exceptions.ConnectionError:
                flash('Cannot connect to server', 'error')
            except Exception as e:
                flash(f'Error: {str(e)}', 'error')
    return render_template('accounting/account_form.html', account=None)

@accounting_bp.route('/accounts/<int:account_id>/edit', methods=['GET', 'POST'])
def edit_account(account_id):
    if request.method == 'POST':
        data = {
            'name': request.form.get('name', '').strip(),
            'description': request.form.get('description', '').strip() or None,
            'is_active': request.form.get('is_active') == 'on'
        }
        try:
            response = requests.put(f'{API_BASE}/accounting/accounts/{account_id}', json=data, headers=get_headers(), timeout=10)
            if response.status_code == 200:
                flash('Account updated successfully', 'success')
                return redirect(url_for('accounting.index'))
            else:
                flash(handle_error(response), 'error')
        except requests.exceptions.ConnectionError:
            flash('Cannot connect to server', 'error')
        except Exception as e:
            flash(f'Error: {str(e)}', 'error')
    
    account = None
    try:
        r = requests.get(f'{API_BASE}/accounting/accounts/{account_id}', headers=get_headers(), timeout=5)
        if r.status_code == 200: account = r.json()
    except: pass
    
    return render_template('accounting/account_form.html', account=account)

@accounting_bp.route('/journal-vouchers')
def journal_vouchers():
    try:
        response = requests.get(f'{API_BASE}/accounting/journal-vouchers', headers=get_headers(), timeout=10)
        data = response.json() if response.status_code == 200 else []
    except:
        data = []
    return render_template('accounting/journal_voucher.html', vouchers=get_items(data))

@accounting_bp.route('/journal-vouchers/create', methods=['GET', 'POST'])
def create_journal_voucher():
    if request.method == 'POST':
        entries = []
        for i in range(int(request.form.get('entry_count', 0))):
            account_id = request.form.get(f'account_id_{i}')
            debit = float(request.form.get(f'debit_{i}', 0))
            credit = float(request.form.get(f'credit_{i}', 0))
            if account_id and (debit > 0 or credit > 0):
                entries.append({
                    'account_id': int(account_id),
                    'debit': debit,
                    'credit': credit,
                    'description': request.form.get(f'description_{i}', '')
                })
        data = {
            'transaction_date': request.form.get('transaction_date'),
            'description': request.form.get('description', '').strip(),
            'reference': request.form.get('reference', '').strip() or None,
            'entries': entries,
            'branch_id': session.get('branch_id', 1)
        }
        if not entries:
            flash('Please add at least one entry', 'error')
        else:
            try:
                response = requests.post(f'{API_BASE}/accounting/journal-vouchers', json=data, headers=get_headers(), timeout=10)
                if response.status_code in [200, 201]:
                    flash('Journal voucher created successfully', 'success')
                    return redirect(url_for('accounting.journal_vouchers'))
                else:
                    flash(handle_error(response), 'error')
            except requests.exceptions.ConnectionError:
                flash('Cannot connect to server', 'error')
            except Exception as e:
                flash(f'Error: {str(e)}', 'error')
    
    accounts = []
    try:
        r = requests.get(f'{API_BASE}/accounting/accounts', headers=get_headers(), timeout=5)
        if r.status_code == 200: accounts = get_items(r.json())
    except: pass
    
    return render_template('accounting/journal_voucher_form.html', accounts=accounts)

@accounting_bp.route('/ledger')
def ledger():
    account_id = request.args.get('account_id')
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')
    params = {}
    if account_id: params['account_id'] = account_id
    if start_date: params['start_date'] = start_date
    if end_date: params['end_date'] = end_date
    
    entries_data, accounts_data = [], []
    try:
        r = requests.get(f'{API_BASE}/accounting/ledger', params=params, headers=get_headers(), timeout=10)
        if r.status_code == 200: entries_data = r.json()
    except: pass
    try:
        r = requests.get(f'{API_BASE}/accounting/accounts', headers=get_headers(), timeout=5)
        if r.status_code == 200: accounts_data = r.json()
    except: pass
    
    return render_template('accounting/ledger.html', entries=get_items(entries_data), accounts=get_items(accounts_data))

@accounting_bp.route('/trial-balance')
def trial_balance():
    as_of_date = request.args.get('as_of_date', datetime.now().strftime('%Y-%m-%d'))
    report = {}
    try:
        r = requests.get(f'{API_BASE}/accounting/trial-balance', params={'as_of_date': as_of_date}, headers=get_headers(), timeout=10)
        if r.status_code == 200: report = r.json()
    except: pass
    return render_template('accounting/trial_balance.html', report=report, as_of_date=as_of_date)
