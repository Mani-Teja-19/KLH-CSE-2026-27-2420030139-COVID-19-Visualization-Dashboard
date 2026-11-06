from datetime import datetime
from flask import Blueprint, jsonify, request
from routes.auth import login_required
from services.stats_calculator import StatsCalculator
from models import Place, Member, CovidCase, Vaccination, Notification

api_bp = Blueprint('api', __name__, url_prefix='/api')

@api_bp.route('/stats/summary')
@login_required
def stats_summary():
    data = StatsCalculator.get_dashboard_summary()
    return jsonify(data)

@api_bp.route('/charts/data')
@login_required
def charts_data():
    data = StatsCalculator.get_analytics_charts_data()
    return jsonify(data)

@api_bp.route('/districts/data')
@login_required
def districts_data():
    data = StatsCalculator.get_district_statistics()
    return jsonify(data)

@api_bp.route('/notifications/unread')
@login_required
def unread_notifications():
    notifs = Notification.query.filter_by(is_read=False).order_by(Notification.created_at.desc()).limit(5).all()
    count = Notification.query.filter_by(is_read=False).count()
    return jsonify({
        'count': count,
        'notifications': [n.to_dict() for n in notifs]
    })

@api_bp.route('/places/search')
@login_required
def search_places():
    query = request.args.get('q', '').strip()
    places = Place.query.filter(Place.place_name.ilike(f'%{query}%')).limit(10).all()
    return jsonify([p.to_dict() for p in places])


# =========================================================================
# STATE-WISE COVID-19 DATASET API ENDPOINTS (Excel Integration)
# =========================================================================

@api_bp.route('/states/data')
@login_required
def states_unified_data():
    """
    Unified endpoint returning summary, charts, and table data for a given state (or All).
    Powers real-time reactive dashboard filtering.
    """
    from services.state_data_service import StateDataService
    state = request.args.get('state', 'All').strip()
    sort_deaths = request.args.get('sort_deaths', 'default').strip()
    search = request.args.get('search', '').strip()
    sort_by = request.args.get('sort_by', 'state_name').strip()
    sort_order = request.args.get('sort_order', 'asc').strip()

    summary = StateDataService.get_summary(state_name=state)
    charts = StateDataService.get_charts_data(state_name=state, sort_deaths=sort_deaths)
    table = StateDataService.get_table_data(state_name=state, search=search, sort_by=sort_by, sort_order=sort_order)

    return jsonify({
        'state': state,
        'summary': summary,
        'charts': charts,
        'table': table
    })


@api_bp.route('/states/summary')
@login_required
def states_summary():
    """Returns dynamic summary metrics for cards."""
    from services.state_data_service import StateDataService
    state = request.args.get('state', 'All').strip()
    data = StateDataService.get_summary(state_name=state)
    return jsonify(data)


@api_bp.route('/states/charts')
@login_required
def states_charts():
    """Returns Chart.js payloads for the 4 state-wise charts."""
    from services.state_data_service import StateDataService
    state = request.args.get('state', 'All').strip()
    sort_deaths = request.args.get('sort_deaths', 'default').strip()
    data = StateDataService.get_charts_data(state_name=state, sort_deaths=sort_deaths)
    return jsonify(data)


@api_bp.route('/states/table')
@login_required
def states_table():
    """Returns table records with search and sort."""
    from services.state_data_service import StateDataService
    state = request.args.get('state', 'All').strip()
    search = request.args.get('search', '').strip()
    sort_by = request.args.get('sort_by', 'state_name').strip()
    sort_order = request.args.get('sort_order', 'asc').strip()
    data = StateDataService.get_table_data(state_name=state, search=search, sort_by=sort_by, sort_order=sort_order)
    return jsonify(data)


@api_bp.route('/states/import', methods=['POST'])
@login_required
def states_import():
    """Triggers dataset re-import / sync from Covid Dashboard.xlsx."""
    from services.state_data_service import StateDataService
    res = StateDataService.import_excel_dataset()
    return jsonify(res)


@api_bp.route('/states/export/excel')
@login_required
def states_export_excel():
    """Exports state-wise dataset as an Excel file (.xlsx)."""
    from flask import send_file
    from services.state_data_service import StateDataService
    state = request.args.get('state', 'All').strip()
    excel_buf = StateDataService.export_excel(state_name=state)
    filename = f"State_wise_COVID_Data_{datetime.utcnow().strftime('%Y%m%d_%H%M')}.xlsx"
    return send_file(
        excel_buf,
        mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
        as_attachment=True,
        download_name=filename
    )


@api_bp.route('/states/export/csv')
@login_required
def states_export_csv():
    """Exports state-wise dataset as a CSV file."""
    from flask import Response
    from services.state_data_service import StateDataService
    state = request.args.get('state', 'All').strip()
    csv_buf = StateDataService.export_csv(state_name=state)
    filename = f"State_wise_COVID_Data_{datetime.utcnow().strftime('%Y%m%d_%H%M')}.csv"
    return Response(
        csv_buf.getvalue(),
        mimetype='text/csv',
        headers={'Content-Disposition': f'attachment; filename="{filename}"'}
    )

