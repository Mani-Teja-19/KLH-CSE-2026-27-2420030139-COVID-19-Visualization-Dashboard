from datetime import datetime
from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from routes.auth import login_required, role_required
from models import db, Place, Member
from services.logger_service import LoggerService

places_bp = Blueprint('places', __name__, url_prefix='/places')

@places_bp.route('/')
@login_required
def index():
    query = Place.query
    
    # Filter parameters
    search = request.args.get('search', '').strip()
    district = request.args.get('district', '').strip()
    status = request.args.get('status', '').strip()
    
    if search:
        query = query.filter(
            (Place.place_name.ilike(f'%{search}%')) |
            (Place.village_city.ilike(f'%{search}%')) |
            (Place.pincode.ilike(f'%{search}%'))
        )
    if district:
        query = query.filter(Place.district == district)
    if status:
        query = query.filter(Place.affected_status == status)

    places = query.order_by(Place.positive_cases.desc(), Place.place_name.asc()).all()
    
    # Get distinct districts for filter dropdown
    districts = [d[0] for d in db.session.query(Place.district).distinct().all() if d[0]]

    return render_template(
        'places/list.html',
        places=places,
        districts=districts,
        selected_district=district,
        selected_status=status,
        search=search
    )

@places_bp.route('/create', methods=['GET', 'POST'])
@login_required
def create():
    if request.method == 'POST':
        place_name = request.form.get('place_name', '').strip()
        village_city = request.form.get('village_city', '').strip()
        mandal_taluk = request.form.get('mandal_taluk', '').strip()
        district = request.form.get('district', '').strip()
        state = request.form.get('state', 'State').strip()
        pincode = request.form.get('pincode', '').strip()
        total_population = int(request.form.get('total_population') or 0)
        total_families = int(request.form.get('total_families') or 0)
        
        if not place_name or not district or not pincode:
            flash('Place Name, District, and Pincode are required.', 'danger')
            return render_template('places/form.html', place=None)

        new_place = Place(
            place_name=place_name,
            village_city=village_city,
            mandal_taluk=mandal_taluk,
            district=district,
            state=state,
            pincode=pincode,
            total_population=total_population,
            total_families=total_families,
            affected_status='Not Affected',
            positive_cases=0,
            active_cases=0,
            recovered_cases=0,
            death_cases=0,
            vaccinated_count=0,
            not_vaccinated_count=0,
            last_updated=datetime.utcnow()
        )
        
        db.session.add(new_place)
        db.session.commit()
        
        LoggerService.log_activity('Place Created', 'Place Management', f"Created place '{new_place.place_name}' ({new_place.district}).")
        flash(f"Place '{new_place.place_name}' has been successfully added!", 'success')
        return redirect(url_for('places.index'))

    return render_template('places/form.html', place=None)

@places_bp.route('/<int:id>')
@login_required
def view(id):
    place = Place.query.get_or_404(id)
    members = Member.query.filter_by(place_id=place.id).all()
    place.recalculate_statistics()
    db.session.commit()
    return render_template('places/view.html', place=place, members=members)

@places_bp.route('/<int:id>/edit', methods=['GET', 'POST'])
@login_required
def edit(id):
    place = Place.query.get_or_404(id)
    
    if request.method == 'POST':
        place.place_name = request.form.get('place_name', '').strip()
        place.village_city = request.form.get('village_city', '').strip()
        place.mandal_taluk = request.form.get('mandal_taluk', '').strip()
        place.district = request.form.get('district', '').strip()
        place.state = request.form.get('state', 'State').strip()
        place.pincode = request.form.get('pincode', '').strip()
        place.total_population = int(request.form.get('total_population') or 0)
        place.total_families = int(request.form.get('total_families') or 0)
        
        place.recalculate_statistics()
        db.session.commit()
        
        LoggerService.log_activity('Place Updated', 'Place Management', f"Updated place details for '{place.place_name}'.")
        flash(f"Place '{place.place_name}' updated successfully!", 'success')
        return redirect(url_for('places.view', id=place.id))

    return render_template('places/form.html', place=place)

@places_bp.route('/<int:id>/delete', methods=['POST'])
@login_required
@role_required('Admin')
def delete(id):
    place = Place.query.get_or_404(id)
    place_name = place.place_name
    db.session.delete(place)
    db.session.commit()
    
    LoggerService.log_activity('Place Deleted', 'Place Management', f"Deleted place '{place_name}'.")
    flash(f"Place '{place_name}' has been deleted.", 'info')
    return redirect(url_for('places.index'))
