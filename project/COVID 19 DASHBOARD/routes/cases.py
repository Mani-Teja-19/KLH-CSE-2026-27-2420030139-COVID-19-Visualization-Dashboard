import random
from datetime import datetime
from flask import Blueprint, render_template, request, redirect, url_for, flash
from routes.auth import login_required, role_required
from models import db, CovidCase, Member, Place, Hospital
from services.logger_service import LoggerService

cases_bp = Blueprint('cases', __name__, url_prefix='/cases')

@cases_bp.route('/')
@login_required
def index():
    query = CovidCase.query.join(Member, CovidCase.member_id == Member.id)
    
    # Filters
    search = request.args.get('search', '').strip()
    quarantine = request.args.get('quarantine_status', '').strip()
    severity = request.args.get('severity', '').strip()
    variant = request.args.get('variant', '').strip()
    
    if search:
        query = query.filter(
            (CovidCase.case_code.ilike(f'%{search}%')) |
            (Member.full_name.ilike(f'%{search}%')) |
            (Member.member_code.ilike(f'%{search}%')) |
            (CovidCase.assigned_doctor.ilike(f'%{search}%'))
        )
    if quarantine:
        query = query.filter(CovidCase.quarantine_status == quarantine)
    if severity:
        query = query.filter(CovidCase.severity == severity)
    if variant:
        query = query.filter(CovidCase.covid_variant == variant)

    cases = query.order_by(CovidCase.id.desc()).all()
    
    # Summary metrics for cases header
    active_count = CovidCase.query.filter(CovidCase.quarantine_status.in_(['Home Isolation', 'Hospitalized', 'Oxygen Support', 'ICU'])).count()
    icu_count = CovidCase.query.filter(CovidCase.quarantine_status == 'ICU').count()
    oxygen_count = CovidCase.query.filter(CovidCase.quarantine_status == 'Oxygen Support').count()
    recovered_count = CovidCase.query.filter(CovidCase.quarantine_status == 'Discharged').count()
    deceased_count = CovidCase.query.filter(CovidCase.quarantine_status == 'Deceased').count()

    return render_template(
        'cases/list.html',
        cases=cases,
        active_count=active_count,
        icu_count=icu_count,
        oxygen_count=oxygen_count,
        recovered_count=recovered_count,
        deceased_count=deceased_count,
        selected_quarantine=quarantine,
        selected_severity=severity,
        selected_variant=variant,
        search=search
    )

@cases_bp.route('/create', methods=['GET', 'POST'])
@login_required
def create():
    members = Member.query.order_by(Member.full_name).all()
    places = Place.query.order_by(Place.place_name).all()
    hospitals = Hospital.query.all()
    
    if request.method == 'POST':
        member_id_str = request.form.get('member_id')
        if not member_id_str:
            flash('Please select a member.', 'danger')
            return render_template('cases/form.html', case=None, members=members, places=places, hospitals=hospitals)

        member = Member.query.get(int(member_id_str))
        if not member:
            flash('Selected member not found.', 'danger')
            return redirect(url_for('cases.create'))

        adm_date_str = request.form.get('admission_date')
        adm_date = datetime.strptime(adm_date_str, '%Y-%m-%d').date() if adm_date_str else datetime.utcnow().date()
        
        variant = request.form.get('covid_variant', 'Omicron BA.5')
        symptoms = request.form.get('symptoms', '')
        ct_score = request.form.get('ct_score', '12/25')
        severity = request.form.get('severity', 'Moderate')
        quarantine_status = request.form.get('quarantine_status', 'Home Isolation')
        ward_bed = request.form.get('ward_bed_no', '')
        assigned_doctor = request.form.get('assigned_doctor', '')
        notes = request.form.get('notes', '')

        case_code = f"COV-{random.randint(100000, 999999)}"
        new_case = CovidCase(
            case_code=case_code,
            member_id=member.id,
            place_id=member.place_id,
            admission_date=adm_date,
            covid_variant=variant,
            symptoms=symptoms,
            ct_score=ct_score,
            severity=severity,
            quarantine_status=quarantine_status,
            ward_bed_no=ward_bed,
            assigned_doctor=assigned_doctor,
            notes=notes
        )

        # Update member status
        if quarantine_status in ['Home Isolation', 'Hospitalized', 'Oxygen Support', 'ICU']:
            member.covid_status = 'Active'
            member.infection_date = adm_date
        elif quarantine_status == 'Discharged':
            member.covid_status = 'Recovered'
            member.recovery_date = datetime.utcnow().date()
        elif quarantine_status == 'Deceased':
            member.covid_status = 'Deceased'

        db.session.add(new_case)
        db.session.commit()

        if member.place:
            member.place.recalculate_statistics()
            db.session.commit()

        LoggerService.log_activity('Case Admitted', 'COVID Cases', f"Admitted case {new_case.case_code} for member '{member.full_name}'.")
        flash(f"COVID Case '{new_case.case_code}' registered successfully for {member.full_name}!", 'success')
        return redirect(url_for('cases.view', id=new_case.id))

    return render_template('cases/form.html', case=None, members=members, places=places, hospitals=hospitals)

