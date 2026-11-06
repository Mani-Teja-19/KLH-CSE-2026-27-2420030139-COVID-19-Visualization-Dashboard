from datetime import datetime
from flask import request, session
from models import db, ActivityLog, Notification

class LoggerService:
    @staticmethod
    def log_activity(action, module, details="", user_id=None):
        """Logs an admin or user activity to the database."""
        try:
            if not user_id and 'user_id' in session:
                user_id = session['user_id']
            
            ip_addr = request.remote_addr if request else '127.0.0.1'
            log_entry = ActivityLog(
                user_id=user_id,
                action=action,
                module=module,
                details=details,
                ip_address=ip_addr,
                created_at=datetime.utcnow()
            )
            db.session.add(log_entry)
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            print(f"Failed to log activity: {e}")

    @staticmethod
    def create_notification(title, message, category='General', alert_level='Medium', target_url=None):
        """Creates a dashboard notification."""
        try:
            notif = Notification(
                title=title,
                message=message,
                category=category,
                alert_level=alert_level,
                target_url=target_url,
                created_at=datetime.utcnow()
            )
            db.session.add(notif)
            db.session.commit()
            return notif
        except Exception as e:
            db.session.rollback()
            print(f"Failed to create notification: {e}")
            return None
