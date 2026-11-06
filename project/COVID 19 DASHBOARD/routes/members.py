import os
import random
from datetime import datetime
from werkzeug.utils import secure_filename
from flask import Blueprint, render_template, request, redirect, url_for, flash, current_app
from routes.auth import login_required, role_required
from models import db, Member, Place, CovidCase, Vaccination
from services.logger_service import LoggerService

members_bp = Blueprint('members', __name__, url_prefix='/members')

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in current_app.config['ALLOWED_EXTENSIONS']

@members_bp.route('/')
@login_required
def index():
    query = Member.query.join(Place, Member.place_id == Place.id, isouter=True)
    
    # Filters
    search = request.args.get('search', '').strip()
    covid_status = request.args.get('covid_status', '').strip()
    vaccination_status = request.args.get('vaccination_status', '').strip()
    gender = request.args.get('gender', '').strip()
    place_id = request.args.get('place_id', '').strip()
    age_group = request.args.get('age_group', '').strip()
    
    if search:
        query = query.filter(
            (Member.full_name.ilike(f'%{search}%')) |
            (Member.member_code.ilike(f'%{search}%')) |
            (Member.mobile_number.ilike(f'%{search}%')) |
            (Member.aadhaar_number.ilike(f'%{search}%')) |
            (Member.email.ilike(f'%{search}%'))
        )
    if covid_status:
        query = query.filter(Member.covid_status == covid_status)
    if vaccination_status:
        query = query.filter(Member.vaccination_status == vaccination_status)
    if gender:
        query = query.filter(Member.gender == gender)
    if place_id:
        query = query.filter(Member.place_id == int(place_id))
    if age_group:
        if age_group == '0-17':
            query = query.filter(Member.age <= 17)
        elif age_group == '18-44':
            query = query.filter(Member.age >= 18, Member.age <= 44)
        elif age_group == '45-59':
            query = query.filter(Member.age >= 45, Member.age <= 59)
        elif age_group == '60+':
            query = query.filter(Member.age >= 60)

    members = query.order_by(Member.id.desc()).all()
    places = Place.query.order_by(Place.place_name).all()

    return render_template(
        'members/list.html',
        members=members,
        places=places,
        selected_covid=covid_status,
        selected_vax=vaccination_status,
        selected_gender=gender,
        selected_place=place_id,
        selected_age=age_group,
        search=search
    )

@members_bp.route('/create', methods=['GET', 'POST'])
@login_required
def create():
    places = Place.query.order_by(Place.place_name).all()
    
    if request.method == 'POST':
        full_name = request.form.get('full_name', '').strip()
        age = int(request.form.get('age') or 0)
        gender = request.form.get('gender', 'Other')
        dob_str = request.form.get('dob')
        mobile_number = request.form.get('mobile_number', '').strip()
        email = request.form.get('email', '').strip()
        aadhaar_number = request.form.get('aadhaar_number', '').strip()
        address = request.form.get('address', '').strip()
        place_id = request.form.get('place_id')
        occupation = request.form.get('occupation', '').strip()
        
        # Medical & COVID fields
        covid_status = request.form.get('covid_status', 'Negative')
        inf_date_str = request.form.get('infection_date')
        rec_date_str = request.form.get('recovery_date')
        vaccination_status = request.form.get('vaccination_status', 'Not Vaccinated')
        vaccine_name = request.form.get('vaccine_name', '')
        dose1_str = request.form.get('dose1_date')
        dose2_str = request.form.get('dose2_date')
        booster_str = request.form.get('booster_date')
        hospital_name = request.form.get('hospital_name', '').strip()
        doctor_name = request.form.get('doctor_name', '').strip()
        medical_remarks = request.form.get('medical_remarks', '').strip()

        if not full_name or not mobile_number:
            flash('Full Name and Mobile Number are required.', 'danger')
            return render_template('members/form.html', member=None, places=places)

        dob = datetime.strptime(dob_str, '%Y-%m-%d').date() if dob_str else None
        infection_date = datetime.strptime(inf_date_str, '%Y-%m-%d').date() if inf_date_str else None
        recovery_date = datetime.strptime(rec_date_str, '%Y-%m-%d').date() if rec_date_str else None
        dose1_date = datetime.strptime(dose1_str, '%Y-%m-%d').date() if dose1_str else None
        dose2_date = datetime.strptime(dose2_str, '%Y-%m-%d').date() if dose2_str else None
        booster_date = datetime.strptime(booster_str, '%Y-%m-%d').date() if booster_str else None

        # Handle Profile Photo
        photo_filename = 'default-user.png'
        if 'photo' in request.files:
            file = request.files['photo']
            if file and allowed_file(file.filename):
                filename = secure_filename(f"user_{datetime.utcnow().timestamp()}_{file.filename}")
                file.save(os.path.join(current_app.config['UPLOAD_FOLDER'], filename))
                photo_filename = filename

        # Generate unique member code
        new_code = f"MEM-{random.randint(20000, 99999)}"
        while Member.query.filter_by(member_code=new_code).first():
            new_code = f"MEM-{random.randint(20000, 99999)}"

        new_member = Member(
            member_code=new_code,
            full_name=full_name,
            age=age,
            gender=gender,
            dob=dob,
            mobile_number=mobile_number,
            email=email,
            aadhaar_number=aadhaar_number,
            address=address,
            place_id=int(place_id) if place_id else None,
            occupation=occupation,
            covid_status=covid_status,
            infection_date=infection_date,
            recovery_date=recovery_date,
            vaccination_status=vaccination_status,
            vaccine_name=vaccine_name if vaccination_status != 'Not Vaccinated' else None,
            dose1_date=dose1_date,
            dose2_date=dose2_date,
            booster_date=booster_date,
            hospital_name=hospital_name,
            doctor_name=doctor_name,
            medical_remarks=medical_remarks,
            photo_url=photo_filename,
            created_at=datetime.utcnow()
        )
        db.session.add(new_member)
        db.session.commit()

        # If COVID active or positive, create a CovidCase record
        if covid_status in ['Active', 'Positive']:
            new_case = CovidCase(
                case_code=f"COV-{random.randint(100000, 999999)}",
                member_id=new_member.id,
                place_id=new_member.place_id,
                admission_date=infection_date or datetime.utcnow().date(),
                covid_variant="Omicron Variant",
                symptoms="Fever, Cough, Mild Fatigue",
                ct_score="12/25",
                severity="Mild",
                quarantine_status="Home Isolation",
                assigned_doctor=doctor_name or "Dr. Rajesh Kumar",
                notes=medical_remarks or "Initial screening record created."
            )
            db.session.add(new_case)
            db.session.commit()

        # Recalculate place statistics
        if new_member.place:
            new_member.place.recalculate_statistics()
            db.session.commit()

        LoggerService.log_activity('Member Created', 'Member Management', f"Added member '{new_member.full_name}' ({new_member.member_code}).")
        flash(f"Member '{new_member.full_name}' registered successfully with ID {new_member.member_code}!", 'success')
        return redirect(url_for('members.view', id=new_member.id))

    return render_template('members/form.html', member=None, places=places)