@cases_bp.route('/<int:id>')
@login_required
def view(id):
    case = CovidCase.query.get_or_404(id)
    return render_template('cases/view.html', case=case)

@cases_bp.route('/<int:id>/edit', methods=['GET', 'POST'])
@login_required
def edit(id):
    case = CovidCase.query.get_or_404(id)
    members = Member.query.order_by(Member.full_name).all()
    places = Place.query.order_by(Place.place_name).all()
    hospitals = Hospital.query.all()

    if request.method == 'POST':
        case.covid_variant = request.form.get('covid_variant', case.covid_variant)
        case.symptoms = request.form.get('symptoms', case.symptoms)
        case.ct_score = request.form.get('ct_score', case.ct_score)
        case.severity = request.form.get('severity', case.severity)
        case.quarantine_status = request.form.get('quarantine_status', case.quarantine_status)
        case.ward_bed_no = request.form.get('ward_bed_no', case.ward_bed_no)
        case.assigned_doctor = request.form.get('assigned_doctor', case.assigned_doctor)
        case.notes = request.form.get('notes', case.notes)

        rec_str = request.form.get('recovery_date')
        death_str = request.form.get('death_date')
        case.recovery_date = datetime.strptime(rec_str, '%Y-%m-%d').date() if rec_str else None
        case.death_date = datetime.strptime(death_str, '%Y-%m-%d').date() if death_str else None

        # Synchronize member status
        if case.member:
            if case.quarantine_status == 'Discharged':
                case.member.covid_status = 'Recovered'
                case.member.recovery_date = case.recovery_date or datetime.utcnow().date()
            elif case.quarantine_status == 'Deceased':
                case.member.covid_status = 'Deceased'
            elif case.quarantine_status in ['Home Isolation', 'Hospitalized', 'Oxygen Support', 'ICU']:
                case.member.covid_status = 'Active'

        db.session.commit()

        if case.place:
            case.place.recalculate_statistics()
            db.session.commit()

        LoggerService.log_activity('Case Updated', 'COVID Cases', f"Updated case {case.case_code}.")
        flash(f"Case '{case.case_code}' updated successfully!", 'success')
        return redirect(url_for('cases.view', id=case.id))

    return render_template('cases/form.html', case=case, members=members, places=places, hospitals=hospitals)

@cases_bp.route('/<int:id>/discharge', methods=['POST'])
@login_required
def discharge(id):
    case = CovidCase.query.get_or_404(id)
    case.quarantine_status = 'Discharged'
    case.recovery_date = datetime.utcnow().date()
    
    if case.member:
        case.member.covid_status = 'Recovered'
        case.member.recovery_date = case.recovery_date
    
    db.session.commit()
    
    if case.place:
        case.place.recalculate_statistics()
        db.session.commit()

    LoggerService.log_activity('Patient Discharged', 'COVID Cases', f"Patient for case {case.case_code} discharged as recovered.")
    flash(f"Patient for case {case.case_code} has been successfully discharged and marked recovered!", 'success')
    return redirect(url_for('cases.view', id=case.id))
