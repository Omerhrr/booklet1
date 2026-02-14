"""
Accounting Frontend Routes
"""
from flask import Blueprint, render_template, request, redirect, url_for, flash, session, jsonify
import requests
from datetime import datetime

accounting_bp = Blueprint('accounting', __name__, url_prefix='/accounting')

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


@accounting_bp.route('/')
def index():
    """Chart of Accounts page"""
    try:
        response = requests.get(f'{API_BASE}/accounting/accounts', headers=get_headers())
        data = response.json() if response.status_code == 200 else []
    except:
        data = []

    return render_template('accounting/chart_of_accounts.html', accounts=get_items(data))


@accounting_bp.route('/accounts/create', methods=['GET', 'POST'])
def create_account():
    """Create new account"""
    if request.method == 'POST':
        data = {
            'code': request.form.get('code'),
            'name': request.form.get('name'),
            'type': request.form.get('type'),
            'description': request.form.get('description'),
            'opening_balance': float(request.form.get('opening_balance', 0)),
            'branch_id': session.get('branch_id', 1)
        }

        try:
            response = requests.post(
                f'{API_BASE}/accounting/accounts',
                json=data,
                headers=get_headers()
            )
            if response.status_code == 200:
                flash('Account created successfully', 'success')
                return redirect(url_for('accounting.index'))
            else:
                flash(response.json().get('detail', 'Error creating account'), 'error')
        except Exception as e:
            flash(f'Error: {str(e)}', 'error')

    return render_template('accounting/account_form.html', account=None)


@accounting_bp.route('/accounts/<int:account_id>/edit', methods=['GET', 'POST'])
def edit_account(account_id):
    """Edit account"""
    if request.method == 'POST':
        data = {
            'name': request.form.get('name'),
            'description': request.form.get('description'),
            'is_active': request.form.get('is_active') == 'on'
        }

        try:
            response = requests.put(
                f'{API_BASE}/accounting/accounts/{account_id}',
                json=data,
                headers=get_headers()
            )
            if response.status_code == 200:
                flash('Account updated successfully', 'success')
                return redirect(url_for('accounting.index'))
        except Exception as e:
            flash(f'Error: {str(e)}', 'error')

    try:
        response = requests.get(f'{API_BASE}/accounting/accounts/{account_id}', headers=get_headers())
        account = response.json() if response.status_code == 200 else None
    except:
        account = None

    return render_template('accounting/account_form.html', account=account)


@accounting_bp.route('/journal-vouchers')
def journal_vouchers():
    """Journal Vouchers list"""
    try:
        response = requests.get(f'{API_BASE}/accounting/journal-vouchers', headers=get_headers())
        data = response.json() if response.status_code == 200 else []
    except:
        data = []

    return render_template('accounting/journal_voucher.html', vouchers=get_items(data))


@accounting_bp.route('/journal-vouchers/create', methods=['GET', 'POST'])
def create_journal_voucher():
    """Create journal voucher"""
    if request.method == 'POST':
        entries = []
        for i in range(int(request.form.get('entry_count', 0))):
            account_id = request.form.get(f'account_id_{i}')
            debit = float(request.form.get(f'debit_{i}', 0))
            credit = float(request.form.get(f'credit_{i}', 0))
            description = request.form.get(f'description_{i}', '')

            if account_id and (debit > 0 or credit > 0):
                entries.append({
                    'account_id': int(account_id),
                    'debit': debit,
                    'credit': credit,
                    'description': description
                })

        data = {
            'transaction_date': request.form.get('transaction_date'),
            'description': request.form.get('description'),
            'reference': request.form.get('reference'),
            'entries': entries,
            'branch_id': session.get('branch_id', 1)
        }

        try:
            response = requests.post(
                f'{API_BASE}/accounting/journal-vouchers',
                json=data,
                headers=get_headers()
            )
            if response.status_code == 200:
                flash('Journal voucher created successfully', 'success')
                return redirect(url_for('accounting.journal_vouchers'))
        except Exception as e:
            flash(f'Error: {str(e)}', 'error')

    # Get accounts for dropdown
    try:
        response = requests.get(f'{API_BASE}/accounting/accounts', headers=get_headers())
        accounts_data = response.json() if response.status_code == 200 else []
    except:
        accounts_data = []

    return render_template('accounting/journal_voucher_form.html', accounts=get_items(accounts_data))


@accounting_bp.route('/ledger')
def ledger():
    """General Ledger"""
    account_id = request.args.get('account_id')
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')

    params = {}
    if account_id:
        params['account_id'] = account_id
    if start_date:
        params['start_date'] = start_date
    if end_date:
        params['end_date'] = end_date

    try:
        response = requests.get(
            f'{API_BASE}/accounting/ledger',
            params=params,
            headers=get_headers()
        )
        entries_data = response.json() if response.status_code == 200 else []
    except:
        entries_data = []

    # Get accounts for filter
    try:
        response = requests.get(f'{API_BASE}/accounting/accounts', headers=get_headers())
        accounts_data = response.json() if response.status_code == 200 else []
    except:
        accounts_data = []

    return render_template('accounting/ledger.html', entries=get_items(entries_data), accounts=get_items(accounts_data))


@accounting_bp.route('/trial-balance')
def trial_balance():
    """Trial Balance report"""
    as_of_date = request.args.get('as_of_date', datetime.now().strftime('%Y-%m-%d'))

    try:
        response = requests.get(
            f'{API_BASE}/accounting/trial-balance',
            params={'as_of_date': as_of_date},
            headers=get_headers()
        )
        report = response.json() if response.status_code == 200 else {}
    except:
        report = {}

    return render_template('accounting/trial_balance.html', report=report)
