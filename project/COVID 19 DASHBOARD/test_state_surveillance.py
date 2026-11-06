import unittest
import json
from app import create_app
from models import db, StateCovidData
from services.state_data_service import StateDataService

class StateSurveillanceTestCase(unittest.TestCase):
    def setUp(self):
        self.app = create_app()
        self.app.config['TESTING'] = True
        self.client = self.app.test_client()
        self.ctx = self.app.app_context()
        self.ctx.push()
        
        # Ensure database and state data are initialized
        db.create_all()
        StateDataService.import_excel_dataset()

    def tearDown(self):
        self.ctx.pop()

    def login(self, username='admin', password='admin123'):
        return self.client.post('/login', data={
            'username': username,
            'password': password
        }, follow_redirects=True)

    def test_01_excel_dataset_integration_and_counts(self):
        print("\n[STATE TEST 1] Verifying Excel dataset integration and state counts...")
        states = StateCovidData.query.all()
        self.assertEqual(len(states), 36, f"Expected 36 states/UTs, found {len(states)}")
        
        # Verify deduplication on re-import
        reimport_res = StateDataService.import_excel_dataset()
        self.assertTrue(reimport_res['success'])
        self.assertEqual(reimport_res['imported'], 0)
        self.assertEqual(reimport_res['updated'], 36)
        self.assertEqual(StateCovidData.query.count(), 36)
        print(" -> Exactly 36 unique States/UTs imported with duplicate protection: OK")

    def test_02_national_summary_calculations(self):
        print("\n[STATE TEST 2] Verifying exact mathematical formulas and overall totals...")
        summary = StateDataService.get_summary('All')
        
        # Expected totals from Excel dataset
        self.assertEqual(summary['total_population'], 1429869880)
        self.assertEqual(summary['affected'], 34437307)
        self.assertEqual(summary['non_affected'], 1395432573)
        self.assertEqual(summary['active'], 135918)
        self.assertEqual(summary['recovered'], 33837859)
        self.assertEqual(summary['deaths'], 463530)
        
        # Exact formula verifications
        self.assertEqual(summary['non_affected'], summary['total_population'] - summary['affected'])
        self.assertEqual(summary['active'] + summary['recovered'] + summary['deaths'], summary['affected'])
        print(f" -> National Totals Verified: Pop={summary['total_population']:,}, Affected={summary['affected']:,}, Deaths={summary['deaths']:,}: OK")

    def test_03_vaccination_data_integrity(self):
        print("\n[STATE TEST 3] Verifying strict vaccination data integrity (no fabricated data)...")
        summary = StateDataService.get_summary('All')
        self.assertFalse(summary['vaccination_data_available'])
        self.assertIsNone(summary['vaccinated'])
        self.assertIsNone(summary['non_vaccinated'])
        self.assertEqual(summary['vaccination_status_text'], 'Vaccination data not available')

        # Check charts payload for unavailable notice
        charts = StateDataService.get_charts_data('All')
        vax_chart = charts['chart4_vaccination']
        self.assertFalse(vax_chart['available'])
        self.assertIn('Vaccination data not available', vax_chart['message'])
        print(" -> Vaccination data unavailability properly handled without fake figures: OK")

    def test_04_individual_state_filtering(self):
        print("\n[STATE TEST 4] Verifying individual state filtering (Maharashtra & Kerala)...")
        mh = StateDataService.get_summary('Maharashtra')
        self.assertEqual(mh['state_name'], 'Maharashtra')
        self.assertEqual(mh['total_population'], 124904071)
        self.assertEqual(mh['affected'], 6623344)
        self.assertEqual(mh['non_affected'], 124904071 - 6623344)
        self.assertEqual(mh['active'], 15866)
        self.assertEqual(mh['recovered'], 6466913)
        self.assertEqual(mh['deaths'], 140565)
        self.assertEqual(mh['active'] + mh['recovered'] + mh['deaths'], mh['affected'])

        kl = StateDataService.get_summary('Kerala')
        self.assertEqual(kl['state_name'], 'Kerala')
        self.assertEqual(kl['affected'], 5055224)
        self.assertEqual(kl['active'], 69258)
        self.assertEqual(kl['recovered'], 4950281)
        self.assertEqual(kl['deaths'], 35685)
        self.assertEqual(kl['active'] + kl['recovered'] + kl['deaths'], kl['affected'])
        print(" -> Maharashtra & Kerala precise state-level metrics: OK")

    def test_05_death_sorting_functionality(self):
        print("\n[STATE TEST 5] Verifying Chart 2 death sorting (highest to lowest)...")
        sorted_charts = StateDataService.get_charts_data('All', sort_deaths='highest')
        labels = sorted_charts['chart2_deaths']['labels']
        deaths = sorted_charts['chart2_deaths']['datasets'][0]['data']

        # Verify sorted descending
        for i in range(len(deaths) - 1):
            self.assertGreaterEqual(deaths[i], deaths[i + 1])

        self.assertEqual(labels[0], 'Maharashtra')
        self.assertEqual(deaths[0], 140565)
        self.assertEqual(labels[1], 'Karnataka')
        self.assertEqual(deaths[1], 38143)
        self.assertEqual(labels[2], 'Tamil Nadu')
        self.assertEqual(deaths[2], 36273)
        print(" -> Death sorting: Top 3 (MH=140k, KA=38k, TN=36k) descending order: OK")

    def test_06_api_endpoints_and_exports(self):
        print("\n[STATE TEST 6] Verifying REST API endpoints and Excel/CSV exporters...")
        self.login('admin', 'admin123')

        # Unified data endpoint
        res = self.client.get('/api/states/data?state=All')
        self.assertEqual(res.status_code, 200)
        data = json.loads(res.data)
        self.assertIn('summary', data)
        self.assertIn('charts', data)
        self.assertIn('table', data)
        self.assertEqual(len(data['table']['rows']), 36)

        # Single state API
        res_mh = self.client.get('/api/states/data?state=Maharashtra')
        self.assertEqual(res_mh.status_code, 200)
        data_mh = json.loads(res_mh.data)
        self.assertEqual(data_mh['summary']['affected'], 6623344)

        # Excel export API
        res_excel = self.client.get('/api/states/export/excel?state=All')
        self.assertEqual(res_excel.status_code, 200)
        self.assertEqual(res_excel.mimetype, 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
        self.assertGreater(len(res_excel.data), 4000)

        # CSV export API
        res_csv = self.client.get('/api/states/export/csv?state=All')
        self.assertEqual(res_csv.status_code, 200)
        self.assertIn(b'Maharashtra', res_csv.data)
        self.assertIn(b'Total / National Summary', res_csv.data)
        print(" -> API endpoints and valid Excel & CSV exports: OK")

if __name__ == '__main__':
    unittest.main()

