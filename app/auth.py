"""
Authentication utilities and decorators for role-based access control
"""
from functools import wraps
from flask import session, redirect, url_for, flash
from app.models import User, UserRole

def login_required(f):
    """Decorator to require login"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash('Please log in first', 'warning')
            return redirect(url_for('routes.index'))
        return f(*args, **kwargs)
    return decorated_function

def role_required(*allowed_roles):
    """Decorator to require specific user roles"""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if 'user_id' not in session:
                flash('Please log in first', 'warning')
                return redirect(url_for('login'))
            
            if session.get('user_role') not in allowed_roles:
                flash('You do not have permission to access this page', 'danger')
                return redirect(url_for('index'))
            
            return f(*args, **kwargs)
        return decorated_function
    return decorator

def get_current_user():
    """Get the current logged-in user"""
    user_id = session.get('user_id')
    if user_id:
        return User.query.get(user_id)
    return None

def get_current_doctor():
    """Get the current logged-in doctor"""
    from app.models import Doctor
    user = get_current_user()
    if user and user.doctor:
        return user.doctor
    return None

def get_current_admin():
    """Get the current logged-in admin"""
    from app.models import Admin
    user = get_current_user()
    if user and user.admin:
        return user.admin
    return None

def get_current_patient():
    """Get the current logged-in patient"""
    from app.models import Patient
    user = get_current_user()
    if user and user.patient:
        return user.patient
    return None

def get_current_asha_worker():
    """Get the current logged-in Asha Worker"""
    from app.models import AshaWorker
    user = get_current_user()
    if user and user.asha_worker:
        return user.asha_worker
    return None
