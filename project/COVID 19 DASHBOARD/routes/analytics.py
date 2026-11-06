from flask import Blueprint, render_template, request
from routes.auth import login_required
from services.stats_calculator import StatsCalculator
from models import Place

analytics_bp = Blueprint('analytics', __name__, url_prefix='/analytics')

@analytics_bp.route('/')
@login_required
def index():
    stats = StatsCalculator.get_dashboard_summary()
    charts_data = StatsCalculator.get_analytics_charts_data()
    districts_data = StatsCalculator.get_district_statistics()
    all_places = Place.query.order_by(Place.place_name).all()

    return render_template(
        'analytics/index.html',
        stats=stats,
        charts_data=charts_data,
        districts_data=districts_data,
        places=all_places
    )
