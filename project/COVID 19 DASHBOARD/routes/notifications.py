from datetime import datetime
from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from routes.auth import login_required, role_required
from models import db, Notification
from services.logger_service import LoggerService

notifications_bp = Blueprint('notifications', __name__, url_prefix='/notifications')

@notifications_bp.route('/')
@login_required
def index():
    category = request.args.get('category', '').strip()
    status = request.args.get('status', '').strip()
    
    query = Notification.query
    if category:
        query = query.filter(Notification.category == category)
    if status == 'unread':
        query = query.filter(Notification.is_read == False)
        
    notifications = query.order_by(Notification.created_at.desc()).all()
    unread_count = Notification.query.filter_by(is_read=False).count()

    return render_template(
        'notifications/index.html',
        notifications=notifications,
        unread_count=unread_count,
        selected_category=category,
        selected_status=status
    )

@notifications_bp.route('/<int:id>/read', methods=['POST'])
@login_required
def mark_read(id):
    notif = Notification.query.get_or_404(id)
    notif.is_read = True
    db.session.commit()
    return jsonify({'success': True, 'id': id})

@notifications_bp.route('/mark-all-read', methods=['POST'])
@login_required
def mark_all_read():
    Notification.query.update({Notification.is_read: True})
    db.session.commit()
    flash('All notifications have been marked as read.', 'success')
    return redirect(url_for('notifications.index'))

@notifications_bp.route('/create', methods=['POST'])
@login_required
@role_required('Admin')
def create():
    title = request.form.get('title', '').strip()
    message = request.form.get('message', '').strip()
    category = request.form.get('category', 'General')
    alert_level = request.form.get('alert_level', 'Medium')
    target_url = request.form.get('target_url', '')

    if not title or not message:
        flash('Title and message are required to broadcast an alert.', 'danger')
        return redirect(url_for('notifications.index'))

    notif = Notification(
        title=title,
        message=message,
        category=category,
        alert_level=alert_level,
        target_url=target_url or '/dashboard',
        created_at=datetime.utcnow()
    )
    db.session.add(notif)
    db.session.commit()

    LoggerService.log_activity('Alert Broadcasted', 'Notifications', f"Broadcasted alert: '{title}' ({alert_level}).")
    flash('Emergency notification successfully broadcasted across the dashboard!', 'success')
    return redirect(url_for('notifications.index'))
