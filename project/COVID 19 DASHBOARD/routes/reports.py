from datetime import datetime, timedelta
from flask import Blueprint, render_template, request, make_response, Response
from routes.auth import login_required
from models import db, Place, Member, CovidCase, Vaccination, Hospital
from services.export_service import ExportService
from services.stats_calculator import StatsCalculator
from services.logger_service import LoggerService

reports_bp = Blueprint('reports', __name__, url_prefix='/reports')

def get_report_dataset(report_type, district_filter=None, status_filter=None, date_from=None, date_to=None):
    """Fetches headers, rows, and summary object for any report type."""
    summary = {}
    
    if report_type == 'place_wise':
        title = "Place-wise COVID-19 Health Summary"
        headers = ["Place Name", "Village/City", "District", "Population", "Affected Status", "Positive Cases", "Active Cases", "Recovered", "Deaths", "Vaccinated Count"]
        query = Place.query
        if district_filter:
            query = query.filter(Place.district == district_filter)
        if status_filter:
            query = query.filter(Place.affected_status == status_filter)
        places = query.order_by(Place.positive_cases.desc()).all()
        
        rows = [
            [p.place_name, p.village_city, p.district, p.total_population, p.affected_status, p.positive_cases, p.active_cases, p.recovered_cases, p.death_cases, p.vaccinated_count]
            for p in places
        ]
        summary = {
            "Total Places": len(places),
            "Affected Places": sum(1 for p in places if p.affected_status == 'Affected'),
            "Total Positive Cases": sum(p.positive_cases for p in places),
            "Total Deaths": sum(p.death_cases for p in places)
        }

    elif report_type == 'district_wise':
        title = "District-wise Epidemiological Report"
        headers = ["District Name", "Places Count", "Total Population", "Positive Cases", "Active Cases", "Recovered", "Deaths", "Vaccinated Count"]
        dist_stats = StatsCalculator.get_district_statistics()
        if district_filter:
            dist_stats = [d for d in dist_stats if d['district'] == district_filter]
        rows = [
            [d['district'], d['place_count'], d['population'], d['positive'], d['active'], d['recovered'], d['deaths'], d['vaccinated']]
            for d in dist_stats
        ]
        summary = {
            "Districts Monitored": len(dist_stats),
            "Total Cases": sum(d['positive'] for d in dist_stats),
            "Active Cases": sum(d['active'] for d in dist_stats),
            "Total Deaths": sum(d['deaths'] for d in dist_stats)
        }

    elif report_type == 'vaccination':
        title = "Vaccination Drive & Coverage Report"
        headers = ["Certificate No", "Member Name", "Member Code", "Dose", "Vaccine Name", "Vaccination Date", "Center Name", "Vaccinated By"]
        query = Vaccination.query.join(Member, Vaccination.member_id == Member.id)
        if date_from:
            query = query.filter(Vaccination.vaccination_date >= date_from)
        if date_to:
            query = query.filter(Vaccination.vaccination_date <= date_to)
        vaxes = query.order_by(Vaccination.id.desc()).all()
        rows = [
            [v.certificate_no, v.member.full_name if v.member else 'N/A', v.member.member_code if v.member else 'N/A', f"Dose {v.dose_number}", v.vaccine_name, v.vaccination_date.strftime('%Y-%m-%d'), v.center_name, v.vaccinated_by or 'Staff']
            for v in vaxes
        ]
        summary = {
            "Total Doses Administered": len(vaxes),
            "Dose 1 Count": sum(1 for v in vaxes if v.dose_number == 1),
            "Dose 2 Count": sum(1 for v in vaxes if v.dose_number == 2),
            "Booster Count": sum(1 for v in vaxes if v.dose_number == 3)
        }

    elif report_type == 'active_cases':
        title = "Active COVID-19 Cases & Hospitalization Report"
        headers = ["Case Code", "Patient Name", "Age", "Gender", "District", "Severity", "Quarantine Status", "Ward/Bed", "Doctor", "Admission Date"]
        query = CovidCase.query.join(Member, CovidCase.member_id == Member.id).filter(
            CovidCase.quarantine_status.in_(['Home Isolation', 'Hospitalized', 'Oxygen Support', 'ICU'])
        )
        cases = query.order_by(CovidCase.admission_date.desc()).all()
        rows = [
            [c.case_code, c.member.full_name, c.member.age, c.member.gender, c.place.district if c.place else 'N/A', c.severity, c.quarantine_status, c.ward_bed_no or 'N/A', c.assigned_doctor or 'N/A', c.admission_date.strftime('%Y-%m-%d')]
            for c in cases
        ]
        summary = {
            "Total Active Cases": len(cases),
            "Home Isolation": sum(1 for c in cases if c.quarantine_status == 'Home Isolation'),
            "Hospitalized": sum(1 for c in cases if c.quarantine_status == 'Hospitalized'),
            "ICU / Oxygen Support": sum(1 for c in cases if c.quarantine_status in ['ICU', 'Oxygen Support'])
        }

    elif report_type == 'deaths':
        title = "COVID-19 Mortality & Deceased Patients Report"
        headers = ["Case Code", "Patient Name", "Age", "Gender", "District", "Variant", "Hospital", "Infection Date", "Death Date"]
        cases = CovidCase.query.join(Member, CovidCase.member_id == Member.id).filter(
            CovidCase.quarantine_status == 'Deceased'
        ).order_by(CovidCase.id.desc()).all()
        rows = [
            [c.case_code, c.member.full_name, c.member.age, c.member.gender, c.place.district if c.place else 'N/A', c.covid_variant, c.member.hospital_name or 'City Hospital', c.member.infection_date.strftime('%Y-%m-%d') if c.member.infection_date else 'N/A', c.death_date.strftime('%Y-%m-%d') if c.death_date else 'N/A']
            for c in cases
        ]
        summary = {
            "Total Deceased Cases": len(cases),
            "Senior Citizens (60+)": sum(1 for c in cases if c.member.age >= 60),
            "Under 60": sum(1 for c in cases if c.member.age < 60)
        }

    elif report_type == 'recoveries':
        title = "COVID-19 Successful Recoveries Report"
        headers = ["Case Code", "Patient Name", "Age", "Gender", "District", "Hospital", "Admission Date", "Recovery Date"]
        cases = CovidCase.query.join(Member, CovidCase.member_id == Member.id).filter(
            CovidCase.quarantine_status == 'Discharged'
        ).order_by(CovidCase.recovery_date.desc()).all()
        rows = [
            [c.case_code, c.member.full_name, c.member.age, c.member.gender, c.place.district if c.place else 'N/A', c.member.hospital_name or 'Healthcare Center', c.admission_date.strftime('%Y-%m-%d'), c.recovery_date.strftime('%Y-%m-%d') if c.recovery_date else 'N/A']
            for c in cases
        ]
        summary = {
            "Total Recovered Patients": len(cases),
            "Male Recovered": sum(1 for c in cases if c.member.gender == 'Male'),
            "Female Recovered": sum(1 for c in cases if c.member.gender == 'Female')
        }

    elif report_type == 'state_wise':
        from services.state_data_service import StateDataService
        title = "State-wise COVID-19 Surveillance Report"
        headers = ["State / UT", "Population", "Affected (Cases)", "Non-Affected", "Active Cases", "Recovered", "Deaths", "Vaccinated", "Non-Vaccinated"]
        state_data = StateDataService.get_table_data()
        rows = [
            [
                r['state_name'],
                f"{r['population']:,}",
                f"{r['affected']:,}",
                f"{r['non_affected']:,}",
                f"{r['active']:,}",
                f"{r['recovered']:,}",
                f"{r['deaths']:,}",
                r['vaccinated'] if r['vaccinated'] is not None else "Vaccination data not available",
                r['non_vaccinated'] if r['non_vaccinated'] is not None else "Vaccination data not available"
            ]
            for r in state_data['rows']
        ]
        totals = state_data['totals']
        summary = {
            "Monitored States/UTs": len(state_data['rows']),
            "Total Population": f"{totals['population']:,}",
            "Total Affected": f"{totals['affected']:,}",
            "Total Deaths": f"{totals['deaths']:,}"
        }


    else:  # 'members' or default
        title = "Comprehensive Citizen Health Directory"
        headers = ["Member ID", "Full Name", "Age", "Gender", "Place", "District", "COVID Status", "Vaccination Status", "Vaccine Name", "Mobile"]
        query = Member.query.join(Place, Member.place_id == Place.id, isouter=True)
        if district_filter:
            query = query.filter(Place.district == district_filter)
        if status_filter:
            query = query.filter(Member.covid_status == status_filter)
        members = query.order_by(Member.id.desc()).all()
        rows = [
            [m.member_code, m.full_name, m.age, m.gender, m.place.place_name if m.place else 'N/A', m.place.district if m.place else 'N/A', m.covid_status, m.vaccination_status, m.vaccine_name or 'N/A', m.mobile_number]
            for m in members
        ]
        summary = {
            "Total Citizens Registered": len(members),
            "Fully Vaccinated": sum(1 for m in members if m.vaccination_status == 'Fully Vaccinated'),
            "COVID Positive (Lifetime)": sum(1 for m in members if m.covid_status in ['Positive', 'Active', 'Recovered', 'Deceased']),
            "Currently Negative": sum(1 for m in members if m.covid_status == 'Negative')
        }

    return title, headers, rows, summary

