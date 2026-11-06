import os
import random
from datetime import datetime, timedelta
from flask import Flask
from config import Config
from models import db, User, Place, Member, CovidCase, Vaccination, Hospital, Notification, ActivityLog, Setting

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    
    # Ensure database folder exists if using SQLite
    db_dir = os.path.join(os.path.abspath(os.path.dirname(__file__)), 'database')
    os.makedirs(db_dir, exist_ok=True)
    
    upload_dir = app.config['UPLOAD_FOLDER']
    os.makedirs(upload_dir, exist_ok=True)
    
    db.init_app(app)
    return app

def seed_database():
    app = create_app()
    with app.app_context():
        print("Dropping existing tables...")
        db.drop_all()
        print("Creating new database schema...")
        db.create_all()
        
        print("Seeding Users...")
        # 1. Seed Default Users
        admin_user = User(
            username='admin',
            email='admin@covid19dashboard.gov',
            full_name='Dr. Rajesh Kumar (Chief Health Officer)',
            role='Admin',
            phone='+91 9876543210',
            avatar='default-avatar.png',
            is_active=True,
            created_at=datetime.utcnow() - timedelta(days=60),
            last_login=datetime.utcnow()
        )
        admin_user.set_password('admin123')
        
        doctor_user = User(
            username='doctor',
            email='dr.ananya@apollohealth.org',
            full_name='Dr. Ananya Sen (Infectious Disease Specialist)',
            role='Doctor',
            phone='+91 9811223344',
            avatar='default-avatar.png',
            is_active=True,
            created_at=datetime.utcnow() - timedelta(days=45),
            last_login=datetime.utcnow() - timedelta(hours=3)
        )
        doctor_user.set_password('doctor123')
        
        staff_user = User(
            username='staff',
            email='healthstaff@district.gov',
            full_name='Priya Sharma (Field Health Coordinator)',
            role='Health_Officer',
            phone='+91 9844556677',
            avatar='default-avatar.png',
            is_active=True,
            created_at=datetime.utcnow() - timedelta(days=30),
            last_login=datetime.utcnow() - timedelta(days=1)
        )
        staff_user.set_password('staff123')
        
        db.session.add_all([admin_user, doctor_user, staff_user])
        db.session.commit()
        
        print("Seeding Hospitals...")
        # 2. Seed Hospitals
        hospitals_data = [
            Hospital(name="City Apex Covid Care Hospital", district="Central District", state="Maharashtra", total_beds=350, occupied_beds=180, icu_beds=50, occupied_icu=28, oxygen_cylinders=120, helpline="1800-111-999", address="45 Health Avenue, Central District"),
            Hospital(name="St. Jude Memorial Hospital", district="North District", state="Maharashtra", total_beds=220, occupied_beds=115, icu_beds=35, occupied_icu=18, oxygen_cylinders=85, helpline="1800-222-888", address="12 Ring Road, North District"),
            Hospital(name="Sunrise Community Healthcare Center", district="South District", state="Maharashtra", total_beds=180, occupied_beds=92, icu_beds=25, occupied_icu=12, oxygen_cylinders=60, helpline="1800-333-777", address="78 Marine Drive, South District"),
            Hospital(name="Lifeline Multi-Speciality Hospital", district="East District", state="Maharashtra", total_beds=300, occupied_beds=145, icu_beds=40, occupied_icu=22, oxygen_cylinders=110, helpline="1800-444-666", address="90 Tech Boulevard, East District"),
            Hospital(name="Valley General Hospital", district="West District", state="Maharashtra", total_beds=200, occupied_beds=85, icu_beds=30, occupied_icu=10, oxygen_cylinders=75, helpline="1800-555-555", address="23 Hill View Highway, West District"),
        ]
        db.session.add_all(hospitals_data)
        db.session.commit()

        print("Seeding Places...")
        # 3. Seed Places across various districts
        places_raw = [
            {"name": "Green Valley Colony", "vc": "Sector 4", "mandal": "Central Taluk", "dist": "Central District", "state": "Maharashtra", "pin": "400001", "pop": 18500, "fam": 4200},
            {"name": "Shivaji Nagar", "vc": "Ward 12", "mandal": "North Taluk", "dist": "North District", "state": "Maharashtra", "pin": "400015", "pop": 24000, "fam": 5600},
            {"name": "Lotus Park Heights", "vc": "Urban Ward 8", "mandal": "South Taluk", "dist": "South District", "state": "Maharashtra", "pin": "400028", "pop": 12000, "fam": 2800},
            {"name": "Lakeview Enclave", "vc": "East Zone 3", "mandal": "East Taluk", "dist": "East District", "state": "Maharashtra", "pin": "400050", "pop": 16500, "fam": 3900},
            {"name": "Pawan Dham Village", "vc": "Rural Block A", "mandal": "West Taluk", "dist": "West District", "state": "Maharashtra", "pin": "400072", "pop": 8500, "fam": 1900},
            {"name": "Adarsh Nagar", "vc": "Sector 9", "mandal": "Central Taluk", "dist": "Central District", "state": "Maharashtra", "pin": "400004", "pop": 21000, "fam": 4900},
            {"name": "Royal Palms Avenue", "vc": "North Zone 2", "mandal": "North Taluk", "dist": "North District", "state": "Maharashtra", "pin": "400021", "pop": 14200, "fam": 3300},
            {"name": "Kasturba Hamlet", "vc": "South Block 5", "mandal": "South Taluk", "dist": "South District", "state": "Maharashtra", "pin": "400035", "pop": 6800, "fam": 1500},
            {"name": "Golden Hill Township", "vc": "East Ward 7", "mandal": "East Taluk", "dist": "East District", "state": "Maharashtra", "pin": "400062", "pop": 31000, "fam": 7200},
            {"name": "Shanti Nagar", "vc": "West Zone 4", "mandal": "West Taluk", "dist": "West District", "state": "Maharashtra", "pin": "400088", "pop": 15500, "fam": 3600},
            {"name": "Millennium Plaza Circle", "vc": "Central Zone 1", "mandal": "Central Taluk", "dist": "Central District", "state": "Maharashtra", "pin": "400010", "pop": 29000, "fam": 6800},
            {"name": "Vidya Vihar Campus", "vc": "North Sector 6", "mandal": "North Taluk", "dist": "North District", "state": "Maharashtra", "pin": "400077", "pop": 9800, "fam": 2100},
            {"name": "Harbor Bay Residency", "vc": "South Coastal", "mandal": "South Taluk", "dist": "South District", "state": "Maharashtra", "pin": "400005", "pop": 17800, "fam": 4100},
            {"name": "Sundar Gram", "vc": "East Rural Sector", "mandal": "East Taluk", "dist": "East District", "state": "Maharashtra", "pin": "400095", "pop": 5400, "fam": 1200},
            {"name": "Mahatma Phule Basti", "vc": "West Ward 10", "mandal": "West Taluk", "dist": "West District", "state": "Maharashtra", "pin": "400080", "pop": 22400, "fam": 5100}
        ]

        created_places = []
        for p in places_raw:
            place_obj = Place(
                place_name=p["name"],
                village_city=p["vc"],
                mandal_taluk=p["mandal"],
                district=p["dist"],
                state=p["state"],
                pincode=p["pin"],
                total_population=p["pop"],
                total_families=p["fam"],
                affected_status="Not Affected",
                positive_cases=0,
                active_cases=0,
                recovered_cases=0,
                death_cases=0,
                vaccinated_count=0,
                not_vaccinated_count=0,
                last_updated=datetime.utcnow() - timedelta(days=random.randint(1, 10))
            )
            db.session.add(place_obj)
            created_places.append(place_obj)
        db.session.commit()

        print("Seeding Members & COVID Cases...")
        # 4. Seed Members with comprehensive realistic diversity
        first_names_m = ["Aarav", "Vikram", "Rohan", "Aditya", "Rahul", "Arjun", "Karan", "Siddharth", "Manish", "Amit", "Suresh", "Nikhil", "Deepak", "Vivek", "Gaurav", "Pranav", "Ashwin", "Dev", "Rajesh", "Sameer"]
        first_names_f = ["Ananya", "Sneha", "Pooja", "Diya", "Riya", "Kavya", "Tanvi", "Neha", "Meera", "Swati", "Nandini", "Isha", "Roshni", "Anjali", "Shreya", "Aditi", "Priyanka", "Divya", "Sunita", "Preeti"]
        last_names = ["Sharma", "Verma", "Patel", "Mehta", "Kulkarni", "Deshmukh", "Chavan", "Iyer", "Nair", "Reddy", "Gupta", "Malhotra", "Bose", "Joshi", "Singhania", "Rao", "Shetty", "Pandey", "Saxena", "Kapoor"]
        occupations = ["Software Engineer", "Healthcare Worker", "School Teacher", "Bank Manager", "Shop Owner", "Civil Engineer", "Student", "Police Officer", "Accountant", "Homemaker", "Chef", "Pharmacist", "Electrician", "Architect"]
        vaccine_types = ["Covishield", "Covaxin", "Pfizer", "Moderna", "Sputnik V"]
        symptoms_pool = ["High Fever, Dry Cough", "Loss of Taste & Smell, Fatigue", "Severe Breathlessness, Sore Throat", "Headache, Body Pain, Mild Cough", "Chest Tightness, Low SpO2", "Mild Fever, Chills"]
        doctors = ["Dr. Rajesh Kumar", "Dr. Ananya Sen", "Dr. Suresh Patil", "Dr. Shalini Roy", "Dr. Arvind Iyer"]

        members_list = []
        created_cases = []
        created_vaccinations = []
        cert_counter = 1001

        for i in range(1, 65):
            is_female = (i % 2 == 0)
            fname = random.choice(first_names_f) if is_female else random.choice(first_names_m)
            lname = random.choice(last_names)
            full_name = f"{fname} {lname}"
            age = random.randint(12, 78)
            dob_year = 2026 - age
            dob = datetime(dob_year, random.randint(1, 12), random.randint(1, 28)).date()
            gender = "Female" if is_female else "Male"
            mob = f"98{random.randint(10000000, 99999999)}"
            email = f"{fname.lower()}.{lname.lower()}{random.randint(10, 99)}@gmail.com"
            aadhaar = f"{random.randint(1000, 9999)} {random.randint(1000, 9999)} {random.randint(1000, 9999)}"
            place_chosen = random.choice(created_places)
            occ = random.choice(occupations)

            # Determine COVID status distribution:
            # ~18% Active, ~32% Recovered, ~5% Deceased, ~45% Negative
            roll = random.random()
            if roll < 0.18:
                c_status = "Active"
                inf_date = (datetime.utcnow() - timedelta(days=random.randint(2, 12))).date()
                rec_date = None
            elif roll < 0.50:
                c_status = "Recovered"
                inf_date = (datetime.utcnow() - timedelta(days=random.randint(20, 50))).date()
                rec_date = (inf_date + timedelta(days=random.randint(10, 18)))
            elif roll < 0.55:
                c_status = "Deceased"
                inf_date = (datetime.utcnow() - timedelta(days=random.randint(30, 70))).date()
                rec_date = None
            else:
                c_status = "Negative"
                inf_date = None
                rec_date = None

            # Determine Vaccination status:
            # ~60% Fully Vaccinated, ~25% Partially Vaccinated, ~15% Not Vaccinated
            vax_roll = random.random()
            vax_brand = random.choice(vaccine_types)
            dose1 = None
            dose2 = None
            booster = None

            if vax_roll < 0.60:
                vax_status = "Fully Vaccinated"
                dose1 = (datetime.utcnow() - timedelta(days=random.randint(120, 240))).date()
                dose2 = (dose1 + timedelta(days=random.randint(30, 84)))
                if random.random() < 0.45:
                    booster = (dose2 + timedelta(days=random.randint(90, 180)))
            elif vax_roll < 0.85:
                vax_status = "Partially Vaccinated"
                dose1 = (datetime.utcnow() - timedelta(days=random.randint(10, 50))).date()
            else:
                vax_status = "Not Vaccinated"
                vax_brand = None

            member = Member(
                member_code=f"MEM-{10000 + i}",
                full_name=full_name,
                age=age,
                gender=gender,
                dob=dob,
                mobile_number=mob,
                email=email,
                aadhaar_number=aadhaar,
                address=f"Flat {random.randint(101, 909)}, {place_chosen.place_name}, {place_chosen.village_city}",
                place_id=place_chosen.id,
                occupation=occ,
                covid_status=c_status,
                infection_date=inf_date,
                recovery_date=rec_date,
                vaccination_status=vax_status,
                vaccine_name=vax_brand,
                dose1_date=dose1,
                dose2_date=dose2,
                booster_date=booster,
                hospital_name=random.choice(hospitals_data).name if c_status != "Negative" else None,
                doctor_name=random.choice(doctors) if c_status != "Negative" else None,
                medical_remarks=f"Patient vitals monitored regularly. BP normal, SpO2: {random.randint(93, 99)}%." if c_status != "Negative" else "Routine annual healthcare screening.",
                photo_url='default-user.png',
                created_at=datetime.utcnow() - timedelta(days=random.randint(5, 90))
            )
            db.session.add(member)
            members_list.append(member)
        db.session.commit()

        # 5. Create CovidCases and Vaccination records linked to members
        print("Linking detailed Case records and Vaccination entries...")
        for m in members_list:
            if m.covid_status in ["Active", "Recovered", "Deceased"]:
                # Create Covid Case record
                q_status = "Home Isolation"
                severity = "Mild"
                ct_score = f"{random.randint(8, 22)}/25"
                symptoms = random.choice(symptoms_pool)
                ward_no = None
                
                if m.covid_status == "Active":
                    r_mode = random.random()
                    if r_mode < 0.35:
                        q_status = "Home Isolation"
                        severity = "Mild"
                    elif r_mode < 0.65:
                        q_status = "Hospitalized"
                        severity = "Moderate"
                        ward_no = f"Ward {random.randint(1, 5)} - Bed {random.randint(101, 140)}"
                    elif r_mode < 0.85:
                        q_status = "Oxygen Support"
                        severity = "Severe"
                        ward_no = f"O2 Ward - Bed {random.randint(201, 230)}"
                    else:
                        q_status = "ICU"
                        severity = "Critical"
                        ward_no = f"ICU Pod {random.randint(1, 8)}"
                elif m.covid_status == "Recovered":
                    q_status = "Discharged"
                    severity = random.choice(["Mild", "Moderate", "Severe"])
                elif m.covid_status == "Deceased":
                    q_status = "Deceased"
                    severity = "Critical"
                    ward_no = f"ICU Pod {random.randint(1, 8)}"

                case_obj = CovidCase(
                    case_code=f"COV-{random.randint(100000, 999999)}",
                    member_id=m.id,
                    place_id=m.place_id,
                    admission_date=m.infection_date or (datetime.utcnow().date() - timedelta(days=5)),
                    covid_variant=random.choice(["Omicron BA.5", "Delta Plus", "JN.1 Variant", "Omicron XBB"]),
                    symptoms=symptoms,
                    ct_score=ct_score,
                    severity=severity,
                    quarantine_status=q_status,
                    ward_bed_no=ward_no,
                    assigned_doctor=m.doctor_name or random.choice(doctors),
                    recovery_date=m.recovery_date,
                    death_date=m.infection_date + timedelta(days=random.randint(7, 14)) if m.covid_status == "Deceased" and m.infection_date else None,
                    notes=f"Clinical protocol followed. Medications administered: Paracetamol, Azithromycin, Vitamin C/Zinc. {m.medical_remarks}"
                )
                db.session.add(case_obj)

            # Vaccination entries
            if m.vaccination_status in ["Partially Vaccinated", "Fully Vaccinated"] and m.dose1_date:
                v1 = Vaccination(
                    member_id=m.id,
                    dose_number=1,
                    vaccine_name=m.vaccine_name or "Covishield",
                    vaccination_date=m.dose1_date,
                    center_name=random.choice(hospitals_data).name,
                    batch_number=f"VAC-B{random.randint(100, 999)}X",
                    vaccinated_by="Sister Mary V.",
                    certificate_no=f"COV-VAX-{cert_counter}",
                    next_due_date=m.dose1_date + timedelta(days=84) if m.vaccination_status == "Partially Vaccinated" else None
                )
                db.session.add(v1)
                cert_counter += 1

                if m.vaccination_status == "Fully Vaccinated" and m.dose2_date:
                    v2 = Vaccination(
                        member_id=m.id,
                        dose_number=2,
                        vaccine_name=m.vaccine_name or "Covishield",
                        vaccination_date=m.dose2_date,
                        center_name=random.choice(hospitals_data).name,
                        batch_number=f"VAC-B{random.randint(100, 999)}Y",
                        vaccinated_by="Staff Nurse Robert K.",
                        certificate_no=f"COV-VAX-{cert_counter}",
                        next_due_date=m.dose2_date + timedelta(days=180)
                    )
                    db.session.add(v2)
                    cert_counter += 1

                if m.booster_date:
                    v3 = Vaccination(
                        member_id=m.id,
                        dose_number=3,
                        vaccine_name=m.vaccine_name or "Covishield",
                        vaccination_date=m.booster_date,
                        center_name=random.choice(hospitals_data).name,
                        batch_number=f"VAC-B{random.randint(100, 999)}Z",
                        vaccinated_by="Officer Ankit Dave",
                        certificate_no=f"COV-VAX-{cert_counter}"
                    )
                    db.session.add(v3)
                    cert_counter += 1

        db.session.commit()

        print("Recalculating Place aggregates...")
        for p in created_places:
            p.recalculate_statistics()
        db.session.commit()

        print("Seeding Notifications...")
        # 6. Seed Notifications
        sample_notifs = [
            Notification(title="Emergency Containment Alert", message="Shivaji Nagar (North District) declared a micro-containment zone due to 5 active cases in 48 hours.", category="Containment Zone", alert_level="High", target_url="/places", created_at=datetime.utcnow() - timedelta(hours=2)),
            Notification(title="High ICU Occupancy Warning", message="City Apex Hospital ICU occupancy reached 85%. Additional ventilator support requested.", category="Emergency", alert_level="High", target_url="/cases", created_at=datetime.utcnow() - timedelta(hours=5)),
            Notification(title="Mega Vaccination Drive Complete", message="Successfully administered over 1,200 vaccine doses across East & South district camps.", category="Vaccination", alert_level="Low", target_url="/vaccinations", created_at=datetime.utcnow() - timedelta(days=1)),
            Notification(title="New Recovery Milestone", message="District recovery rate has crossed 88.5% this week with 14 patients safely discharged.", category="Recovery", alert_level="Low", target_url="/cases", created_at=datetime.utcnow() - timedelta(days=2)),
            Notification(title="New Omicron Sub-variant Screened", message="Health laboratory confirmed detection of 2 sub-variant cases; contact tracing initiated.", category="New Case", alert_level="Medium", target_url="/cases", created_at=datetime.utcnow() - timedelta(days=3))
        ]
        db.session.add_all(sample_notifs)

        print("Seeding Activity Logs...")
        # 7. Seed Activity Logs
        sample_logs = [
            ActivityLog(user_id=admin_user.id, action="System Initialized", module="System", details="Database tables created and sample healthcare datasets populated.", ip_address="127.0.0.1", created_at=datetime.utcnow() - timedelta(days=30)),
            ActivityLog(user_id=admin_user.id, action="Place Created", module="Place Management", details="Added 'Lotus Park Heights' in South District with 12,000 population.", ip_address="127.0.0.1", created_at=datetime.utcnow() - timedelta(days=15)),
            ActivityLog(user_id=doctor_user.id, action="Case Admitted", module="COVID Cases", details="Admitted patient COV-982144 to ICU Pod 3 at City Apex Hospital.", ip_address="192.168.1.15", created_at=datetime.utcnow() - timedelta(days=4)),
            ActivityLog(user_id=staff_user.id, action="Vaccination Recorded", module="Vaccination Management", details="Recorded Dose 2 for member MEM-10014 (Covishield).", ip_address="192.168.1.28", created_at=datetime.utcnow() - timedelta(days=2)),
            ActivityLog(user_id=admin_user.id, action="Report Exported", module="Reports", details="Generated and downloaded Monthly COVID-19 District Epidemiological PDF Report.", ip_address="127.0.0.1", created_at=datetime.utcnow() - timedelta(hours=1))
        ]
        db.session.add_all(sample_logs)

        print("Seeding Settings...")
        # 8. Seed System Settings
        sample_settings = [
            Setting(setting_key="app_title", setting_value="COVID-19 Public Health & Visualization Portal", description="Application branding title"),
            Setting(setting_key="alert_email_notifications", setting_value="true", description="Enable automated emergency email alerts to district heads"),
            Setting(setting_key="containment_threshold_cases", setting_value="5", description="Number of active cases in a place triggering containment zone status"),
            Setting(setting_key="default_theme", setting_value="dark", description="Default UI color theme (light / dark)"),
            Setting(setting_key="auto_refresh_seconds", setting_value="60", description="Live dashboard metric polling interval in seconds")
        ]
        db.session.add_all(sample_settings)

        print("Importing State-wise COVID Dataset from Excel...")
        # 9. Import State-wise COVID Dataset
        from services.state_data_service import StateDataService
        excel_res = StateDataService.import_excel_dataset()
        print(f" -> State data import result: {excel_res}")

        db.session.commit()
        print("Database initialization and data seeding completed successfully!")

if __name__ == '__main__':
    seed_database()
