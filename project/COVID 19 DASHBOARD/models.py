from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash

db = SQLAlchemy()

class User(db.Model):
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False, index=True)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255), nullable=False)
    full_name = db.Column(db.String(120), nullable=False)
    role = db.Column(db.String(50), default='Admin')  # Admin, Doctor, Health_Officer, Staff
    phone = db.Column(db.String(20), nullable=True)
    avatar = db.Column(db.String(255), default='default-avatar.png')
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    last_login = db.Column(db.DateTime, nullable=True)
    
    # Relationships
    activity_logs = db.relationship('ActivityLog', backref='user', lazy=True, cascade='all, delete-orphan')

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def to_dict(self):
        return {
            'id': self.id,
            'username': self.username,
            'email': self.email,
            'full_name': self.full_name,
            'role': self.role,
            'phone': self.phone,
            'avatar': self.avatar,
            'is_active': self.is_active,
            'created_at': self.created_at.strftime('%Y-%m-%d %H:%M') if self.created_at else None,
            'last_login': self.last_login.strftime('%Y-%m-%d %H:%M') if self.last_login else None
        }


class Place(db.Model):
    __tablename__ = 'places'
    
    id = db.Column(db.Integer, primary_key=True)
    place_name = db.Column(db.String(150), nullable=False, index=True)
    village_city = db.Column(db.String(150), nullable=False)
    mandal_taluk = db.Column(db.String(150), nullable=False)
    district = db.Column(db.String(150), nullable=False, index=True)
    state = db.Column(db.String(100), nullable=False, default='State')
    pincode = db.Column(db.String(20), nullable=False)
    total_population = db.Column(db.Integer, default=0)
    total_families = db.Column(db.Integer, default=0)
    affected_status = db.Column(db.String(50), default='Not Affected')  # 'Affected', 'Not Affected'
    positive_cases = db.Column(db.Integer, default=0)
    active_cases = db.Column(db.Integer, default=0)
    recovered_cases = db.Column(db.Integer, default=0)
    death_cases = db.Column(db.Integer, default=0)
    vaccinated_count = db.Column(db.Integer, default=0)
    not_vaccinated_count = db.Column(db.Integer, default=0)
    last_updated = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    members = db.relationship('Member', backref='place', lazy=True, cascade='all, delete-orphan')
    covid_cases = db.relationship('CovidCase', backref='place', lazy=True)

    def recalculate_statistics(self):
        """Update aggregate counts from members associated with this place."""
        m_list = self.members
        self.positive_cases = sum(1 for m in m_list if m.covid_status in ['Positive', 'Active', 'Recovered', 'Deceased'])
        self.active_cases = sum(1 for m in m_list if m.covid_status in ['Positive', 'Active'])
        self.recovered_cases = sum(1 for m in m_list if m.covid_status == 'Recovered')
        self.death_cases = sum(1 for m in m_list if m.covid_status == 'Deceased')
        self.vaccinated_count = sum(1 for m in m_list if m.vaccination_status in ['Fully Vaccinated', 'Partially Vaccinated'])
        self.not_vaccinated_count = sum(1 for m in m_list if m.vaccination_status == 'Not Vaccinated')
        self.affected_status = 'Affected' if self.positive_cases > 0 else 'Not Affected'
        self.last_updated = datetime.utcnow()

    def to_dict(self):
        return {
            'id': self.id,
            'place_name': self.place_name,
            'village_city': self.village_city,
            'mandal_taluk': self.mandal_taluk,
            'district': self.district,
            'state': self.state,
            'pincode': self.pincode,
            'total_population': self.total_population,
            'total_families': self.total_families,
            'affected_status': self.affected_status,
            'positive_cases': self.positive_cases,
            'active_cases': self.active_cases,
            'recovered_cases': self.recovered_cases,
            'death_cases': self.death_cases,
            'vaccinated_count': self.vaccinated_count,
            'not_vaccinated_count': self.not_vaccinated_count,
            'last_updated': self.last_updated.strftime('%Y-%m-%d %H:%M:%S') if self.last_updated else None
        }