@reports_bp.route('/')
@login_required
def index():
    report_type = request.args.get('type', 'place_wise')
    district = request.args.get('district', '')
    status = request.args.get('status', '')
    
    title, headers, rows, summary = get_report_dataset(report_type, district, status)
    districts = [d[0] for d in db.session.query(Place.district).distinct().all() if d[0]]

    return render_template(
        'reports/index.html',
        report_type=report_type,
        title=title,
        headers=headers,
        rows=rows,
        summary=summary,
        districts=districts,
        selected_district=district,
        selected_status=status
    )

@reports_bp.route('/export/pdf')
@login_required
def export_pdf():
    report_type = request.args.get('type', 'place_wise')
    district = request.args.get('district', '')
    status = request.args.get('status', '')
    
    title, headers, rows, summary = get_report_dataset(report_type, district, status)
    pdf_bytes = ExportService.generate_pdf(title, headers, rows, summary)
    
    LoggerService.log_activity('Report Exported (PDF)', 'Reports', f"Exported PDF for '{title}'.")
    
    response = make_response(pdf_bytes)
    response.headers['Content-Type'] = 'application/pdf'
    response.headers['Content-Disposition'] = f'attachment; filename="covid19_{report_type}_report.pdf"'
    return response

@reports_bp.route('/export/excel')
@login_required
def export_excel():
    report_type = request.args.get('type', 'place_wise')
    district = request.args.get('district', '')
    status = request.args.get('status', '')
    
    title, headers, rows, summary = get_report_dataset(report_type, district, status)
    excel_bytes = ExportService.generate_excel(title, headers, rows, summary)
    
    LoggerService.log_activity('Report Exported (Excel)', 'Reports', f"Exported Excel for '{title}'.")
    
    response = make_response(excel_bytes)
    response.headers['Content-Type'] = 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    response.headers['Content-Disposition'] = f'attachment; filename="covid19_{report_type}_report.xlsx"'
    return response

@reports_bp.route('/export/csv')
@login_required
def export_csv():
    report_type = request.args.get('type', 'place_wise')
    district = request.args.get('district', '')
    status = request.args.get('status', '')
    
    title, headers, rows, _ = get_report_dataset(report_type, district, status)
    csv_bytes = ExportService.generate_csv(headers, rows)
    
    LoggerService.log_activity('Report Exported (CSV)', 'Reports', f"Exported CSV for '{title}'.")
    
    response = Response(csv_bytes, mimetype='text/csv')
    response.headers['Content-Disposition'] = f'attachment; filename="covid19_{report_type}_report.csv"'
    return response

@reports_bp.route('/print')
@login_required
def print_view():
    report_type = request.args.get('type', 'place_wise')
    district = request.args.get('district', '')
    status = request.args.get('status', '')
    
    title, headers, rows, summary = get_report_dataset(report_type, district, status)
    return render_template(
        'reports/print.html',
        title=title,
        headers=headers,
        rows=rows,
        summary=summary,
        report_type=report_type,
        generated_at=datetime.utcnow().strftime('%B %d, %Y at %H:%M:%S UTC')
    )
