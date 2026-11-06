import unittest
import json
from app import create_app
from models import db, User, Place, Member, CovidCase, Vaccination, Notification

class CovidDashboardTestCase(unittest.TestCase):
    def setUp(self):
        self.app = create_app()
        self.app.config['TESTING'] = True
        self.client = self.app.test_client()
        self.ctx = self.app.app_context()
        self.ctx.push()

    def tearDown(self):
        self.ctx.pop()

    def login(self, username, password):
        return self.client.post('/login', data={
            'username': username,
            'password': password,
            'remember': 'on'
        }, follow_redirects=True)

    def test_01_login_flow(self):
        print("\n[TEST 1] Testing Authentication...")
        # Bad login
        res = self.login('admin', 'wrong_pass')
        self.assertIn(b'Invalid username/email or password', res.data)
        
        # Valid login
        res = self.login('admin', 'admin123')
        self.assertEqual(res.status_code, 200)
        self.assertIn(b'Epidemiological Dashboard', res.data)
        print(" -> Admin Login Success: OK")

    def test_02_dashboard_and_api(self):
        print("\n[TEST 2] Testing Dashboard & JSON API Endpoints...")
        self.login('admin', 'admin123')
        
        # Stats summary API
        res = self.client.get('/api/stats/summary')
        self.assertEqual(res.status_code, 200)
        data = json.loads(res.data)
        self.assertIn('total_places', data)
        self.assertIn('recovery_rate', data)
        self.assertIn('positive_members', data)
        print(f" -> Dashboard Metrics: Places={data['total_places']}, Members={data['total_members']}, Recovery Rate={data['recovery_rate']}%: OK")
        
        # Charts data API
        res = self.client.get('/api/charts/data')
        self.assertEqual(res.status_code, 200)
        cdata = json.loads(res.data)
        self.assertIn('places_pie', cdata)
        self.assertIn('trend_line', cdata)
        print(" -> Chart.js JSON Payloads: OK")

    def test_03_places_crud(self):
        print("\n[TEST 3] Testing Place Management CRUD...")
        self.login('admin', 'admin123')
        
        # 1. Create Place
        res = self.client.post('/places/create', data={
            'place_name': 'Test Cyber City',
            'village_city': 'Sector 88',
            'mandal_taluk': 'Central Taluk',
            'district': 'Central District',
            'state': 'Maharashtra',
            'pincode': '400099',
            'total_population': '45000',
            'total_families': '10500'
        }, follow_redirects=True)
        self.assertEqual(res.status_code, 200)
        self.assertIn(b'Test Cyber City', res.data)
        
        # 2. View Place
        p = Place.query.filter_by(place_name='Test Cyber City').first()
        self.assertIsNotNone(p)
        res = self.client.get(f'/places/{p.id}')
        self.assertEqual(res.status_code, 200)
        self.assertIn(b'Test Cyber City', res.data)

        # 3. Edit Place
        res = self.client.post(f'/places/{p.id}/edit', data={
            'place_name': 'Test Cyber City Updated',
            'village_city': 'Sector 88',
            'mandal_taluk': 'Central Taluk',
            'district': 'Central District',
            'state': 'Maharashtra',
            'pincode': '400099',
            'total_population': '50000',
            'total_families': '12000'
        }, follow_redirects=True)
        self.assertEqual(res.status_code, 200)
        self.assertIn(b'Test Cyber City Updated', res.data)

        # 4. Delete Place
        res = self.client.post(f'/places/{p.id}/delete', follow_redirects=True)
        self.assertEqual(res.status_code, 200)
        self.assertIsNone(Place.query.get(p.id))
        print(" -> Place CRUD: Create, View, Edit, Delete: OK")

    def test_04_member_management(self):
        print("\n[TEST 4] Testing Member Management & Health Passport...")
        self.login('admin', 'admin123')
        
        p = Place.query.first()
        res = self.client.post('/members/create', data={
            'full_name': 'Dr. Vikram Malhotra',
            'age': '42',
            'gender': 'Male',
            'dob': '1984-06-15',
            'mobile_number': '9899887766',
            'email': 'vikram.m@testhealth.gov',
            'aadhaar_number': '1234 5678 9012',
            'address': 'House 14, Main Road',
            'place_id': str(p.id) if p else '',
            'occupation': 'Surgeon',
            'covid_status': 'Negative',
            'vaccination_status': 'Fully Vaccinated',
            'vaccine_name': 'Covishield',
            'dose1_date': '2024-01-10',
            'dose2_date': '2024-04-12',
            'hospital_name': 'City Apex Covid Care Hospital',
            'doctor_name': 'Dr. Rajesh Kumar',
            'medical_remarks': 'Health worker booster priority.'
        }, follow_redirects=True)
        self.assertEqual(res.status_code, 200)
        
        m = Member.query.filter_by(full_name='Dr. Vikram Malhotra').first()
        self.assertIsNotNone(m)
        self.assertTrue(m.member_code.startswith('MEM-'))
        
        # View Health Card
        res = self.client.get(f'/members/{m.id}')
        self.assertEqual(res.status_code, 200)
        self.assertIn(b'Citizen Health Identity Card', res.data)
        self.assertIn(b'Dr. Vikram Malhotra', res.data)
        print(f" -> Member Created: {m.full_name} ({m.member_code}), Health Passport: OK")

    def test_05_cases_and_discharge(self):
        print("\n[TEST 5] Testing COVID Case Admission & Discharge Flow...")
        self.login('admin', 'admin123')
        
        m = Member.query.first()
        res = self.client.post('/cases/create', data={
            'member_id': str(m.id),
            'admission_date': '2026-09-01',
            'covid_variant': 'Omicron BA.5',
            'symptoms': 'Fever, Dry Cough, Sore Throat',
            'ct_score': '11/25',
            'severity': 'Moderate',
            'quarantine_status': 'Hospitalized',
            'ward_bed_no': 'Ward 2 - Bed 104',
            'assigned_doctor': 'Dr. Ananya Sen',
            'notes': 'Vitals stable. SpO2 96%.'
        }, follow_redirects=True)
        self.assertEqual(res.status_code, 200)
        
        case = CovidCase.query.filter_by(member_id=m.id).order_by(CovidCase.id.desc()).first()
        self.assertIsNotNone(case)
        self.assertEqual(case.quarantine_status, 'Hospitalized')
        
        # Discharge
        res = self.client.post(f'/cases/{case.id}/discharge', follow_redirects=True)
        self.assertEqual(res.status_code, 200)
        updated_case = CovidCase.query.get(case.id)
        self.assertEqual(updated_case.quarantine_status, 'Discharged')
        print(" -> Case Admission & Patient Discharge: OK")

    def test_06_vaccination_and_certificate(self):
        print("\n[TEST 6] Testing Vaccination Drive & Official Certificate...")
        self.login('admin', 'admin123')
        
        m = Member.query.first()
        res = self.client.post('/vaccinations/create', data={
            'member_id': str(m.id),
            'dose_number': '1',
            'vaccine_name': 'Covishield',
            'vaccination_date': '2026-09-05',
            'center_name': 'Sunrise Community Healthcare Center',
            'batch_number': 'VAC-B777X',
            'vaccinated_by': 'Nurse Roshni K.'
        }, follow_redirects=True)
        self.assertEqual(res.status_code, 200)
        
        vax = Vaccination.query.filter_by(member_id=m.id).order_by(Vaccination.id.desc()).first()
        self.assertIsNotNone(vax)
        self.assertTrue(vax.certificate_no.startswith('COV-VAX-'))
        
        # View Certificate
        res = self.client.get(f'/vaccinations/{vax.id}/certificate')
        self.assertEqual(res.status_code, 200)
        self.assertIn(b'Certificate of COVID-19 Vaccination', res.data)
        print(f" -> Vaccination Certificate: {vax.certificate_no}: OK")

    def test_07_reports_and_export_generation(self):
        print("\n[TEST 7] Testing Reports & Multi-Format Exporters (PDF, Excel, CSV, Print)...")
        self.login('admin', 'admin123')
        
        # 1. Reports Page View
        res = self.client.get('/reports/?type=district_wise')
        self.assertEqual(res.status_code, 200)
        self.assertIn(b'District-wise Epidemiological Matrix Report', res.data)
        
        # 2. PDF Export
        res = self.client.get('/reports/export/pdf?type=place_wise')
        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.content_type, 'application/pdf')
        self.assertTrue(res.data.startswith(b'%PDF-'))
        print(f" -> PDF Exporter: Valid Binary PDF ({len(res.data)} bytes): OK")

        # 3. Excel Export
        res = self.client.get('/reports/export/excel?type=place_wise')
        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.content_type, 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
        self.assertTrue(res.data.startswith(b'PK')) # Zip header of xlsx
        print(f" -> Excel Exporter: Valid .xlsx Spreadsheet ({len(res.data)} bytes): OK")

        # 4. CSV Export
        res = self.client.get('/reports/export/csv?type=place_wise')
        self.assertEqual(res.status_code, 200)
        self.assertIn(b'Place Name,Village/City,District', res.data)
        print(f" -> CSV Exporter: Valid CSV stream ({len(res.data)} bytes): OK")

        # 5. Print Layout
        res = self.client.get('/reports/print?type=place_wise')
        self.assertEqual(res.status_code, 200)
        self.assertIn(b'window.print()', res.data)
        print(" -> Print View Layout: OK")

    def test_08_notifications_and_broadcast(self):
        print("\n[TEST 8] Testing Notifications Center & Broadcast...")
        self.login('admin', 'admin123')
        
        # Broadcast
        res = self.client.post('/notifications/create', data={
            'title': 'Automated Test Warning',
            'message': 'Testing emergency alert delivery to dashboard.',
            'category': 'Emergency',
            'alert_level': 'High',
            'target_url': '/dashboard'
        }, follow_redirects=True)
        self.assertEqual(res.status_code, 200)
        
        notif = Notification.query.filter_by(title='Automated Test Warning').first()
        self.assertIsNotNone(notif)
        
        # Mark as read
        res = self.client.post(f'/notifications/{notif.id}/read')
        self.assertEqual(res.status_code, 200)
        updated_n = Notification.query.get(notif.id)
        self.assertTrue(updated_n.is_read)
        print(" -> Emergency Alert Broadcast & Read Status: OK")

    def test_09_settings_and_preferences(self):
        print("\n[TEST 9] Testing System Settings & Configuration...")
        self.login('admin', 'admin123')
        
        res = self.client.post('/settings/', data={
            'app_title': 'COVID-19 Health Intelligence Portal Pro',
            'containment_threshold_cases': '4',
            'auto_refresh_seconds': '30',
            'alert_email_notifications': 'on'
        }, follow_redirects=True)
        self.assertEqual(res.status_code, 200)
        self.assertIn(b'System configuration updated successfully', res.data)
        print(" -> Settings Update: OK")

    def test_10_state_surveillance(self):
        print("\n[TEST 10] Testing State-wise COVID Surveillance & Excel Integration...")
        from services.state_data_service import StateDataService
        from models import StateCovidData

        # 1. Verify 36 States Imported
        states_count = StateCovidData.query.count()
        self.assertEqual(states_count, 36)

        # 2. Verify National Sums
        summary = StateDataService.get_summary('All')
        self.assertEqual(summary['total_population'], 1429869880)
        self.assertEqual(summary['affected'], 34437307)
        self.assertEqual(summary['non_affected'], 1395432573)
        self.assertEqual(summary['active'], 135918)
        self.assertEqual(summary['recovered'], 33837859)
        self.assertEqual(summary['deaths'], 463530)
        self.assertFalse(summary['vaccination_data_available'])
        self.assertIsNone(summary['vaccinated'])

        # 3. Verify Specific State (Maharashtra)
        mh = StateDataService.get_summary('Maharashtra')
        self.assertEqual(mh['state_name'], 'Maharashtra')
        self.assertEqual(mh['total_population'], 124904071)
        self.assertEqual(mh['affected'], 6623344)
        self.assertEqual(mh['non_affected'], 124904071 - 6623344)
        self.assertEqual(mh['active'], 15866)
        self.assertEqual(mh['recovered'], 6466913)
        self.assertEqual(mh['deaths'], 140565)

        # 4. Verify API Endpoints & Exporters
        self.login('admin', 'admin123')
        res_api = self.client.get('/api/states/data?state=All')
        self.assertEqual(res_api.status_code, 200)
        api_data = json.loads(res_api.data)
        self.assertEqual(len(api_data['table']['rows']), 36)

        res_excel = self.client.get('/api/states/export/excel?state=All')
        self.assertEqual(res_excel.status_code, 200)
        self.assertGreater(len(res_excel.data), 4000)

        res_csv = self.client.get('/api/states/export/csv?state=All')
        self.assertEqual(res_csv.status_code, 200)
        self.assertIn(b'Maharashtra', res_csv.data)
        print(" -> State-wise Surveillance, Excel Integration & APIs: OK")

if __name__ == '__main__':
    unittest.main()
