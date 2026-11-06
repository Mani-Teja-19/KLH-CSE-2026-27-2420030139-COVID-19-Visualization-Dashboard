import os
import openpyxl
from io import BytesIO
from datetime import datetime
from sqlalchemy import func
from models import db, StateCovidData

class StateDataService:
    EXCEL_FILENAME = 'Covid Dashboard.xlsx'

    @classmethod
    def get_excel_path(cls):
        """Locates the Covid Dashboard.xlsx file in workspace or common directories."""
        base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
        possible_paths = [
            os.path.join(base_dir, cls.EXCEL_FILENAME),
            os.path.join(base_dir, 'database', cls.EXCEL_FILENAME),
            os.path.join(base_dir, 'static', 'uploads', cls.EXCEL_FILENAME),
            os.path.join(os.path.expanduser('~'), 'Downloads', cls.EXCEL_FILENAME),
            os.path.join(os.path.expanduser('~'), 'Desktop', cls.EXCEL_FILENAME),
        ]
        for path in possible_paths:
            if os.path.exists(path):
                return path
        return None

    @classmethod
    def import_excel_dataset(cls, file_path=None):
        """
        Imports and parses the Covid Dashboard.xlsx dataset.
        Handles missing values, duplicate state records (upsert), and ensures
        no fake/random vaccination data is generated.
        """
        if not file_path:
            file_path = cls.get_excel_path()

        if not file_path or not os.path.exists(file_path):
            return {
                'success': False,
                'error': f'Excel file "{cls.EXCEL_FILENAME}" not found on system.',
                'imported': 0,
                'updated': 0
            }

        try:
            wb = openpyxl.load_workbook(file_path, data_only=True)
            # Find the primary data sheet (prefer 'Data')
            sheet_name = 'Data' if 'Data' in wb.sheetnames else wb.sheetnames[0]
            sheet = wb[sheet_name]

            # Read headers from Row 1
            headers = [str(sheet.cell(1, c).value or '').strip() for c in range(1, sheet.max_column + 1)]
            
            # Map column indices (case-insensitive substring matching)
            col_map = {}
            for idx, h in enumerate(headers, start=1):
                h_lower = h.lower()
                if 'state' in h_lower or 'ut' in h_lower:
                    col_map['state'] = idx
                elif 'zone' in h_lower:
                    col_map['zone'] = idx
                elif 'total case' in h_lower or 'cases' in h_lower:
                    col_map['total_cases'] = idx
                elif 'active ratio' in h_lower:
                    col_map['active_ratio'] = idx
                elif 'active' in h_lower:
                    col_map['active'] = idx
                elif 'discharge ratio' in h_lower:
                    col_map['discharge_ratio'] = idx
                elif 'discharge avg' in h_lower:
                    col_map['discharge_avg'] = idx
                elif 'discharge' in h_lower or 'recovered' in h_lower:
                    col_map['discharged'] = idx
                elif 'death ratio' in h_lower:
                    col_map['death_ratio'] = idx
                elif 'death avg' in h_lower:
                    col_map['death_avg'] = idx
                elif 'death' in h_lower:
                    col_map['deaths'] = idx
                elif 'population' in h_lower:
                    col_map['population'] = idx
                elif 'vaccin' in h_lower:
                    col_map['vaccinated'] = idx

            # Fallback to standard 1-based columns from sheet 'Data' if header names vary
            if 'state' not in col_map: col_map['state'] = 1
            if 'zone' not in col_map: col_map['zone'] = 2
            if 'total_cases' not in col_map: col_map['total_cases'] = 3
            if 'active' not in col_map: col_map['active'] = 4
            if 'discharged' not in col_map: col_map['discharged'] = 5
            if 'deaths' not in col_map: col_map['deaths'] = 6
            if 'active_ratio' not in col_map: col_map['active_ratio'] = 7
            if 'discharge_ratio' not in col_map: col_map['discharge_ratio'] = 8
            if 'discharge_avg' not in col_map: col_map['discharge_avg'] = 9
            if 'death_ratio' not in col_map: col_map['death_ratio'] = 10
            if 'death_avg' not in col_map: col_map['death_avg'] = 11
            if 'population' not in col_map: col_map['population'] = 12

            def safe_int(val):
                if val is None or val == '': return 0
                try:
                    return int(float(str(val).replace(',', '').strip()))
                except (ValueError, TypeError):
                    return 0

            def safe_float(val):
                if val is None or val == '': return 0.0
                try:
                    return float(str(val).replace(',', '').strip())
                except (ValueError, TypeError):
                    return 0.0

            def safe_str(val):
                if val is None: return ''
                return str(val).strip()

            imported_count = 0
            updated_count = 0
            processed_states = set()

            for r in range(2, sheet.max_row + 1):
                state_raw = sheet.cell(r, col_map['state']).value
                if not state_raw:
                    continue
                state_name = safe_str(state_raw)
                # Ignore summary or empty rows like 'Grand Total' or 'Total'
                if not state_name or state_name.lower() in ('total', 'grand total', 'all states'):
                    continue
                
                # Check for duplicate within the same Excel sheet
                if state_name.lower() in processed_states:
                    continue
                processed_states.add(state_name.lower())

                zone = safe_str(sheet.cell(r, col_map['zone']).value) if 'zone' in col_map else 'N/A'
                total_cases = safe_int(sheet.cell(r, col_map['total_cases']).value)
                active = safe_int(sheet.cell(r, col_map['active']).value)
                discharged = safe_int(sheet.cell(r, col_map['discharged']).value)
                deaths = safe_int(sheet.cell(r, col_map['deaths']).value)
                population = safe_int(sheet.cell(r, col_map['population']).value)
                active_ratio = safe_float(sheet.cell(r, col_map['active_ratio']).value) if 'active_ratio' in col_map else 0.0
                discharge_ratio = safe_float(sheet.cell(r, col_map['discharge_ratio']).value) if 'discharge_ratio' in col_map else 0.0
                discharge_avg = safe_str(sheet.cell(r, col_map['discharge_avg']).value) if 'discharge_avg' in col_map else 'N/A'
                death_ratio = safe_float(sheet.cell(r, col_map['death_ratio']).value) if 'death_ratio' in col_map else 0.0
                death_avg = safe_str(sheet.cell(r, col_map['death_avg']).value) if 'death_avg' in col_map else 'N/A'

                # Vaccination handling: genuine Excel data check only
                vax_val = None
                vax_available = False
                if 'vaccinated' in col_map:
                    raw_vax = sheet.cell(r, col_map['vaccinated']).value
                    if raw_vax is not None and str(raw_vax).strip() != '':
                        vax_val = safe_int(raw_vax)
                        vax_available = True

                # Upsert by state_name (case-insensitive check)
                existing = StateCovidData.query.filter(
                    func.lower(StateCovidData.state_name) == state_name.lower()
                ).first()

                if existing:
                    existing.state_name = state_name  # preserve canonical casing
                    existing.zone = zone
                    existing.population = population
                    existing.total_cases = total_cases
                    existing.active_cases = active
                    existing.discharged = discharged
                    existing.deaths = deaths
                    existing.active_ratio = active_ratio
                    existing.discharge_ratio = discharge_ratio
                    existing.discharge_avg = discharge_avg
                    existing.death_ratio = death_ratio
                    existing.death_avg = death_avg
                    if vax_available:
                        existing.vaccinated = vax_val
                        existing.non_vaccinated = max(0, population - vax_val)
                        existing.vaccination_data_available = True
                    else:
                        existing.vaccinated = None
                        existing.non_vaccinated = None
                        existing.vaccination_data_available = False
                    existing.source_file = os.path.basename(file_path)
                    existing.updated_at = datetime.utcnow()
                    updated_count += 1
                else:
                    new_state = StateCovidData(
                        state_name=state_name,
                        zone=zone,
                        population=population,
                        total_cases=total_cases,
                        active_cases=active,
                        discharged=discharged,
                        deaths=deaths,
                        active_ratio=active_ratio,
                        discharge_ratio=discharge_ratio,
                        discharge_avg=discharge_avg,
                        death_ratio=death_ratio,
                        death_avg=death_avg,
                        vaccinated=vax_val if vax_available else None,
                        non_vaccinated=max(0, population - vax_val) if vax_available else None,
                        vaccination_data_available=vax_available,
                        source_file=os.path.basename(file_path),
                        created_at=datetime.utcnow(),
                        updated_at=datetime.utcnow()
                    )
                    db.session.add(new_state)
                    imported_count += 1

            db.session.commit()
            return {
                'success': True,
                'imported': imported_count,
                'updated': updated_count,
                'total_states': len(processed_states),
                'source_file': os.path.basename(file_path)
            }
        except Exception as e:
            db.session.rollback()
            return {
                'success': False,
                'error': str(e),
                'imported': 0,
                'updated': 0
            }

    @classmethod
    def get_summary(cls, state_name=None):
        """
        Returns dynamic summary statistics for:
        - Total Population
        - Total Affected People (Total Cases)
        - Total Non-Affected People (Population - Total Cases)
        - Total Active Cases
        - Total Recovered Cases (Discharged)
        - Total Deaths
        - Total Vaccinated People (or unavailable indicator)
        - Total Non-Vaccinated People (or unavailable indicator)
        """
        # If database is empty, automatically attempt import
        if StateCovidData.query.count() == 0:
            cls.import_excel_dataset()

        is_all = not state_name or state_name.strip().lower() in ('all', 'all states', '')

        if not is_all:
            state = StateCovidData.query.filter(
                func.lower(StateCovidData.state_name) == state_name.strip().lower()
            ).first()
            if state:
                d = state.to_dict()
                return {
                    'scope': state.state_name,
                    'is_all_states': False,
                    'state_name': state.state_name,
                    'zone': state.zone,
                    'total_population': d['population'],
                    'affected': d['affected'],
                    'non_affected': d['non_affected'],
                    'active': d['active'],
                    'recovered': d['recovered'],
                    'deaths': d['deaths'],
                    'vaccinated': d['vaccinated'],
                    'non_vaccinated': d['non_vaccinated'],
                    'vaccination_data_available': d['vaccination_data_available'],
                    'vaccination_status_text': d['vaccination_status_text'],
                    'recovery_rate': round((d['recovered'] / d['affected'] * 100), 2) if d['affected'] > 0 else 0.0,
                    'death_rate': round((d['deaths'] / d['affected'] * 100), 2) if d['affected'] > 0 else 0.0,
                    'active_rate': round((d['active'] / d['affected'] * 100), 2) if d['affected'] > 0 else 0.0,
                    'attack_rate': round((d['affected'] / d['population'] * 100), 2) if d['population'] > 0 else 0.0
                }

        # Overall aggregate across all states
        states = StateCovidData.query.all()
        total_pop = sum(s.population or 0 for s in states)
        total_affected = sum(s.total_cases or 0 for s in states)
        total_non_affected = sum(max(0, (s.population or 0) - (s.total_cases or 0)) for s in states)
        total_active = sum(s.active_cases or 0 for s in states)
        total_recovered = sum(s.discharged or 0 for s in states)
        total_deaths = sum(s.deaths or 0 for s in states)

        # Check if genuine vaccination data is present
        has_vax = any(s.vaccination_data_available and s.vaccinated is not None for s in states)
        total_vax = sum(s.vaccinated or 0 for s in states) if has_vax else None
        total_non_vax = max(0, total_pop - total_vax) if has_vax and total_vax is not None else None

        recovery_rate = round((total_recovered / total_affected * 100), 2) if total_affected > 0 else 0.0
        death_rate = round((total_deaths / total_affected * 100), 2) if total_affected > 0 else 0.0
        active_rate = round((total_active / total_affected * 100), 2) if total_affected > 0 else 0.0
        attack_rate = round((total_affected / total_pop * 100), 2) if total_pop > 0 else 0.0

        return {
            'scope': 'All States & Union Territories',
            'is_all_states': True,
            'state_name': 'All States',
            'zone': 'National',
            'total_population': total_pop,
            'affected': total_affected,
            'non_affected': total_non_affected,
            'active': total_active,
            'recovered': total_recovered,
            'deaths': total_deaths,
            'vaccinated': total_vax,
            'non_vaccinated': total_non_vax,
            'vaccination_data_available': has_vax,
            'vaccination_status_text': 'Vaccination data not available' if not has_vax else f"{total_vax:,}",
            'recovery_rate': recovery_rate,
            'death_rate': death_rate,
            'active_rate': active_rate,
            'attack_rate': attack_rate,
            'states_count': len(states)
        }

    @classmethod
    def get_charts_data(cls, state_name=None, sort_deaths='default'):
        """
        Generates structured data payloads for the 4 interactive Chart.js charts:
        - Chart 1: State-wise Affected vs Non-Affected (Bar Chart)
        - Chart 2: State-wise Deaths (Bar Chart, sortable)
        - Chart 3: State-wise Active vs Recovered (Grouped Bar Chart)
        - Chart 4: Vaccinated vs Non-Vaccinated (Doughnut Chart / Clear unavailable message)
        """
        if StateCovidData.query.count() == 0:
            cls.import_excel_dataset()

        is_all = not state_name or state_name.strip().lower() in ('all', 'all states', '')

        if not is_all:
            query_state = StateCovidData.query.filter(
                func.lower(StateCovidData.state_name) == state_name.strip().lower()
            ).first()
            states = [query_state] if query_state else []
        else:
            states = StateCovidData.query.order_by(StateCovidData.state_name.asc()).all()

        state_labels = [s.state_name for s in states]
        affected_list = [s.affected for s in states]
        non_affected_list = [s.non_affected for s in states]
        active_list = [s.active_cases for s in states]
        recovered_list = [s.recovered for s in states]
        deaths_list = [s.deaths for s in states]

        # Chart 1: Affected vs Non-Affected (Bar Chart)
        chart1_affected_vs_non_affected = {
            'labels': state_labels,
            'datasets': [
                {
                    'label': 'Affected People (Total Cases)',
                    'data': affected_list,
                    'backgroundColor': 'rgba(239, 68, 68, 0.85)',   # Red
                    'borderColor': '#ef4444',
                    'borderWidth': 1.5,
                    'borderRadius': 4
                },
                {
                    'label': 'Non-Affected People (Population - Cases)',
                    'data': non_affected_list,
                    'backgroundColor': 'rgba(14, 165, 233, 0.85)',  # Sky Blue
                    'borderColor': '#0ea5e9',
                    'borderWidth': 1.5,
                    'borderRadius': 4
                }
            ]
        }

        # Chart 2: Deaths Bar Chart with Sorting capability
        death_pairs = list(zip(state_labels, deaths_list))
        if sort_deaths == 'highest':
            death_pairs.sort(key=lambda x: x[1], reverse=True)
        elif sort_deaths == 'lowest':
            death_pairs.sort(key=lambda x: x[1], reverse=False)

        chart2_deaths = {
            'labels': [p[0] for p in death_pairs],
            'datasets': [
                {
                    'label': 'Total Fatalities / Deaths',
                    'data': [p[1] for p in death_pairs],
                    'backgroundColor': 'rgba(220, 38, 38, 0.85)',   # Crimson Red
                    'borderColor': '#b91c1c',
                    'borderWidth': 1.5,
                    'borderRadius': 4
                }
            ],
            'current_sort': sort_deaths
        }

        # Chart 3: Active vs Recovered (Grouped Bar Chart)
        chart3_active_vs_recovered = {
            'labels': state_labels,
            'datasets': [
                {
                    'label': 'Active Cases',
                    'data': active_list,
                    'backgroundColor': 'rgba(245, 158, 11, 0.85)',  # Amber
                    'borderColor': '#f59e0b',
                    'borderWidth': 1.5,
                    'borderRadius': 4
                },
                {
                    'label': 'Recovered / Discharged',
                    'data': recovered_list,
                    'backgroundColor': 'rgba(16, 185, 129, 0.85)',  # Emerald Green
                    'borderColor': '#10b981',
                    'borderWidth': 1.5,
                    'borderRadius': 4
                }
            ]
        }

        # Chart 4: Vaccinated vs Non-Vaccinated (Doughnut Chart)
        # Requirement: The current Excel dataset does not contain vaccinated or non-vaccinated counts.
        # Do not assume or generate these values. Display only when genuine vaccination data is available.
        has_vax = any(s.vaccination_data_available and s.vaccinated is not None for s in states)
        if has_vax:
            total_vax = sum(s.vaccinated or 0 for s in states)
            total_non_vax = sum(s.non_vaccinated or 0 for s in states)
            chart4_vaccination = {
                'available': True,
                'labels': ['Vaccinated Population', 'Non-Vaccinated Population'],
                'datasets': [{
                    'data': [total_vax, total_non_vax],
                    'backgroundColor': ['#10b981', '#f59e0b'],
                    'borderColor': ['#059669', '#d97706'],
                    'borderWidth': 2
                }],
                'message': None
            }
        else:
            chart4_vaccination = {
                'available': False,
                'labels': [],
                'datasets': [],
                'message': 'Vaccination data not available in the uploaded Excel dataset. Genuine records have not been supplied, and synthetic figures are strictly disallowed.'
            }

        return {
            'chart1_affected_vs_non_affected': chart1_affected_vs_non_affected,
            'chart2_deaths': chart2_deaths,
            'chart3_active_vs_recovered': chart3_active_vs_recovered,
            'chart4_vaccination': chart4_vaccination,
            'selected_state': state_name or 'All'
        }

    @classmethod
    def get_table_data(cls, state_name=None, search=None, sort_by='state_name', sort_order='asc'):
        """
        Returns complete state data formatted for the responsive data table,
        including searchable, sortable list and grand totals row.
        """
        if StateCovidData.query.count() == 0:
            cls.import_excel_dataset()

        query = StateCovidData.query

        # Filter by state if specified
        if state_name and state_name.strip().lower() not in ('all', 'all states', ''):
            query = query.filter(func.lower(StateCovidData.state_name) == state_name.strip().lower())

        # Search filter
        if search and search.strip():
            s = f"%{search.strip().lower()}%"
            query = query.filter(func.lower(StateCovidData.state_name).like(s))

        records = query.all()
        state_dicts = [r.to_dict() for r in records]

        # In-memory sorting for computed columns
        reverse = (sort_order.lower() == 'desc')
        valid_keys = ['state_name', 'population', 'affected', 'non_affected', 'active', 'recovered', 'deaths', 'zone']
        if sort_by in valid_keys:
            if sort_by == 'state_name':
                state_dicts.sort(key=lambda x: str(x[sort_by]).lower(), reverse=reverse)
            else:
                state_dicts.sort(key=lambda x: (x[sort_by] is None, x[sort_by]), reverse=reverse)

        # Calculate totals for the footer
        total_pop = sum(d['population'] for d in state_dicts)
        total_affected = sum(d['affected'] for d in state_dicts)
        total_non_affected = sum(d['non_affected'] for d in state_dicts)
        total_active = sum(d['active'] for d in state_dicts)
        total_recovered = sum(d['recovered'] for d in state_dicts)
        total_deaths = sum(d['deaths'] for d in state_dicts)

        has_vax = any(d['vaccination_data_available'] and d['vaccinated'] is not None for d in state_dicts)
        total_vax = sum(d['vaccinated'] or 0 for d in state_dicts) if has_vax else 'Vaccination data not available'
        total_non_vax = sum(d['non_vaccinated'] or 0 for d in state_dicts) if has_vax else 'Vaccination data not available'

        totals_row = {
            'state_name': 'Total / National Summary' if len(state_dicts) > 1 else 'Total',
            'population': total_pop,
            'affected': total_affected,
            'non_affected': total_non_affected,
            'active': total_active,
            'recovered': total_recovered,
            'deaths': total_deaths,
            'vaccinated': total_vax,
            'non_vaccinated': total_non_vax,
            'vaccination_status_text': 'Vaccination data not available' if not has_vax else f"{total_vax:,}"
        }

        return {
            'rows': state_dicts,
            'total_count': len(state_dicts),
            'totals': totals_row
        }

    @classmethod
    def export_excel(cls, state_name=None):
        """Exports state-wise statistics to an Excel spreadsheet (.xlsx)."""
        table_info = cls.get_table_data(state_name=state_name, sort_by='state_name')
        rows = table_info['rows']
        totals = table_info['totals']

        wb = openpyxl.Workbook()
        ws = wb.active
        ws.title = "State-wise COVID Statistics"

        from openpyxl.styles import Font, PatternFill, Alignment, Border, Side

        # Colors & Styles
        header_fill = PatternFill(start_color="1E293B", end_color="1E293B", fill_type="solid")
        header_font = Font(name="Segoe UI", size=11, bold=True, color="FFFFFF")
        totals_fill = PatternFill(start_color="F1F5F9", end_color="F1F5F9", fill_type="solid")
        totals_font = Font(name="Segoe UI", size=11, bold=True, color="0F172A")
        body_font = Font(name="Segoe UI", size=10, color="334155")
        thin_border = Border(
            left=Side(style='thin', color='CBD5E1'),
            right=Side(style='thin', color='CBD5E1'),
            top=Side(style='thin', color='CBD5E1'),
            bottom=Side(style='thin', color='CBD5E1')
        )

        # Title Row
        ws.merge_cells('A1:I1')
        title_cell = ws.cell(row=1, column=1, value="COVID-19 Health & Visualization Dashboard - State-wise Surveillance")
        title_cell.font = Font(name="Segoe UI", size=14, bold=True, color="1E3A8A")
        title_cell.alignment = Alignment(horizontal="center", vertical="center")
        ws.row_dimensions[1].height = 30

        # Subtitle
        ws.merge_cells('A2:I2')
        sub_cell = ws.cell(row=2, column=1, value=f"Exported on {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S UTC')} | Source: Official COVID Surveillance Dataset")
        sub_cell.font = Font(name="Segoe UI", size=9, italic=True, color="64748B")
        sub_cell.alignment = Alignment(horizontal="center", vertical="center")
        ws.row_dimensions[2].height = 18

        headers = [
            "State / UT",
            "Population",
            "Affected (Total Cases)",
            "Non-Affected",
            "Active Cases",
            "Recovered (Discharged)",
            "Total Deaths",
            "Vaccinated",
            "Non-Vaccinated"
        ]

        # Write Headers on Row 4
        ws.row_dimensions[4].height = 24
        for col_idx, h in enumerate(headers, start=1):
            cell = ws.cell(row=4, column=col_idx, value=h)
            cell.font = header_font
            cell.fill = header_fill
            cell.alignment = Alignment(horizontal="center", vertical="center", wrap_text=True)
            cell.border = thin_border

        # Write Data Rows
        current_row = 5
        for r in rows:
            ws.row_dimensions[current_row].height = 20
            vals = [
                r['state_name'],
                r['population'],
                r['affected'],
                r['non_affected'],
                r['active'],
                r['recovered'],
                r['deaths'],
                r['vaccinated'] if r['vaccinated'] is not None else "Vaccination data not available",
                r['non_vaccinated'] if r['non_vaccinated'] is not None else "Vaccination data not available"
            ]
            for col_idx, val in enumerate(vals, start=1):
                cell = ws.cell(row=current_row, column=col_idx, value=val)
                cell.font = body_font
                cell.border = thin_border
                if col_idx == 1:
                    cell.alignment = Alignment(horizontal="left", vertical="center")
                elif isinstance(val, (int, float)):
                    cell.alignment = Alignment(horizontal="right", vertical="center")
                    cell.number_format = '#,##0'
                else:
                    cell.alignment = Alignment(horizontal="center", vertical="center")
            current_row += 1

        # Totals Row
        ws.row_dimensions[current_row].height = 24
        t_vals = [
            totals['state_name'],
            totals['population'],
            totals['affected'],
            totals['non_affected'],
            totals['active'],
            totals['recovered'],
            totals['deaths'],
            totals['vaccinated'] if isinstance(totals['vaccinated'], (int, float)) else "Vaccination data not available",
            totals['non_vaccinated'] if isinstance(totals['non_vaccinated'], (int, float)) else "Vaccination data not available"
        ]
        for col_idx, val in enumerate(t_vals, start=1):
            cell = ws.cell(row=current_row, column=col_idx, value=val)
            cell.font = totals_font
            cell.fill = totals_fill
            cell.border = thin_border
            if col_idx == 1:
                cell.alignment = Alignment(horizontal="left", vertical="center")
            elif isinstance(val, (int, float)):
                cell.alignment = Alignment(horizontal="right", vertical="center")
                cell.number_format = '#,##0'
            else:
                cell.alignment = Alignment(horizontal="center", vertical="center")

        # Auto-fit Column Widths
        for col in ws.columns:
            max_len = 0
            col_letter = openpyxl.utils.get_column_letter(col[0].column)
            for cell in col:
                val_str = str(cell.value or '')
                if cell.row not in (1, 2):  # skip merged header
                    max_len = max(max_len, len(val_str))
            ws.column_dimensions[col_letter].width = max(max_len + 4, 14)

        buf = BytesIO()
        wb.save(buf)
        buf.seek(0)
        return buf

    @classmethod
    def export_csv(cls, state_name=None):
        """Exports state-wise statistics to CSV format."""
        import csv
        from io import StringIO
        table_info = cls.get_table_data(state_name=state_name, sort_by='state_name')
        rows = table_info['rows']
        totals = table_info['totals']

        output = StringIO()
        writer = csv.writer(output)
        
        headers = [
            "State / UT",
            "Population",
            "Affected (Total Cases)",
            "Non-Affected",
            "Active Cases",
            "Recovered (Discharged)",
            "Total Deaths",
            "Vaccinated",
            "Non-Vaccinated"
        ]
        writer.writerow(headers)

        for r in rows:
            writer.writerow([
                r['state_name'],
                r['population'],
                r['affected'],
                r['non_affected'],
                r['active'],
                r['recovered'],
                r['deaths'],
                r['vaccinated'] if r['vaccinated'] is not None else "Vaccination data not available",
                r['non_vaccinated'] if r['non_vaccinated'] is not None else "Vaccination data not available"
            ])

        writer.writerow([
            totals['state_name'],
            totals['population'],
            totals['affected'],
            totals['non_affected'],
            totals['active'],
            totals['recovered'],
            totals['deaths'],
            totals['vaccinated'] if isinstance(totals['vaccinated'], (int, float)) else "Vaccination data not available",
            totals['non_vaccinated'] if isinstance(totals['non_vaccinated'], (int, float)) else "Vaccination data not available"
        ])

        output.seek(0)
        return output