class Member(db.Model):
    __tablename__ = 'members'
    
    id = db.Column(db.Integer, primary_key=True)
    member_code = db.Column(db.String(50), unique=True, nullable=False, index=True)
    full_name = db.Column(db.String(150), nullable=False, index=True)
    age = db.Column(db.Integer, nullable=False)
    gender = db.Column(db.String(20), nullable=False)  # Male, Female, Other
    dob = db.Column(db.Date, nullable=True)
    mobile_number = db.Column(db.String(20), nullable=False)
    email = db.Column(db.String(120), nullable=True)
    aadhaar_number = db.Column(db.String(30), nullable=True)
    address = db.Column(db.Text, nullable=True)
    place_id = db.Column(db.Integer, db.ForeignKey('places.id', ondelete='SET NULL'), nullable=True)
    occupation = db.Column(db.String(100), nullable=True)
    covid_status = db.Column(db.String(50), default='Negative')  # 'Positive', 'Negative', 'Active', 'Recovered', 'Deceased'
    infection_date = db.Column(db.Date, nullable=True)
    recovery_date = db.Column(db.Date, nullable=True)
    vaccination_status = db.Column(db.String(50), default='Not Vaccinated')  # 'Not Vaccinated', 'Partially Vaccinated', 'Fully Vaccinated'
    vaccine_name = db.Column(db.String(100), nullable=True)  # Covaxin, Covishield, Pfizer, Moderna, Sputnik V
    dose1_date = db.Column(db.Date, nullable=True)
    dose2_date = db.Column(db.Date, nullable=True)
    booster_date = db.Column(db.Date, nullable=True)
    hospital_name = db.Column(db.String(150), nullable=True)
    doctor_name = db.Column(db.String(120), nullable=True)
    medical_remarks = db.Column(db.Text, nullable=True)
    photo_url = db.Column(db.String(255), default='default-user.png')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    covid_cases = db.relationship('CovidCase', backref='member', lazy=True, cascade='all, delete-orphan')
    vaccinations = db.relationship('Vaccination', backref='member', lazy=True, cascade='all, delete-orphan')

    def to_dict(self):
        return {
            'id': self.id,
            'member_code': self.member_code,
            'full_name': self.full_name,
            'age': self.age,
            'gender': self.gender,
            'dob': self.dob.strftime('%Y-%m-%d') if self.dob else None,
            'mobile_number': self.mobile_number,
            'email': self.email,
            'aadhaar_number': self.aadhaar_number,
            'address': self.address,
            'place_id': self.place_id,
            'place_name': self.place.place_name if self.place else 'N/A',
            'district': self.place.district if self.place else 'N/A',
            'occupation': self.occupation,
            'covid_status': self.covid_status,
            'infection_date': self.infection_date.strftime('%Y-%m-%d') if self.infection_date else None,
            'recovery_date': self.recovery_date.strftime('%Y-%m-%d') if self.recovery_date else None,
            'vaccination_status': self.vaccination_status,
            'vaccine_name': self.vaccine_name,
            'dose1_date': self.dose1_date.strftime('%Y-%m-%d') if self.dose1_date else None,
            'dose2_date': self.dose2_date.strftime('%Y-%m-%d') if self.dose2_date else None,
            'booster_date': self.booster_date.strftime('%Y-%m-%d') if self.booster_date else None,
            'hospital_name': self.hospital_name,
            'doctor_name': self.doctor_name,
            'medical_remarks': self.medical_remarks,
            'photo_url': self.photo_url,
            'created_at': self.created_at.strftime('%Y-%m-%d %H:%M') if self.created_at else None
        }


