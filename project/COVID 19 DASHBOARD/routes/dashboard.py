from flask import Blueprint, render_template, session
from routes.auth import login_required
from services.stats_calculator import StatsCalculator
from services.state_data_service import StateDataService
from models import CovidCase, Place, Notification, ActivityLog, Hospital, StateCovidData

dashboard_bp = Blueprint('dashboard', __name__)

@dashboard_bp.route('/')
@dashboard_bp.route('/dashboard')
@login_required
def index():
    stats = StatsCalculator.get_dashboard_summary()
    charts_data = StatsCalculator.get_analytics_charts_data()
    districts = StatsCalculator.get_district_statistics()
    
    # State-wise Surveillance Data (from Excel dataset)
    state_summary = StateDataService.get_summary('All')
    state_charts_data = StateDataService.get_charts_data('All')
    state_table_data = StateDataService.get_table_data('All')
    states_list = [s.state_name for s in StateCovidData.query.order_by(StateCovidData.state_name.asc()).all()]

    # Recent Active/Severe Cases
    recent_cases = CovidCase.query.order_by(CovidCase.id.desc()).limit(6).all()
    
    # Active high-priority notifications
    high_alerts = Notification.query.filter(
        Notification.alert_level.in_(['High', 'Emergency'])
    ).order_by(Notification.created_at.desc()).limit(3).all()
    
    # Recent Activity Logs
    recent_logs = ActivityLog.query.order_by(ActivityLog.created_at.desc()).limit(5).all()
    
    # Hospitals list
    hospitals = Hospital.query.all()

    return render_template(
        'dashboard/index.html',
        stats=stats,
        charts_data=charts_data,
        districts=districts,
        state_summary=state_summary,
        state_charts_data=state_charts_data,
        state_table_data=state_table_data,
        states_list=states_list,
        recent_cases=recent_cases,
        high_alerts=high_alerts,
        recent_logs=recent_logs,
        hospitals=hospitals
    )