@members_bp.route('/<int:id>')
@login_required
def view(id):
    member = Member.query.get_or_404(id)
    return render_template('members/view.html', member=member)

@members_bp.route('/<int:id>/edit', methods=['GET', 'POST'])
@login_required
def edit(id):
    member = Member.query.get_or_404(id)
    places = Place.query.order_by(Place.place_name).all()

    if request.method == 'POST':
        member.full_name = request.form.get('full_name', '').strip()
        member.age = int(request.form.get('age') or 0)
        member.gender = request.form.get('gender', member.gender)
        
        dob_str = request.form.get('dob')
        if dob_str:
            member.dob = datetime.strptime(dob_str, '%Y-%m-%d').date()

        member.mobile_number = request.form.get('mobile_number', '').strip()
        member.email = request.form.get('email', '').strip()
        member.aadhaar_number = request.form.get('aadhaar_number', '').strip()
        member.address = request.form.get('address', '').strip()
        
        old_place_id = member.place_id
        place_id_str = request.form.get('place_id')
        member.place_id = int(place_id_str) if place_id_str else None
        member.occupation = request.form.get('occupation', '').strip()
        
        member.covid_status = request.form.get('covid_status', member.covid_status)
        inf_date_str = request.form.get('infection_date')
        rec_date_str = request.form.get('recovery_date')
        member.infection_date = datetime.strptime(inf_date_str, '%Y-%m-%d').date() if inf_date_str else None
        member.recovery_date = datetime.strptime(rec_date_str, '%Y-%m-%d').date() if rec_date_str else None
        
        member.vaccination_status = request.form.get('vaccination_status', member.vaccination_status)
        member.vaccine_name = request.form.get('vaccine_name', '')
        
        dose1_str = request.form.get('dose1_date')
        dose2_str = request.form.get('dose2_date')
        booster_str = request.form.get('booster_date')
        member.dose1_date = datetime.strptime(dose1_str, '%Y-%m-%d').date() if dose1_str else None
        member.dose2_date = datetime.strptime(dose2_str, '%Y-%m-%d').date() if dose2_str else None
        member.booster_date = datetime.strptime(booster_str, '%Y-%m-%d').date() if booster_str else None

        member.hospital_name = request.form.get('hospital_name', '').strip()
        member.doctor_name = request.form.get('doctor_name', '').strip()
        member.medical_remarks = request.form.get('medical_remarks', '').strip()

        # Check Photo
        if 'photo' in request.files:
            file = request.files['photo']
            if file and allowed_file(file.filename):
                filename = secure_filename(f"user_{datetime.utcnow().timestamp()}_{file.filename}")
                file.save(os.path.join(current_app.config['UPLOAD_FOLDER'], filename))
                member.photo_url = filename

        db.session.commit()

        # Recalculate place statistics
        if member.place:
            member.place.recalculate_statistics()
        if old_place_id and old_place_id != member.place_id:
            old_p = Place.query.get(old_place_id)
            if old_p:
                old_p.recalculate_statistics()
        db.session.commit()

        LoggerService.log_activity('Member Updated', 'Member Management', f"Updated record for '{member.full_name}' ({member.member_code}).")
        flash(f"Member '{member.full_name}' updated successfully!", 'success')
        return redirect(url_for('members.view', id=member.id))

    return render_template('members/form.html', member=member, places=places)

@members_bp.route('/<int:id>/delete', methods=['POST'])
@login_required
@role_required('Admin')
def delete(id):
    member = Member.query.get_or_404(id)
    name = member.full_name
    place = member.place
    db.session.delete(member)
    db.session.commit()
    
    if place:
        place.recalculate_statistics()
        db.session.commit()

    LoggerService.log_activity('Member Deleted', 'Member Management', f"Deleted member '{name}'.")
    flash(f"Member '{name}' has been deleted.", 'info')
    return redirect(url_for('members.index'))
