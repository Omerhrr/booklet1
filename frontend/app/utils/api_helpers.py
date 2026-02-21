"""
Common utilities for frontend routes
"""
import requests
import logging
from flask import session, flash, redirect

logger = logging.getLogger(__name__)

API_BASE = 'http://localhost:8000/api/v1'


def get_headers():
    """Get API request headers with auth token"""
    token = session.get('access_token')
    headers = {'Content-Type': 'application/json'}
    if token:
        headers['Authorization'] = f'Bearer {token}'
    return headers


def get_items(data):
    """Extract items from API response - handles both list and dict responses"""
    if data is None:
        return []
    if isinstance(data, list):
        return data
    if isinstance(data, dict):
        return data.get('items', [])
    return []


def handle_api_error(response, action="operation"):
    """Extract error message from API response"""
    try:
        data = response.json()
        if isinstance(data, dict):
            # Try various error message fields
            for key in ['detail', 'message', 'error', 'error_message']:
                if key in data and data[key]:
                    return str(data[key])
            # Check for validation errors
            if 'errors' in data:
                errors = data['errors']
                if isinstance(errors, dict):
                    return '; '.join([f"{k}: {v}" for k, v in errors.items()])
                return str(errors)
        return f"{action} failed (HTTP {response.status_code})"
    except Exception:
        return f"{action} failed - server returned HTTP {response.status_code}"


def api_request(method, endpoint, data=None, params=None, timeout=10):
    """
    Make an API request with proper error handling
    
    Returns:
        tuple: (success: bool, data: dict/list or error_message: str)
    """
    url = f"{API_BASE}{endpoint}"
    headers = get_headers()
    
    try:
        if method.upper() == 'GET':
            response = requests.get(url, headers=headers, params=params, timeout=timeout)
        elif method.upper() == 'POST':
            response = requests.post(url, json=data, headers=headers, timeout=timeout)
        elif method.upper() == 'PUT':
            response = requests.put(url, json=data, headers=headers, timeout=timeout)
        elif method.upper() == 'DELETE':
            response = requests.delete(url, headers=headers, timeout=timeout)
        else:
            return False, f"Unsupported method: {method}"
        
        # Handle common status codes
        if response.status_code in [200, 201]:
            try:
                return True, response.json()
            except:
                return True, {}
        elif response.status_code == 204:
            return True, {}
        elif response.status_code == 401:
            return False, "AUTH_REQUIRED"
        elif response.status_code == 403:
            return False, "You don't have permission for this action"
        elif response.status_code == 404:
            return False, "Resource not found"
        elif response.status_code == 422:
            # Validation error
            try:
                errors = response.json()
                if 'detail' in errors:
                    return False, errors['detail']
                return False, handle_api_error(response, "Validation failed")
            except:
                return False, "Validation error"
        else:
            return False, handle_api_error(response, f"Request to {endpoint}")
            
    except requests.exceptions.ConnectionError:
        logger.error(f"Connection error: {API_BASE}")
        return False, "Cannot connect to server. Please ensure the backend is running on port 8000."
    except requests.exceptions.Timeout:
        logger.error(f"Request timeout: {endpoint}")
        return False, "Request timed out. Please try again."
    except Exception as e:
        logger.error(f"API request error: {e}")
        return False, f"An error occurred: {str(e)}"


def flash_api_result(success, message, success_msg=None):
    """Flash appropriate message based on API result"""
    if success:
        flash(success_msg or message or "Operation successful", 'success')
        return True
    else:
        if message == "AUTH_REQUIRED":
            flash('Please login again', 'error')
            return False
        flash(message, 'error')
        return False