class CovidCase(db.Model):
    __tablename__ = 'covid_cases'
    
    id = db.Column(db.Integer, primary_key=True)
    case_code = db.Column(db.String(50), unique=True, nullable=False, index=True)
    member_id = db.Column(db.Integer, db.ForeignKey('members.id', ondelete='CASCADE'), nullable=False)
    place_id = db.Column(db.Integer, db.ForeignKey('places.id', ondelete='SET NULL'), nullable=True)
    admission_date = db.Column(db.Date, nullable=False, default=datetime.utcnow)
    covid_variant = db.Column(db.String(50), default='Delta / Omicron')
    symptoms = db.Column(db.String(255), nullable=True)  # Fever, Cough, Breathlessness, Fatigue
    ct_score = db.Column(db.String(50), nullable=True)   # e.g., '12/25'
    severity = db.Column(db.String(50), default='Moderate')  # 'Mild', 'Moderate', 'Severe', 'Critical'
    quarantine_status = db.Column(db.String(50), default='Home Isolation')  # 'Home Isolation', 'Hospitalized', 'Oxygen Support', 'ICU', 'Discharged', 'Deceased'
    ward_bed_no = db.Column(db.String(50), nullable=True)
    assigned_doctor = db.Column(db.String(120), nullable=True)
    recovery_date = db.Column(db.Date, nullable=True)
    death_date = db.Column(db.Date, nullable=True)
    notes = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id,
            'case_code': self.case_code,
            'member_id': self.member_id,
            'member_name': self.member.full_name if self.member else 'N/A',
            'member_code': self.member.member_code if self.member else 'N/A',
            'place_name': self.place.place_name if self.place else (self.member.place.place_name if self.member and self.member.place else 'N/A'),
            'district': self.place.district if self.place else (self.member.place.district if self.member and self.member.place else 'N/A'),
            'admission_date': self.admission_date.strftime('%Y-%m-%d') if self.admission_date else None,
            'covid_variant': self.covid_variant,
            'symptoms': self.symptoms,
            'ct_score': self.ct_score,
            'severity': self.severity,
            'quarantine_status': self.quarantine_status,
            'ward_bed_no': self.ward_bed_no,
            'assigned_doctor': self.assigned_doctor,
            'recovery_date': self.recovery_date.strftime('%Y-%m-%d') if self.recovery_date else None,
            'death_date': self.death_date.strftime('%Y-%m-%d') if self.death_date else None,
            'notes': self.notes,
            'created_at': self.created_at.strftime('%Y-%m-%d') if self.created_at else None
        }


class Vaccination(db.Model):
    __tablename__ = 'vaccinations'
    
    id = db.Column(db.Integer, primary_key=True)
    member_id = db.Column(db.Integer, db.ForeignKey('members.id', ondelete='CASCADE'), nullable=False)
    dose_number = db.Column(db.Integer, nullable=False)  # 1, 2, 3 (Booster)
    vaccine_name = db.Column(db.String(100), nullable=False)  # Covaxin, Covishield, Pfizer, Moderna, Sputnik V
    vaccination_date = db.Column(db.Date, nullable=False, default=datetime.utcnow)
    center_name = db.Column(db.String(150), nullable=False)
    batch_number = db.Column(db.String(80), nullable=True)
    vaccinated_by = db.Column(db.String(120), nullable=True)
    certificate_no = db.Column(db.String(100), unique=True, nullable=False)
    next_due_date = db.Column(db.Date, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id,
            'member_id': self.member_id,
            'member_name': self.member.full_name if self.member else 'N/A',
            'member_code': self.member.member_code if self.member else 'N/A',
            'dose_number': self.dose_number,
            'vaccine_name': self.vaccine_name,
            'vaccination_date': self.vaccination_date.strftime('%Y-%m-%d') if self.vaccination_date else None,
            'center_name': self.center_name,
            'batch_number': self.batch_number,
            'vaccinated_by': self.vaccinated_by,
            'certificate_no': self.certificate_no,
            'next_due_date': self.next_due_date.strftime('%Y-%m-%d') if self.next_due_date else None
        }


class Hospital(db.Model):
    __tablename__ = 'hospitals'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(150), nullable=False)
    district = db.Column(db.String(150), nullable=False)
    state = db.Column(db.String(100), default='State')
    total_beds = db.Column(db.Integer, default=100)
    occupied_beds = db.Column(db.Integer, default=0)
    icu_beds = db.Column(db.Integer, default=20)
    occupied_icu = db.Column(db.Integer, default=0)
    oxygen_cylinders = db.Column(db.Integer, default=50)
    helpline = db.Column(db.String(50), nullable=True)
    address = db.Column(db.Text, nullable=True)

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'district': self.district,
            'state': self.state,
            'total_beds': self.total_beds,
            'occupied_beds': self.occupied_beds,
            'icu_beds': self.icu_beds,
            'occupied_icu': self.occupied_icu,
            'oxygen_cylinders': self.oxygen_cylinders,
            'helpline': self.helpline,
            'address': self.address
        }


