"""HR & Payroll Frontend Routes"""
from flask import Blueprint, render_template, request, redirect, url_for, flash, session
import requests
from datetime import datetime
import logging

hr_bp = Blueprint('hr', __name__, url_prefix='/hr')
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

@hr_bp.route('/')
def index():
    dashboard, employees_data = {}, []
    try:
        r = requests.get(f'{API_BASE}/hr/dashboard', headers=get_headers(), timeout=5)
        if r.status_code == 200: dashboard = r.json()
    except: pass
    try:
        r = requests.get(f'{API_BASE}/hr/employees', headers=get_headers(), timeout=5)
        if r.status_code == 200: employees_data = r.json()
    except: pass
    return render_template('hr/index.html', dashboard=dashboard, employees=get_items(employees_data))

@hr_bp.route('/employees')
def employees():
    department = request.args.get('department', '')
    params = {'department': department} if department else {}
    try:
        response = requests.get(f'{API_BASE}/hr/employees', params=params, headers=get_headers(), timeout=10)
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
    return render_template('hr/employees.html', employees=get_items(data))

@hr_bp.route('/employees/create', methods=['GET', 'POST'])
def create_employee():
    if request.method == 'POST':
        data = {
            'first_name': request.form.get('first_name', '').strip(),
            'last_name': request.form.get('last_name', '').strip(),
            'email': request.form.get('email', '').strip(),
            'phone': request.form.get('phone', '').strip() or None,
            'address': request.form.get('address', '').strip() or None,
            'date_of_birth': request.form.get('date_of_birth') or None,
            'hire_date': request.form.get('hire_date') or None,
            'department': request.form.get('department', '').strip() or None,
            'position': request.form.get('position', '').strip() or None,
            'employment_type': request.form.get('employment_type', 'full_time'),
            'basic_salary': float(request.form.get('basic_salary', 0)),
            'bank_name': request.form.get('bank_name', '').strip() or None,
            'bank_account': request.form.get('bank_account', '').strip() or None,
            'tax_id': request.form.get('tax_id', '').strip() or None,
            'pension_id': request.form.get('pension_id', '').strip() or None,
            'branch_id': session.get('branch_id', 1)
        }
        if not all([data['first_name'], data['last_name'], data['email']]):
            flash('First name, last name and email are required', 'error')
        else:
            try:
                response = requests.post(f'{API_BASE}/hr/employees', json=data, headers=get_headers(), timeout=10)
                if response.status_code in [200, 201]:
                    flash('Employee created successfully', 'success')
                    return redirect(url_for('hr.employees'))
                else:
                    flash(handle_error(response), 'error')
            except requests.exceptions.ConnectionError:
                flash('Cannot connect to server', 'error')
            except Exception as e:
                flash(f'Error: {str(e)}', 'error')
    return render_template('hr/employee_form.html', employee=None)

@hr_bp.route('/employees/<int:employee_id>/edit', methods=['GET', 'POST'])
def edit_employee(employee_id):
    if request.method == 'POST':
        data = {
            'first_name': request.form.get('first_name', '').strip(),
            'last_name': request.form.get('last_name', '').strip(),
            'email': request.form.get('email', '').strip(),
            'phone': request.form.get('phone', '').strip() or None,
            'department': request.form.get('department', '').strip() or None,
            'position': request.form.get('position', '').strip() or None,
            'basic_salary': float(request.form.get('basic_salary', 0)),
            'bank_name': request.form.get('bank_name', '').strip() or None,
            'bank_account': request.form.get('bank_account', '').strip() or None,
            'is_active': request.form.get('is_active') == 'on'
        }
        try:
            response = requests.put(f'{API_BASE}/hr/employees/{employee_id}', json=data, headers=get_headers(), timeout=10)
            if response.status_code == 200:
                flash('Employee updated successfully', 'success')
                return redirect(url_for('hr.employees'))
            else:
                flash(handle_error(response), 'error')
        except requests.exceptions.ConnectionError:
            flash('Cannot connect to server', 'error')
        except Exception as e:
            flash(f'Error: {str(e)}', 'error')
    
    employee = None
    try:
        r = requests.get(f'{API_BASE}/hr/employees/{employee_id}', headers=get_headers(), timeout=5)
        if r.status_code == 200: employee = r.json()
    except: pass
    
    return render_template('hr/employee_form.html', employee=employee)

@hr_bp.route('/payroll')
def payroll():
    try:
        response = requests.get(f'{API_BASE}/hr/payslips', headers=get_headers(), timeout=10)
        data = response.json() if response.status_code == 200 else []
    except:
        data = []
    return render_template('hr/payroll.html', payslips=get_items(data))

@hr_bp.route('/payroll/run', methods=['GET', 'POST'])
def run_payroll():
    if request.method == 'POST':
        data = {
            'month': int(request.form.get('month', datetime.now().month)),
            'year': int(request.form.get('year', datetime.now().year)),
            'branch_id': session.get('branch_id', 1)
        }
        try:
            response = requests.post(f'{API_BASE}/hr/payroll/run', json=data, headers=get_headers(), timeout=30)
            if response.status_code == 200:
                result = response.json()
                flash(result.get('message', 'Payroll processed'), 'success')
                return redirect(url_for('hr.payroll'))
            else:
                flash(handle_error(response), 'error')
        except requests.exceptions.ConnectionError:
            flash('Cannot connect to server', 'error')
        except Exception as e:
            flash(f'Error: {str(e)}', 'error')
    
    return render_template('hr/run_payroll.html', current_month=datetime.now().month, current_year=datetime.now().year)

@hr_bp.route('/payslips/<int:payslip_id>')
def view_payslip(payslip_id):
    try:
        response = requests.get(f'{API_BASE}/hr/payslips/{payslip_id}', headers=get_headers(), timeout=10)
        payslip = response.json() if response.status_code == 200 else None
    except:
        payslip = None
    if not payslip:
        flash('Payslip not found', 'error')
        return redirect(url_for('hr.payroll'))
    return render_template('hr/payslip_view.html', payslip=payslip)
