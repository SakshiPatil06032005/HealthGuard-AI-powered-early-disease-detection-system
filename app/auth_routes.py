"""
Authentication routes for login, logout, registration
"""
from flask import Blueprint, render_template, request, session, redirect, url_for, flash, jsonify
from app.models import db, User, Admin, Doctor, Patient, AshaWorker
from app.auth import get_current_user, login_required, role_required

auth = Blueprint('auth', __name__, url_prefix='/auth')

@auth.route('/login', methods=['GET', 'POST'])
def login():
    """Handle user login"""
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '').strip()
        
        if not username or not password:
            flash('Username and password are required', 'danger')
            return redirect(url_for('auth.login'))
        
        # Find user by username or email
        user = User.query.filter(
            (User.username == username) | (User.email == username)
        ).first()
        
        if user and user.check_password(password):
            # Login successful
            session['user_id'] = user.id
            session['username'] = user.username
            session['user_role'] = user.role
            session.permanent = True
            
            flash(f'Welcome back, {user.username}!', 'success')
            
            # Redirect based on role
            if user.role == 'admin':
                return redirect(url_for('dashboards.admin_dashboard'))
            elif user.role == 'doctor':
                return redirect(url_for('dashboards.doctor_dashboard'))
            elif user.role == 'patient':
                return redirect(url_for('dashboards.patient_dashboard'))
            elif user.role == 'asha_worker':
                return redirect(url_for('dashboards.asha_dashboard'))
            else:
                return redirect(url_for('routes.index'))
        else:
            flash('Invalid username or password', 'danger')
    
    return render_template('auth/login.html')

@auth.route('/register', methods=['GET', 'POST'])
def register():
    """Handle user registration"""
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        email = request.form.get('email', '').strip()
        password = request.form.get('password', '').strip()
        password_confirm = request.form.get('password_confirm', '').strip()
        role = request.form.get('role', 'patient')
        full_name = request.form.get('full_name', '').strip()
        
        # Validation
        if not all([username, email, password, full_name]):
            flash('All fields are required', 'danger')
            return redirect(url_for('auth.register'))
        
        if len(password) < 6:
            flash('Password must be at least 6 characters', 'danger')
            return redirect(url_for('auth.register'))
        
        if password != password_confirm:
            flash('Passwords do not match', 'danger')
            return redirect(url_for('auth.register'))
        
        # Check if user already exists
        existing_user = User.query.filter(
            (User.username == username) | (User.email == email)
        ).first()
        
        if existing_user:
            flash('Username or email already exists', 'danger')
            return redirect(url_for('auth.register'))
        
        # Only allow patient registration (admin/doctor must be created manually)
        if role not in ['patient']:
            role = 'patient'
        
        # Create new user
        user = User(username=username, email=email, role=role)
        user.set_password(password)
        db.session.add(user)
        db.session.flush()
        
        # Create profile based on role
        if role == 'patient':
            patient = Patient(
                user_id=user.id,
                full_name=full_name,
                age=request.form.get('age', ''),
                gender=request.form.get('gender', ''),
                region=request.form.get('region', '')
            )
            db.session.add(patient)
        
        db.session.commit()
        
        flash('Registration successful! Please log in.', 'success')
        return redirect(url_for('auth.login'))
    
    return render_template('auth/register.html')

@auth.route('/logout', methods=['POST'])
def logout():
    """Handle user logout"""
    session.clear()
    flash('You have been logged out', 'info')
    return redirect(url_for('routes.index'))

@auth.route('/profile', methods=['GET'])
@login_required
def profile():
    """View user profile"""
    user = get_current_user()
    if not user:
        return redirect(url_for('auth.login'))
    
    context = {
        'user': user,
        'admin': user.admin,
        'doctor': user.doctor,
        'patient': user.patient,
    }
    return render_template('auth/profile.html', **context)

@auth.route('/api/check-username', methods=['POST'])
def check_username():
    """Check if username is available (for registration)"""
    data = request.get_json()
    username = data.get('username', '').strip()
    
    if not username:
        return jsonify({'available': False, 'error': 'Username is required'})
    
    existing = User.query.filter_by(username=username).first()
    return jsonify({'available': existing is None})

@auth.route('/api/check-email', methods=['POST'])
def check_email():
    """Check if email is available (for registration)"""
    data = request.get_json()
    email = data.get('email', '').strip()
    
    if not email:
        return jsonify({'available': False, 'error': 'Email is required'})
    
    existing = User.query.filter_by(email=email).first()
    return jsonify({'available': existing is None})

@auth.route('/asha-login', methods=['GET', 'POST'])
def asha_login():
    """Handle Asha Worker login"""
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '').strip()
        
        if not username or not password:
            flash('Email/Username and password are required', 'danger')
            return redirect(url_for('auth.asha_login'))
        
        # Find user by username or email
        user = User.query.filter(
            ((User.username == username) | (User.email == username)) &
            (User.role == 'asha_worker')
        ).first()
        
        if user and user.check_password(password):
            # Login successful
            session['user_id'] = user.id
            session['username'] = user.username
            session['user_role'] = user.role
            session.permanent = True
            
            flash(f'Welcome back, {user.username}!', 'success')
            return redirect(url_for('dashboards.asha_dashboard'))
        else:
            flash('Invalid credentials or not an Asha Worker account', 'danger')
    
    return render_template('auth/asha_login.html')

@auth.route('/asha-signup', methods=['GET', 'POST'])
def asha_signup():
    """Handle Asha Worker registration"""
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        email = request.form.get('email', '').strip()
        password = request.form.get('password', '').strip()
        password_confirm = request.form.get('password_confirm', '').strip()
        full_name = request.form.get('full_name', '').strip()
        asha_worker_id = request.form.get('asha_worker_id', '').strip()
        region = request.form.get('region', '').strip()
        phone = request.form.get('phone', '').strip()
        
        # Validation
        if not all([username, email, password, full_name, asha_worker_id, region]):
            flash('All required fields must be filled', 'danger')
            return redirect(url_for('auth.asha_signup'))
        
        if len(password) < 6:
            flash('Password must be at least 6 characters', 'danger')
            return redirect(url_for('auth.asha_signup'))
        
        if password_confirm and password != password_confirm:
            flash('Passwords do not match', 'danger')
            return redirect(url_for('auth.asha_signup'))
        
        # Check if user already exists
        existing_user = User.query.filter(
            (User.username == username) | (User.email == email)
        ).first()
        
        if existing_user:
            flash('Username or email already exists', 'danger')
            return redirect(url_for('auth.asha_signup'))
        
        # Check if Asha Worker ID already exists
        existing_asha = AshaWorker.query.filter_by(asha_worker_id=asha_worker_id).first()
        if existing_asha:
            flash('Asha Worker ID already exists', 'danger')
            return redirect(url_for('auth.asha_signup'))
        
        try:
            # Create new user
            user = User(username=username, email=email, role='asha_worker')
            user.set_password(password)
            db.session.add(user)
            db.session.flush()
            
            # Create Asha Worker profile
            asha_worker = AshaWorker(
                user_id=user.id,
                full_name=full_name,
                asha_worker_id=asha_worker_id,
                region=region,
                phone=phone
            )
            db.session.add(asha_worker)
            db.session.commit()
            
            flash('Asha Worker registration successful! Please log in.', 'success')
            return redirect(url_for('auth.asha_login'))
        except Exception as e:
            db.session.rollback()
            flash(f'Registration failed: {str(e)}', 'danger')
            return redirect(url_for('auth.asha_signup'))
    
    return render_template('auth/asha_worker_signup.html')