class Notification(db.Model):
    __tablename__ = 'notifications'
    
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(150), nullable=False)
    message = db.Column(db.Text, nullable=False)
    category = db.Column(db.String(50), default='General')  # 'Emergency', 'New Case', 'Recovery', 'Vaccination', 'Containment Zone'
    alert_level = db.Column(db.String(20), default='Medium')  # 'High', 'Medium', 'Low'
    is_read = db.Column(db.Boolean, default=False)
    target_url = db.Column(db.String(255), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id,
            'title': self.title,
            'message': self.message,
            'category': self.category,
            'alert_level': self.alert_level,
            'is_read': self.is_read,
            'target_url': self.target_url,
            'created_at': self.created_at.strftime('%Y-%m-%d %H:%M') if self.created_at else None
        }


class ActivityLog(db.Model):
    __tablename__ = 'activity_logs'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='SET NULL'), nullable=True)
    action = db.Column(db.String(100), nullable=False)
    module = db.Column(db.String(80), nullable=False)
    details = db.Column(db.Text, nullable=True)
    ip_address = db.Column(db.String(50), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id,
            'user_name': self.user.full_name if self.user else 'System',
            'action': self.action,
            'module': self.module,
            'details': self.details,
            'ip_address': self.ip_address,
            'created_at': self.created_at.strftime('%Y-%m-%d %H:%M:%S') if self.created_at else None
        }


class Setting(db.Model):
    __tablename__ = 'settings'
    
    id = db.Column(db.Integer, primary_key=True)
    setting_key = db.Column(db.String(100), unique=True, nullable=False)
    setting_value = db.Column(db.Text, nullable=False)
    description = db.Column(db.String(255), nullable=True)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class StateCovidData(db.Model):
    __tablename__ = 'state_covid_data'
    
    id = db.Column(db.Integer, primary_key=True)
    state_name = db.Column(db.String(100), unique=True, nullable=False, index=True)
    zone = db.Column(db.String(50), nullable=True)  # North, South, East, West, Central, North East
    population = db.Column(db.BigInteger, nullable=False, default=0)
    total_cases = db.Column(db.BigInteger, nullable=False, default=0)   # Affected People = Total Cases
    active_cases = db.Column(db.BigInteger, nullable=False, default=0)  # Active Cases
    discharged = db.Column(db.BigInteger, nullable=False, default=0)    # Recovered / Discharged
    deaths = db.Column(db.BigInteger, nullable=False, default=0)        # Total Deaths
    active_ratio = db.Column(db.Float, default=0.0)
    discharge_ratio = db.Column(db.Float, default=0.0)
    discharge_avg = db.Column(db.String(50), nullable=True)
    death_ratio = db.Column(db.Float, default=0.0)
    death_avg = db.Column(db.String(50), nullable=True)
    
    # Vaccination data fields (explicitly nullable; no fake data generated)
    vaccinated = db.Column(db.BigInteger, nullable=True, default=None)
    non_vaccinated = db.Column(db.BigInteger, nullable=True, default=None)
    vaccination_data_available = db.Column(db.Boolean, default=False)
    
    source_file = db.Column(db.String(255), default='Covid Dashboard.xlsx')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    @property
    def affected(self):
        """Affected People = Total Cases"""
        return self.total_cases

    @property
    def non_affected(self):
        """Non-Affected People = Population - Total Cases"""
        return max(0, (self.population or 0) - (self.total_cases or 0))

    @property
    def recovered(self):
        """Recovered = Discharged"""
        return self.discharged

    def to_dict(self):
        return {
            'id': self.id,
            'state_name': self.state_name,
            'zone': self.zone or 'N/A',
            'population': int(self.population or 0),
            'affected': int(self.affected),
            'non_affected': int(self.non_affected),
            'active': int(self.active_cases or 0),
            'recovered': int(self.recovered or 0),
            'deaths': int(self.deaths or 0),
            'vaccinated': int(self.vaccinated) if self.vaccinated is not None else None,
            'non_vaccinated': int(self.non_vaccinated) if self.non_vaccinated is not None else None,
            'vaccination_data_available': bool(self.vaccination_data_available),
            'vaccination_status_text': 'Vaccination data not available' if not self.vaccination_data_available or self.vaccinated is None else f"{self.vaccinated:,}",
            'active_ratio': float(self.active_ratio or 0.0),
            'discharge_ratio': float(self.discharge_ratio or 0.0),
            'discharge_avg': self.discharge_avg or 'N/A',
            'death_ratio': float(self.death_ratio or 0.0),
            'death_avg': self.death_avg or 'N/A',
            'updated_at': self.updated_at.strftime('%Y-%m-%d %H:%M:%S') if self.updated_at else None
        }

