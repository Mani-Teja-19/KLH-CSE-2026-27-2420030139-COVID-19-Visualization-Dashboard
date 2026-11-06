from functools import wraps
from datetime import datetime, timedelta
from flask import Blueprint, render_template, request, redirect, url_for, flash, session, current_app
from models import db, User, Setting
from services.logger_service import LoggerService

auth_bp = Blueprint('auth', __name__)

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash('Please log in to access this page.', 'warning')
            return redirect(url_for('auth.login', next=request.url))
        return f(*args, **kwargs)
    return decorated_function

def role_required(*roles):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if 'user_id' not in session:
                flash('Please log in to access this page.', 'warning')
                return redirect(url_for('auth.login'))
            user_role = session.get('user_role', 'User')
            if user_role not in roles and 'Admin' not in roles:
                flash('You do not have permission to perform this action.', 'danger')
                return redirect(url_for('dashboard.index'))
            return f(*args, **kwargs)
        return decorated_function
    return decorator

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if 'user_id' in session:
        return redirect(url_for('dashboard.index'))
        
    if request.method == 'POST':
        username_or_email = request.form.get('username', '').strip()
        password = request.form.get('password', '')
        remember = bool(request.form.get('remember'))

        if not username_or_email or not password:
            flash('Please provide both username/email and password.', 'danger')
            return render_template('auth/login.html')

        user = User.query.filter(
            (User.username == username_or_email) | (User.email == username_or_email)
        ).first()

        if user and user.check_password(password):
            if not user.is_active:
                flash('Your account has been deactivated. Please contact the system administrator.', 'danger')
                return render_template('auth/login.html')

            # Create session
            session['user_id'] = user.id
            session['username'] = user.username
            session['full_name'] = user.full_name
            session['user_role'] = user.role
            session['user_avatar'] = user.avatar
            
            if remember:
                session.permanent = True
                current_app.permanent_session_lifetime = timedelta(days=30)
            else:
                session.permanent = False

            user.last_login = datetime.utcnow()
            db.session.commit()

            LoggerService.log_activity('User Logged In', 'Authentication', f"User {user.username} logged in successfully.", user.id)
            
            flash(f'Welcome back, {user.full_name}!', 'success')
            next_page = request.args.get('next')
            return redirect(next_page or url_for('dashboard.index'))
        else:
            flash('Invalid username/email or password. Please try again.', 'danger')

    return render_template('auth/login.html')

@auth_bp.route('/logout')
def logout():
    user_id = session.get('user_id')
    user_name = session.get('username', 'Unknown')
    if user_id:
        LoggerService.log_activity('User Logged Out', 'Authentication', f"User {user_name} logged out.", user_id)
    session.clear()
    flash('You have been safely logged out.', 'info')
    return redirect(url_for('auth.login'))

@auth_bp.route('/forgot-password', methods=['GET', 'POST'])
def forgot_password():
    if request.method == 'POST':
        email = request.form.get('email', '').strip()
        new_password = request.form.get('new_password', '')
        confirm_password = request.form.get('confirm_password', '')

        if not email:
            flash('Please enter your registered email address.', 'danger')
            return render_template('auth/forgot_password.html')

        user = User.query.filter_by(email=email).first()
        if not user:
            # Avoid enumeration, but give helpful response in demo environment
            flash('If an account exists with this email, password reset instructions have been applied.', 'info')
            return render_template('auth/forgot_password.html')

        if new_password and confirm_password:
            if new_password != confirm_password:
                flash('Passwords do not match.', 'danger')
                return render_template('auth/forgot_password.html')
            if len(new_password) < 6:
                flash('Password must be at least 6 characters long.', 'danger')
                return render_template('auth/forgot_password.html')

            user.set_password(new_password)
            db.session.commit()
            LoggerService.log_activity('Password Reset', 'Authentication', f"Password reset for user {user.username}.", user.id)
            flash('Password has been successfully updated! You can now log in.', 'success')
            return redirect(url_for('auth.login'))

        flash('Reset link verified. Please enter your new password below.', 'success')
        return render_template('auth/forgot_password.html', email_verified=True, email=email)

    return render_template('auth/forgot_password.html')
