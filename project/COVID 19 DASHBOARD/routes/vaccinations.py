import random
from datetime import datetime, timedelta
from flask import Blueprint, render_template, request, redirect, url_for, flash
from routes.auth import login_required
from models import db, Vaccination, Member, Hospital
from services.logger_service import LoggerService

vaccinations_bp = Blueprint('vaccinations', __name__, url_prefix='/vaccinations')

@vaccinations_bp.route('/')
@login_required
def index():
    query = Vaccination.query.join(Member, Vaccination.member_id == Member.id)
    
    # Filters
    search = request.args.get('search', '').strip()
    dose = request.args.get('dose', '').strip()
    vaccine = request.args.get('vaccine', '').strip()
    
    if search:
        query = query.filter(
            (Vaccination.certificate_no.ilike(f'%{search}%')) |
            (Member.full_name.ilike(f'%{search}%')) |
            (Member.member_code.ilike(f'%{search}%')) |
            (Vaccination.center_name.ilike(f'%{search}%'))
        )
    if dose:
        query = query.filter(Vaccination.dose_number == int(dose))
    if vaccine:
        query = query.filter(Vaccination.vaccine_name == vaccine)

    vaccinations = query.order_by(Vaccination.id.desc()).all()
    
    # Stats
    dose1_count = Vaccination.query.filter_by(dose_number=1).count()
    dose2_count = Vaccination.query.filter_by(dose_number=2).count()
    booster_count = Vaccination.query.filter_by(dose_number=3).count()
    total_doses = dose1_count + dose2_count + booster_count

    return render_template(
        'vaccinations/list.html',
        vaccinations=vaccinations,
        dose1_count=dose1_count,
        dose2_count=dose2_count,
        booster_count=booster_count,
        total_doses=total_doses,
        selected_dose=dose,
        selected_vaccine=vaccine,
        search=search
    )

@vaccinations_bp.route('/create', methods=['GET', 'POST'])
@login_required
def create():
    members = Member.query.order_by(Member.full_name).all()
    hospitals = Hospital.query.all()
    
    if request.method == 'POST':
        member_id_str = request.form.get('member_id')
        if not member_id_str:
            flash('Please select a member.', 'danger')
            return render_template('vaccinations/form.html', members=members, hospitals=hospitals)

        member = Member.query.get(int(member_id_str))
        if not member:
            flash('Selected member not found.', 'danger')
            return redirect(url_for('vaccinations.create'))

        dose_number = int(request.form.get('dose_number') or 1)
        vaccine_name = request.form.get('vaccine_name', 'Covishield')
        vax_date_str = request.form.get('vaccination_date')
        vax_date = datetime.strptime(vax_date_str, '%Y-%m-%d').date() if vax_date_str else datetime.utcnow().date()
        center_name = request.form.get('center_name', '').strip()
        batch_number = request.form.get('batch_number', f"VAC-B{random.randint(100, 999)}").strip()
        vaccinated_by = request.form.get('vaccinated_by', 'Health Officer').strip()

        # Certificate number
        cert_no = f"COV-VAX-{random.randint(10000, 99999)}"
        while Vaccination.query.filter_by(certificate_no=cert_no).first():
            cert_no = f"COV-VAX-{random.randint(10000, 99999)}"

        next_due = None
        if dose_number == 1:
            next_due = vax_date + timedelta(days=84)
            member.vaccination_status = 'Partially Vaccinated'
            member.dose1_date = vax_date
            member.vaccine_name = vaccine_name
        elif dose_number == 2:
            next_due = vax_date + timedelta(days=180)
            member.vaccination_status = 'Fully Vaccinated'
            member.dose2_date = vax_date
            member.vaccine_name = vaccine_name
        elif dose_number == 3:
            member.vaccination_status = 'Fully Vaccinated'
            member.booster_date = vax_date

        new_vax = Vaccination(
            member_id=member.id,
            dose_number=dose_number,
            vaccine_name=vaccine_name,
            vaccination_date=vax_date,
            center_name=center_name,
            batch_number=batch_number,
            vaccinated_by=vaccinated_by,
            certificate_no=cert_no,
            next_due_date=next_due
        )

        db.session.add(new_vax)
        db.session.commit()

        if member.place:
            member.place.recalculate_statistics()
            db.session.commit()

        LoggerService.log_activity('Vaccination Recorded', 'Vaccination Management', f"Administered Dose {dose_number} to {member.full_name} ({vaccine_name}).")
        flash(f"Vaccination successfully recorded for {member.full_name}! Certificate generated: {cert_no}", 'success')
        return redirect(url_for('vaccinations.certificate', id=new_vax.id))

    return render_template('vaccinations/form.html', members=members, hospitals=hospitals)

@vaccinations_bp.route('/<int:id>/certificate')
@login_required
def certificate(id):
    vax = Vaccination.query.get_or_404(id)
    return render_template('vaccinations/certificate.html', vax=vax)
