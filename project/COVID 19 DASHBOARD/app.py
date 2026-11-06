import os
from flask import Flask, render_template, session
from config import Config
from models import db, Notification, Setting, User

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    # Ensure directories exist
    db_dir = os.path.join(os.path.abspath(os.path.dirname(__file__)), 'database')
    os.makedirs(db_dir, exist_ok=True)
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

    # Initialize extensions
    db.init_app(app)

    # Register Blueprints
    from routes.auth import auth_bp
    from routes.dashboard import dashboard_bp
    from routes.places import places_bp
    from routes.members import members_bp
    from routes.cases import cases_bp
    from routes.vaccinations import vaccinations_bp
    from routes.analytics import analytics_bp
    from routes.reports import reports_bp
    from routes.notifications import notifications_bp
    from routes.profile import profile_bp
    from routes.settings import settings_bp
    from routes.api import api_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(dashboard_bp)
    app.register_blueprint(places_bp)
    app.register_blueprint(members_bp)
    app.register_blueprint(cases_bp)
    app.register_blueprint(vaccinations_bp)
    app.register_blueprint(analytics_bp)
    app.register_blueprint(reports_bp)
    app.register_blueprint(notifications_bp)
    app.register_blueprint(profile_bp)
    app.register_blueprint(settings_bp)
    app.register_blueprint(api_bp)

    # Global Context Processor
    @app.context_processor
    def inject_global_vars():
        unread_notif_count = 0
        recent_notifs = []
        app_title = "COVID-19 Health & Visualization Dashboard"
        current_user = None

        try:
            if 'user_id' in session:
                unread_notif_count = Notification.query.filter_by(is_read=False).count()
                recent_notifs = Notification.query.order_by(Notification.created_at.desc()).limit(5).all()
                current_user = User.query.get(session['user_id'])
            
            title_setting = Setting.query.filter_by(setting_key='app_title').first()
            if title_setting:
                app_title = title_setting.setting_value
        except Exception:
            pass

        return dict(
            unread_notif_count=unread_notif_count,
            recent_notifs=recent_notifs,
            app_title=app_title,
            current_user=current_user
        )

    # Error Handlers
    @app.errorhandler(404)
    def not_found_error(error):
        return render_template('errors/404.html'), 404

    @app.errorhandler(500)
    def internal_error(error):
        db.session.rollback()
        return render_template('errors/500.html'), 500

    # Ensure tables exist and import state dataset on start
    with app.app_context():
        try:
            db.create_all()
            from models import StateCovidData
            from services.state_data_service import StateDataService
            if StateCovidData.query.count() == 0:
                StateDataService.import_excel_dataset()
        except Exception as e:
            app.logger.warning(f"Initial state dataset check/import notice: {e}")

    return app

if __name__ == '__main__':
    application = create_app()
    application.run(host='0.0.0.0', port=5000, debug=True)
