"""
Reports Frontend Routes
"""
from flask import Blueprint, render_template, request, flash
import requests
from datetime import datetime, timedelta

reports_bp = Blueprint('reports', __name__, url_prefix='/reports')

API_BASE = 'http://localhost:8000/api/v1'


def get_headers():
    token = session.get('access_token')
    return {'Authorization': f'Bearer {token}'} if token else {}


@reports_bp.route('/')
def index():
    """Reports dashboard"""
    return render_template('reports/index.html')


@reports_bp.route('/profit-loss')
def profit_loss():
    """Profit & Loss Statement"""
    start_date = request.args.get('start_date', (datetime.now() - timedelta(days=365)).strftime('%Y-%m-%d'))
    end_date = request.args.get('end_date', datetime.now().strftime('%Y-%m-%d'))
    compare = request.args.get('compare', 'false') == 'true'

    try:
        response = requests.get(
            f'{API_BASE}/reports/profit-loss',
            params={
                'start_date': start_date,
                'end_date': end_date,
                'compare_previous': compare
            },
            headers=get_headers()
        )
        report = response.json() if response.status_code == 200 else {}
    except:
        report = {}

    return render_template('reports/profit_loss.html', report=report, start_date=start_date, end_date=end_date)


@reports_bp.route('/balance-sheet')
def balance_sheet():
    """Balance Sheet"""
    as_of_date = request.args.get('as_of_date', datetime.now().strftime('%Y-%m-%d'))

    try:
        response = requests.get(
            f'{API_BASE}/reports/balance-sheet',
            params={'as_of_date': as_of_date},
            headers=get_headers()
        )
        report = response.json() if response.status_code == 200 else {}
    except:
        report = {}

    return render_template('reports/balance_sheet.html', report=report, as_of_date=as_of_date)


@reports_bp.route('/trial-balance')
def trial_balance():
    """Trial Balance"""
    as_of_date = request.args.get('as_of_date', datetime.now().strftime('%Y-%m-%d'))

    try:
        response = requests.get(
            f'{API_BASE}/reports/trial-balance',
            params={'as_of_date': as_of_date},
            headers=get_headers()
        )
        report = response.json() if response.status_code == 200 else {}
    except:
        report = {}

    return render_template('reports/trial_balance.html', report=report, as_of_date=as_of_date)


@reports_bp.route('/aging')
def aging():
    """Aging Reports"""
    report_type = request.args.get('type', 'receivables')

    try:
        if report_type == 'payables':
            response = requests.get(
                f'{API_BASE}/reports/payables-aging',
                headers=get_headers()
            )
        else:
            response = requests.get(
                f'{API_BASE}/reports/receivables-aging',
                headers=get_headers()
            )
        report = response.json() if response.status_code == 200 else {}
    except:
        report = {}

    return render_template('reports/aging.html', report=report, report_type=report_type)


@reports_bp.route('/sales-summary')
def sales_summary():
    """Sales Summary Report"""
    start_date = request.args.get('start_date', (datetime.now() - timedelta(days=30)).strftime('%Y-%m-%d'))
    end_date = request.args.get('end_date', datetime.now().strftime('%Y-%m-%d'))
    group_by = request.args.get('group_by', 'day')

    try:
        response = requests.get(
            f'{API_BASE}/reports/sales-summary',
            params={
                'start_date': start_date,
                'end_date': end_date,
                'group_by': group_by
            },
            headers=get_headers()
        )
        report = response.json() if response.status_code == 200 else {}
    except:
        report = {}

    return render_template('reports/sales_summary.html', report=report, start_date=start_date, end_date=end_date, group_by=group_by)


@reports_bp.route('/cash-flow')
def cash_flow():
    """Cash Flow Statement"""
    start_date = request.args.get('start_date', (datetime.now() - timedelta(days=30)).strftime('%Y-%m-%d'))
    end_date = request.args.get('end_date', datetime.now().strftime('%Y-%m-%d'))

    try:
        response = requests.get(
            f'{API_BASE}/reports/cash-flow',
            params={
                'start_date': start_date,
                'end_date': end_date
            },
            headers=get_headers()
        )
        report = response.json() if response.status_code == 200 else {}
    except:
        report = {}

    return render_template('reports/cash_flow.html', report=report, start_date=start_date, end_date=end_date)
