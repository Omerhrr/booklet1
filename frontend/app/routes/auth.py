"""
Authentication Routes
"""

from flask import Blueprint, render_template, request, redirect, url_for, session, flash
import requests
import os

bp = Blueprint('auth', __name__)

API_BASE_URL = os.getenv("API_BASE_URL", "http://localhost:8000/api/v1")


@bp.route('/login', methods=['GET', 'POST'])
def login():
    """Login page"""
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        tenant_subdomain = request.form.get('tenant_subdomain')
        
        # Call API
        try:
            response = requests.post(
                f"{API_BASE_URL}/auth/login",
                json={
                    'email': email,
                    'password': password,
                    'tenant_subdomain': tenant_subdomain
                }
            )
            
            if response.status_code == 200:
                data = response.json()
                
                # Store tokens in session
                session['access_token'] = data['access_token']
                session['refresh_token'] = data['refresh_token']
                
                # Get user info
                user_response = requests.get(
                    f"{API_BASE_URL}/auth/me",
                    headers={'Authorization': f"Bearer {data['access_token']}"}
                )
                
                if user_response.status_code == 200:
                    user_data = user_response.json()
                    session['user'] = user_data
                    session['tenant'] = {
                        'business_name': user_data.get('tenant_name', 'Business'),
                        'id': user_data.get('tenant_id')
                    }
                    session['tenant_id'] = user_data.get('tenant_id')
                    session['is_superuser'] = user_data.get('is_superuser', False)
                    # Initialize permissions (superusers will have access to everything)
                    session['permissions'] = [] if not user_data.get('is_superuser') else ['all']

                    flash('Welcome back!', 'success')
                    return redirect(url_for('dashboard.index'))
            else:
                error = response.json().get('detail', 'Login failed')
                flash(error, 'error')
        except Exception as e:
            flash(f'Connection error: {str(e)}', 'error')
    
    return render_template('auth/login.html')


@bp.route('/signup', methods=['GET', 'POST'])
def signup():
    """Signup page"""
    if request.method == 'POST':
        business_name = request.form.get('business_name')
        email = request.form.get('email')
        username = request.form.get('username')
        password = request.form.get('password')
        password_confirm = request.form.get('password_confirm')
        subdomain = request.form.get('subdomain', '').lower()
        first_name = request.form.get('first_name')
        last_name = request.form.get('last_name')
        
        # Validate
        if password != password_confirm:
            flash('Passwords do not match', 'error')
            return render_template('auth/signup.html')
        
        # Call API
        try:
            response = requests.post(
                f"{API_BASE_URL}/auth/signup",
                json={
                    'business_name': business_name,
                    'email': email,
                    'username': username,
                    'password': password,
                    'subdomain': subdomain,
                    'first_name': first_name,
                    'last_name': last_name
                }
            )
            
            if response.status_code == 201:
                data = response.json()

                # Store tokens and login
                session['access_token'] = data['access_token']
                session['refresh_token'] = data['refresh_token']

                # Get user info
                user_response = requests.get(
                    f"{API_BASE_URL}/auth/me",
                    headers={'Authorization': f"Bearer {data['access_token']}"}
                )

                if user_response.status_code == 200:
                    user_data = user_response.json()
                    session['user'] = user_data
                    session['tenant'] = {
                        'business_name': user_data.get('tenant_name', 'Business'),
                        'id': user_data.get('tenant_id')
                    }
                    session['tenant_id'] = user_data.get('tenant_id')
                    session['is_superuser'] = user_data.get('is_superuser', False)
                    # Initialize permissions (superusers will have access to everything)
                    session['permissions'] = [] if not user_data.get('is_superuser') else ['all']

                flash('Account created successfully! Welcome to Booklet.', 'success')
                return redirect(url_for('dashboard.index'))
            else:
                error = response.json().get('detail', 'Signup failed')
                flash(error, 'error')
        except Exception as e:
            flash(f'Connection error: {str(e)}', 'error')
    
    return render_template('auth/signup.html')


@bp.route('/logout')
def logout():
    """Logout user"""
    try:
        requests.post(
            f"{API_BASE_URL}/auth/logout",
            headers={'Authorization': f"Bearer {session.get('access_token')}"}
        )
    except:
        pass
    
    session.clear()
    flash('You have been logged out', 'info')
    return redirect(url_for('auth.login'))


@bp.route('/forgot-password', methods=['GET', 'POST'])
def forgot_password():
    """Forgot password page"""
    if request.method == 'POST':
        email = request.form.get('email')
        # TODO: Implement password reset
        flash('If the email exists, a password reset link will be sent.', 'info')
    
    return render_template('auth/forgot_password.html')


@bp.route('/reset-password/<token>', methods=['GET', 'POST'])
def reset_password(token):
    """Reset password page"""
    if request.method == 'POST':
        password = request.form.get('password')
        password_confirm = request.form.get('password_confirm')
        
        if password != password_confirm:
            flash('Passwords do not match', 'error')
            return render_template('auth/reset_password.html', token=token)
        
        # TODO: Implement password reset with token
        flash('Password reset successful. Please login.', 'success')
        return redirect(url_for('auth.login'))
    
    return render_template('auth/reset_password.html', token=token)
