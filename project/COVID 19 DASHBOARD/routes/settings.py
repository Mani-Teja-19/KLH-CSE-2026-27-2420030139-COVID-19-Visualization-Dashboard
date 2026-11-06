from flask import Blueprint, render_template, request, redirect, url_for, flash
from routes.auth import login_required, role_required
from models import db, Setting, ActivityLog
from services.logger_service import LoggerService

settings_bp = Blueprint('settings', __name__, url_prefix='/settings')

@settings_bp.route('/', methods=['GET', 'POST'])
@login_required
@role_required('Admin')
def index():
    if request.method == 'POST':
        app_title = request.form.get('app_title', 'COVID-19 Visualization Portal')
        email_alerts = 'true' if request.form.get('alert_email_notifications') else 'false'
        containment_threshold = request.form.get('containment_threshold_cases', '5')
        default_theme = request.form.get('default_theme', 'dark')
        auto_refresh = request.form.get('auto_refresh_seconds', '60')

        # Update settings
        settings_map = {
            'app_title': app_title,
            'alert_email_notifications': email_alerts,
            'containment_threshold_cases': containment_threshold,
            'default_theme': default_theme,
            'auto_refresh_seconds': auto_refresh
        }

        for key, val in settings_map.items():
            setting = Setting.query.filter_by(setting_key=key).first()
            if setting:
                setting.setting_value = val
            else:
                db.session.add(Setting(setting_key=key, setting_value=val))

        db.session.commit()
        LoggerService.log_activity('Settings Updated', 'System Settings', "Updated application configuration and alert thresholds.")
        flash('System configuration updated successfully!', 'success')
        return redirect(url_for('settings.index'))

    settings_list = Setting.query.all()
    settings_dict = {s.setting_key: s.setting_value for s in settings_list}
    recent_logs = ActivityLog.query.order_by(ActivityLog.created_at.desc()).limit(15).all()

    return render_template('settings/index.html', settings=settings_dict, logs=recent_logs)
