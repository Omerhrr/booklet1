"""
HR & Payroll Frontend Routes
"""
from flask import Blueprint, render_template, request, redirect, url_for, flash, session
import requests
from datetime import datetime, date

hr_bp = Blueprint('hr', __name__, url_prefix='/hr')

API_BASE = 'http://localhost:8000/api/v1'


def get_headers():
    token = session.get('access_token')
    return {'Authorization': f'Bearer {token}'} if token else {}


def get_items(data):
    if data is None:
        return []
    if isinstance(data, list):
        return data
    if isinstance(data, dict):
        return data.get('items', [])
    return []


@hr_bp.route('/')
def index():
    """HR Dashboard"""
    try:
        dashboard_resp = requests.get(f'{API_BASE}/hr/dashboard', headers=get_headers())
        dashboard = dashboard_resp.json() if dashboard_resp.status_code == 200 else {}
    except:
        dashboard = {}

    try:
        employees_resp = requests.get(f'{API_BASE}/hr/employees', headers=get_headers())
        employees_data = employees_resp.json() if employees_resp.status_code == 200 else []
    except:
        employees_data = []

    return render_template('hr/index.html', dashboard=dashboard, employees=get_items(employees_data))


@hr_bp.route('/employees')
def employees():
    """Employees list"""
    department = request.args.get('department', '')
    params = {}
    if department:
        params['department'] = department

    try:
        response = requests.get(f'{API_BASE}/hr/employees', params=params, headers=get_headers())
        data = response.json() if response.status_code == 200 else []
    except:
        data = []

    return render_template('hr/employees.html', employees=get_items(data))


@hr_bp.route('/employees/create', methods=['GET', 'POST'])
def create_employee():
    """Create new employee"""
    if request.method == 'POST':
        data = {
            'first_name': request.form.get('first_name'),
            'last_name': request.form.get('last_name'),
            'email': request.form.get('email'),
            'phone': request.form.get('phone'),
            'address': request.form.get('address'),
            'date_of_birth': request.form.get('date_of_birth'),
            'hire_date': request.form.get('hire_date'),
            'department': request.form.get('department'),
            'position': request.form.get('position'),
            'employment_type': request.form.get('employment_type', 'full_time'),
            'basic_salary': float(request.form.get('basic_salary', 0)),
            'bank_name': request.form.get('bank_name'),
            'bank_account': request.form.get('bank_account'),
            'tax_id': request.form.get('tax_id'),
            'pension_id': request.form.get('pension_id'),
            'branch_id': session.get('branch_id', 1)
        }
        try:
            response = requests.post(f'{API_BASE}/hr/employees', json=data, headers=get_headers())
            if response.status_code == 200:
                flash('Employee created successfully', 'success')
                return redirect(url_for('hr.employees'))
            else:
                flash(response.json().get('detail', 'Error'), 'error')
        except Exception as e:
            flash(f'Error: {str(e)}', 'error')
    return render_template('hr/employee_form.html', employee=None)


@hr_bp.route('/employees/<int:employee_id>/edit', methods=['GET', 'POST'])
def edit_employee(employee_id):
    """Edit employee"""
    if request.method == 'POST':
        data = {
            'first_name': request.form.get('first_name'),
            'last_name': request.form.get('last_name'),
            'email': request.form.get('email'),
            'phone': request.form.get('phone'),
            'department': request.form.get('department'),
            'position': request.form.get('position'),
            'basic_salary': float(request.form.get('basic_salary', 0)),
            'bank_name': request.form.get('bank_name'),
            'bank_account': request.form.get('bank_account'),
            'is_active': request.form.get('is_active') == 'on'
        }
        try:
            response = requests.put(f'{API_BASE}/hr/employees/{employee_id}', json=data, headers=get_headers())
            if response.status_code == 200:
                flash('Employee updated successfully', 'success')
                return redirect(url_for('hr.employees'))
        except Exception as e:
            flash(f'Error: {str(e)}', 'error')
    try:
        response = requests.get(f'{API_BASE}/hr/employees/{employee_id}', headers=get_headers())
        employee = response.json() if response.status_code == 200 else None
    except:
        employee = None
    return render_template('hr/employee_form.html', employee=employee)


@hr_bp.route('/payroll')
def payroll():
    """Payroll management"""
    try:
        payslips_resp = requests.get(f'{API_BASE}/hr/payslips', headers=get_headers())
        data = payslips_resp.json() if payslips_resp.status_code == 200 else []
    except:
        data = []
    return render_template('hr/payroll.html', payslips=get_items(data))


@hr_bp.route('/payroll/run', methods=['GET', 'POST'])
def run_payroll():
    """Run payroll"""
    if request.method == 'POST':
        data = {
            'month': int(request.form.get('month')),
            'year': int(request.form.get('year')),
            'branch_id': session.get('branch_id', 1)
        }
        try:
            response = requests.post(f'{API_BASE}/hr/payroll/run', json=data, headers=get_headers())
            if response.status_code == 200:
                result = response.json()
                flash(result.get('message', 'Payroll processed'), 'success')
                return redirect(url_for('hr.payroll'))
            else:
                flash(response.json().get('detail', 'Error running payroll'), 'error')
        except Exception as e:
            flash(f'Error: {str(e)}', 'error')
    current_month = datetime.now().month
    current_year = datetime.now().year
    return render_template('hr/run_payroll.html', current_month=current_month, current_year=current_year)


@hr_bp.route('/payslips/<int:payslip_id>')
def view_payslip(payslip_id):
    """View payslip"""
    try:
        response = requests.get(f'{API_BASE}/hr/payslips/{payslip_id}', headers=get_headers())
        payslip = response.json() if response.status_code == 200 else None
    except:
        payslip = None
    if not payslip:
        flash('Payslip not found', 'error')
        return redirect(url_for('hr.payroll'))
    return render_template('hr/payslip_view.html', payslip=payslip)
