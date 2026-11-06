from datetime import datetime, timedelta
from sqlalchemy import func
from models import Place, Member, CovidCase, Vaccination, Hospital, StateCovidData, db

class StatsCalculator:
    @staticmethod
    def get_dashboard_summary():
        """
        Calculates the 12 core statistic metrics and rates for the Admin Dashboard,
        and includes national state-wise surveillance statistics from the imported dataset.
        """
        from services.state_data_service import StateDataService
        state_summary = StateDataService.get_summary()

        # Places stats
        total_places = Place.query.count()
        affected_places = Place.query.filter(Place.affected_status == 'Affected').count()
        not_affected_places = total_places - affected_places
        
        # Population from places
        total_population = db.session.query(func.sum(Place.total_population)).scalar() or 0
        
        # Members stats
        total_members = Member.query.count()
        
        # COVID Status counts
        positive_members = Member.query.filter(Member.covid_status.in_(['Positive', 'Active', 'Recovered', 'Deceased'])).count()
        active_cases = Member.query.filter(Member.covid_status.in_(['Positive', 'Active'])).count()
        recovered_members = Member.query.filter(Member.covid_status == 'Recovered').count()
        death_cases = Member.query.filter(Member.covid_status == 'Deceased').count()
        
        # Vaccination Status counts
        fully_vaccinated = Member.query.filter(Member.vaccination_status == 'Fully Vaccinated').count()
        partially_vaccinated = Member.query.filter(Member.vaccination_status == 'Partially Vaccinated').count()
        not_vaccinated = Member.query.filter(Member.vaccination_status == 'Not Vaccinated').count()
        
        # Calculated rates (percentages)
        recovery_rate = round((recovered_members / positive_members * 100), 1) if positive_members > 0 else 0.0
        death_rate = round((death_cases / positive_members * 100), 1) if positive_members > 0 else 0.0
        positivity_rate = round((positive_members / total_members * 100), 1) if total_members > 0 else 0.0
        vaccination_percentage = round((fully_vaccinated / total_members * 100), 1) if total_members > 0 else 0.0
        active_case_percentage = round((active_cases / positive_members * 100), 1) if positive_members > 0 else 0.0
        
        # Hospital capacity metrics
        hospitals = Hospital.query.all()
        total_beds = sum(h.total_beds for h in hospitals)
        occupied_beds = sum(h.occupied_beds for h in hospitals)
        total_icu = sum(h.icu_beds for h in hospitals)
        occupied_icu = sum(h.occupied_icu for h in hospitals)
        total_oxygen = sum(h.oxygen_cylinders for h in hospitals)
        bed_occupancy_rate = round((occupied_beds / total_beds * 100), 1) if total_beds > 0 else 0.0
        icu_occupancy_rate = round((occupied_icu / total_icu * 100), 1) if total_icu > 0 else 0.0

        return {
            # 12 Core Animated Cards
            'total_places': total_places,
            'affected_places': affected_places,
            'not_affected_places': not_affected_places,
            'total_population': total_population,
            'total_members': total_members,
            'positive_members': positive_members,
            'active_cases': active_cases,
            'recovered_members': recovered_members,
            'death_cases': death_cases,
            'fully_vaccinated': fully_vaccinated,
            'partially_vaccinated': partially_vaccinated,
            'not_vaccinated': not_vaccinated,
            
            # Key KPI Rates
            'recovery_rate': recovery_rate,
            'death_rate': death_rate,
            'positivity_rate': positivity_rate,
            'vaccination_percentage': vaccination_percentage,
            'active_case_percentage': active_case_percentage,
            
            # Hospital Infrastructure
            'total_beds': total_beds,
            'occupied_beds': occupied_beds,
            'bed_occupancy_rate': bed_occupancy_rate,
            'total_icu': total_icu,
            'occupied_icu': occupied_icu,
            'icu_occupancy_rate': icu_occupancy_rate,
            'total_oxygen': total_oxygen,

            # State-wise Dataset Dynamic Totals (Excel Dataset)
            'state_stats': state_summary,
            'excel_population': state_summary['total_population'],
            'excel_affected': state_summary['affected'],
            'excel_non_affected': state_summary['non_affected'],
            'excel_active': state_summary['active'],
            'excel_recovered': state_summary['recovered'],
            'excel_deaths': state_summary['deaths'],
            'excel_vaccinated': state_summary['vaccinated'],
            'excel_non_vaccinated': state_summary['non_vaccinated'],
            'excel_vax_available': state_summary['vaccination_data_available'],
            'excel_vax_text': state_summary['vaccination_status_text']
        }

    @staticmethod
    def get_district_statistics():
        """Returns district-wise aggregation of cases, places, and population."""
        districts = db.session.query(
            Place.district,
            func.count(Place.id).label('place_count'),
            func.sum(Place.total_population).label('population'),
            func.sum(Place.positive_cases).label('positive'),
            func.sum(Place.active_cases).label('active'),
            func.sum(Place.recovered_cases).label('recovered'),
            func.sum(Place.death_cases).label('deaths'),
            func.sum(Place.vaccinated_count).label('vaccinated')
        ).group_by(Place.district).all()

        results = []
        for d in districts:
            results.append({
                'district': d.district,
                'place_count': d.place_count,
                'population': d.population or 0,
                'positive': d.positive or 0,
                'active': d.active or 0,
                'recovered': d.recovered or 0,
                'deaths': d.deaths or 0,
                'vaccinated': d.vaccinated or 0
            })
        return sorted(results, key=lambda x: x['positive'], reverse=True)

    @staticmethod
    def get_analytics_charts_data():
        """Generates datasets formatted for Chart.js."""
        # 1. Affected vs Not Affected Places (Pie Chart)
        total_places = Place.query.count()
        affected_places = Place.query.filter(Place.affected_status == 'Affected').count()
        not_affected_places = max(0, total_places - affected_places)
        
        places_pie = {
            'labels': ['Affected Places', 'Not Affected Places'],
            'data': [affected_places, not_affected_places],
            'colors': ['#ef4444', '#10b981']
        }

        # 2. Vaccination Breakdown (Doughnut Chart)
        fully_vax = Member.query.filter(Member.vaccination_status == 'Fully Vaccinated').count()
        part_vax = Member.query.filter(Member.vaccination_status == 'Partially Vaccinated').count()
        not_vax = Member.query.filter(Member.vaccination_status == 'Not Vaccinated').count()
        
        vaccination_doughnut = {
            'labels': ['Fully Vaccinated', 'Partially Vaccinated', 'Not Vaccinated'],
            'data': [fully_vax, part_vax, not_vax],
            'colors': ['#10b981', '#0ea5e9', '#f59e0b']
        }

        # 3. District-wise Cases (Bar Chart)
        dist_stats = StatsCalculator.get_district_statistics()
        dist_labels = [d['district'] for d in dist_stats]
        dist_positive = [d['positive'] for d in dist_stats]
        dist_active = [d['active'] for d in dist_stats]
        dist_recovered = [d['recovered'] for d in dist_stats]
        dist_deaths = [d['deaths'] for d in dist_stats]

        district_bar = {
            'labels': dist_labels,
            'datasets': [
                {'label': 'Positive Cases', 'data': dist_positive, 'backgroundColor': '#6366f1'},
                {'label': 'Active Cases', 'data': dist_active, 'backgroundColor': '#f59e0b'},
                {'label': 'Recovered', 'data': dist_recovered, 'backgroundColor': '#10b981'},
                {'label': 'Deceased', 'data': dist_deaths, 'backgroundColor': '#ef4444'}
            ]
        }

        # 4. Top Hotspots (Horizontal Bar)
        top_hotspots = dist_stats[:7] if dist_stats else []
        hotspots_bar = {
            'labels': [d['district'] for d in top_hotspots],
            'data': [d['positive'] for d in top_hotspots],
            'colors': ['#ef4444', '#f97316', '#f59e0b', '#eab308', '#84cc16', '#10b981', '#06b6d4']
        }

        # 5. Daily & Weekly Timeline Trends (Line Chart)
        # Generate 14-day chronological trend based on admissions/infections
        now = datetime.utcnow().date()
        date_labels = [(now - timedelta(days=i)).strftime('%b %d') for i in reversed(range(14))]
        
        daily_new_cases = []
        daily_recoveries = []
        for i in reversed(range(14)):
            target_date = now - timedelta(days=i)
            # Count members infected / recovered on this date
            c_count = Member.query.filter(Member.infection_date == target_date).count()
            r_count = Member.query.filter(Member.recovery_date == target_date).count()
            # If dataset is small/sparse, add proportional baseline so chart looks realistic and beautiful
            daily_new_cases.append(c_count)
            daily_recoveries.append(r_count)

        trend_line = {
            'labels': date_labels,
            'cases': daily_new_cases,
            'recoveries': daily_recoveries
        }

        # 6. Age Demographics
        age_brackets = ['0-17', '18-35', '36-50', '51-65', '65+']
        males_by_age = [0, 0, 0, 0, 0]
        females_by_age = [0, 0, 0, 0, 0]
        
        members = Member.query.all()
        for m in members:
            idx = 0
            if m.age <= 17: idx = 0
            elif m.age <= 35: idx = 1
            elif m.age <= 50: idx = 2
            elif m.age <= 65: idx = 3
            else: idx = 4
            
            if m.gender == 'Male':
                males_by_age[idx] += 1
            elif m.gender == 'Female':
                females_by_age[idx] += 1

        demographics = {
            'labels': age_brackets,
            'male': males_by_age,
            'female': females_by_age
        }

        # 7. Vaccine Brands Distribution
        vaccines = db.session.query(
            Member.vaccine_name,
            func.count(Member.id)
        ).filter(Member.vaccine_name.isnot(None)).group_by(Member.vaccine_name).all()

        vax_brands = {
            'labels': [v[0] for v in vaccines if v[0]],
            'data': [v[1] for v in vaccines if v[0]],
            'colors': ['#3b82f6', '#10b981', '#8b5cf6', '#f59e0b', '#ec4899']
        }

        return {
            'places_pie': places_pie,
            'vaccination_doughnut': vaccination_doughnut,
            'district_bar': district_bar,
            'hotspots_bar': hotspots_bar,
            'trend_line': trend_line,
            'demographics': demographics,
            'vax_brands': vax_brands
        }
