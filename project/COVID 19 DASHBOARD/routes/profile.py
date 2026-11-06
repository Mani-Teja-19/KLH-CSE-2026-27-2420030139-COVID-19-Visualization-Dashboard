import os
from datetime import datetime
from werkzeug.utils import secure_filename
from flask import Blueprint, render_template, request, redirect, url_for, flash, session, current_app
from routes.auth import login_required
from models import db, User, ActivityLog
from services.logger_service import LoggerService

profile_bp = Blueprint('profile', __name__, url_prefix='/profile')

@profile_bp.route('/', methods=['GET', 'POST'])
@login_required
def index():
    user = User.query.get_or_404(session['user_id'])
    
    if request.method == 'POST':
        full_name = request.form.get('full_name', '').strip()
        email = request.form.get('email', '').strip()
        phone = request.form.get('phone', '').strip()
        
        if not full_name or not email:
            flash('Full Name and Email are required.', 'danger')
            return redirect(url_for('profile.index'))

        # Check unique email
        existing = User.query.filter(User.email == email, User.id != user.id).first()
        if existing:
            flash('This email address is already in use by another user.', 'danger')
            return redirect(url_for('profile.index'))

        user.full_name = full_name
        user.email = email
        user.phone = phone
        
        # Handle avatar upload
        if 'avatar' in request.files:
            file = request.files['avatar']
            if file and '.' in file.filename and file.filename.rsplit('.', 1)[1].lower() in current_app.config['ALLOWED_EXTENSIONS']:
                filename = secure_filename(f"avatar_{user.id}_{file.filename}")
                file.save(os.path.join(current_app.config['UPLOAD_FOLDER'], filename))
                user.avatar = filename
                session['user_avatar'] = filename

        db.session.commit()
        session['full_name'] = user.full_name

        LoggerService.log_activity('Profile Updated', 'Profile', f"User {user.username} updated profile info.")
        flash('Your profile details have been successfully updated!', 'success')
        return redirect(url_for('profile.index'))

    # Get user activity logs
    user_logs = ActivityLog.query.filter_by(user_id=user.id).order_by(ActivityLog.created_at.desc()).limit(10).all()
    return render_template('profile/index.html', user=user, user_logs=user_logs)

@profile_bp.route('/change-password', methods=['POST'])
@login_required
def change_password():
    user = User.query.get_or_404(session['user_id'])
    current_password = request.form.get('current_password', '')
    new_password = request.form.get('new_password', '')
    confirm_password = request.form.get('confirm_password', '')

    if not user.check_password(current_password):
        flash('The current password entered is incorrect.', 'danger')
        return redirect(url_for('profile.index'))

    if new_password != confirm_password:
        flash('New password and confirmation do not match.', 'danger')
        return redirect(url_for('profile.index'))

    if len(new_password) < 6:
        flash('New password must be at least 6 characters long.', 'danger')
        return redirect(url_for('profile.index'))

    user.set_password(new_password)
    db.session.commit()

    LoggerService.log_activity('Password Changed', 'Profile', f"User {user.username} changed account password.")
    flash('Your password has been changed successfully!', 'success')
    return redirect(url_for('profile.index'))
