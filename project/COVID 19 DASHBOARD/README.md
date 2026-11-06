# 🦠 COVID-19 Health & Epidemiological Visualization Dashboard

A complete, production-ready, responsive, and fully functional **COVID-19 Visualization Dashboard** web application designed with a modern healthcare-themed user interface. Built with **Python Flask**, **SQLAlchemy ORM (MySQL & SQLite Dual-Engine)**, **Bootstrap 5.3**, **Chart.js 4.4**, **ReportLab (PDF Export)**, and **OpenPyXL (Excel Export)**.

---

## 🌟 Key Features

### 1. 🔐 Authentication & Access Control
- **Secure Authentication**: Username/email and hashed password verification with `scrypt` hashing.
- **Show / Hide Password**: Interactive toggle for seamless credential input.
- **Remember Me**: 30-day persistent session support.
- **Forgot Password Flow**: Verification and self-service password reset.
- **Role-Based Access Control (RBAC)**: Admin, Doctor, and Health Officer permissions.
- **Default Accounts**:
  - **Admin**: `admin` / `admin123`
  - **Doctor**: `doctor` / `doctor123`
  - **Staff**: `staff` / `staff123`

### 2. 📊 State-wise COVID-19 Surveillance Dashboard (`Covid Dashboard.xlsx`)
- **Excel Dataset Integration**: Direct integration and automatic mapping from `Covid Dashboard.xlsx` with zero fake/random data and duplicate protection.
- **8 Dynamic Summary Cards**:
  1. **Total Population** (Cumulative national / state census: `1,429,869,880`)
  2. **Total Affected People** (`Total Cases` = `34,437,307`)
  3. **Total Non-Affected People** (`Population - Total Cases` = `1,395,432,573`)
  4. **Total Active Cases** (`135,918`)
  5. **Total Recovered Cases** (`Discharged` = `33,837,859`)
  6. **Total Deaths** (`463,530`)
  7. **Total Vaccinated People** (`Vaccination data not available` indicator)
  8. **Total Non-Vaccinated People** (`Vaccination data not available` indicator)
- **Interactive State Filter**:
  - Live dropdown selector with all 36 States & Union Territories.
  - Selecting any state instantaneously updates all 8 summary cards, the 4 Chart.js charts, and the data table.
  - "All States" option displays national overview.
- **4 Interactive Chart.js Visualizations**:
  - **Chart 1: State-wise Affected vs Non-Affected** (Bar chart comparing Affected and Non-Affected population with formatted tooltips).
  - **Chart 2: State-wise Deaths** (Bar chart showing fatalities with interactive sorting: Highest to Lowest, Lowest to Highest, and A-Z).
  - **Chart 3: State-wise Active vs Recovered** (Grouped side-by-side bar chart).
  - **Chart 4: Vaccinated vs Non-Vaccinated** (Doughnut chart with genuine data verification; displays a clear data integrity notice when vaccination dataset is not provided).
- **Responsive State Registry Data Table**:
  - Columns: `State | Population | Affected | Non-Affected | Active | Recovered | Deaths | Vaccinated | Non-Vaccinated`.
  - Real-time client-side search by state name.
  - Multi-column ascending and descending sorting.
  - Configurable pagination (10, 20, All).
  - Direct Export to Excel (`.xlsx`) and CSV.
  - Dynamic `<tfoot>` totals row recalculating visible/filtered sums.

### 3. 📊 Admin Dashboard & 12 Animated Statistic Cards
- **12 Live Counter Cards** with smooth ease-out animations:
  1. **Total Places** (Monitored jurisdictions)
  2. **Affected Places** (Active containment areas)
  3. **Not Affected Places** (Green / safe zones)
  4. **Total Population** (Cumulative census under care)
  5. **Total Members** (Registered citizens)
  6. **COVID-19 Positive Members** (Cumulative positive tests)
  7. **Active Cases** (Patients currently under treatment)
  8. **Recovered Members** (Discharged / cured patients)
  9. **Death Cases** (Recorded fatalities)
  10. **Fully Vaccinated Members** (2+ doses / boosted)
  11. **Partially Vaccinated Members** (Dose 1 administered)
  12. **Not Vaccinated Members** (Priority outreach group)
- **5 Dynamic KPI Progress Gauges**:
  - **Recovery Rate (%)**
  - **Death Rate (%)**
  - **Positivity Rate (%)**
  - **Vaccination Coverage (%)**
  - **Active Case Rate (%)**
- **Emergency Containment Marquee**: Live broadcast ticker for high-risk zones and alerts.
- **Hospital Infrastructure Monitor**: General beds, ICU occupancy, and oxygen cylinders ready.

### 3. 📈 Interactive Visual Analytics (Chart.js 4.4)
- **Affected vs Not Affected Places**: Interactive 3D-styled Pie Chart.
- **Vaccination Status Breakdown**: High-contrast Doughnut Chart.
- **District-wise Epidemiological Matrix**: Multi-dataset Grouped Bar Chart.
- **14-Day Transmission Timeline**: Smooth Spline Area/Line Chart comparing daily new cases vs recoveries.
- **Top Affected Hotspots**: Horizontal Bar Chart.
- **Demographics Pyramid**: Gender & Age-bracket breakdown.
- **Vaccine Brand Share**: Donut chart (Covishield, Covaxin, Pfizer, Moderna, Sputnik V).
- **Download as Image**: One-click export of any chart to high-resolution PNG.

### 4. 🗺️ Place Management (Full CRUD)
- **Fields**: Place ID, Place Name, Village/City, Mandal/Taluk, District, State, Pincode, Total Population, Total Families, Affected Status, Positive Cases, Active Cases, Recovered Cases, Death Cases, Vaccinated Count, Not Vaccinated Count, Last Updated Date.
- **Features**: Real-time aggregate calculation, district filters, containment status badge, search.

### 5. 👥 Member Management (Full CRUD)
- **Fields**: Member ID, Full Name, Age, Gender, DOB, Mobile Number, Email, Aadhaar, Residential Address, Place Name, Occupation, COVID Status, Infection Date, Recovery Date, Vaccination Status, Vaccine Name, Dose 1 Date, Dose 2 Date, Booster Date, Hospital Name, Doctor Name, Medical Remarks, Photo.
- **Features**: Comprehensive Health Identity Card with vaccination passport status and infection timeline.

### 6. 🏥 COVID Case Management & Clinical Surveillance
- **Clinical Triage**: Mild, Moderate, Severe, Critical.
- **Quarantine Assignment**: Home Isolation, Hospitalized, Oxygen Support, ICU, Discharged, Deceased.
- **Clinical Vitals**: HRCT severity score, symptoms, ward/bed number, attending doctor.
- **One-Click Discharge**: Instant recovery logging with place aggregate recalculation.

### 7. 💉 Vaccination Management & Passport
- **Dose Tracking**: Dose 1, Dose 2, and Booster doses.
- **Printable Certificate**: Official certificate layout with security hash, vaccination center, and QR verification stamp.

### 8. 📑 Reports & Multi-Format Exporter
- **11 Generated Reports**: Place-wise, District-wise, Vaccination, Active Cases, Recoveries, Deaths, Member Directory, Daily, Weekly, Monthly, and Yearly summaries.
- **Export Formats**:
  - **PDF Export** (Built with `ReportLab` using styled medical tables and KPI summaries).
  - **Excel Export** (`.xlsx` formatted with `OpenPyXL` including column headers and borders).
  - **CSV Stream** (Direct RFC 4180 standard export).
  - **Print Layout** (Clean, dedicated browser print layout).

### 9. 🎨 Design Aesthetics & UI System
- **Healthcare Color Palette**: Medical Blue (`#0d6efd`), Health Teal (`#0d9488`), Emerald Green (`#10b981`), Warning Amber (`#f59e0b`), High-Risk Crimson (`#ef4444`).
- **Dark Mode & Light Mode**: Seamless theme switcher with localStorage persistence.
- **Glassmorphism**: Translucent frosted glass effect (`backdrop-filter: blur(16px)`).
- **Fully Responsive**: Collapsible sidebar on desktop, off-canvas mobile navigation drawer.

---

## 🏗️ Project Architecture & Folder Structure

```
COVID 19 DASHBOARD/
├── app.py                      # Flask Application Factory & Blueprints
├── config.py                   # Configuration for MySQL and SQLite dual-engine
├── models.py                   # Normalized SQLAlchemy Data Models
├── init_db.py                  # Database Seeder with 65+ Members & 15 Places
├── run.py                      # Application Startup Entry Point
├── requirements.txt            # Python Dependencies
├── routes/
│   ├── auth.py                 # Authentication, Login, Password Reset, RBAC
│   ├── dashboard.py            # Main Dashboard & Widgets
│   ├── places.py               # Place Management CRUD
│   ├── members.py              # Member Management CRUD
│   ├── cases.py                # COVID Cases Surveillance & Discharge
│   ├── vaccinations.py         # Vaccination Records & Certificates
│   ├── analytics.py            # Analytical Studio (Chart.js)
│   ├── reports.py              # Reports Hub & PDF/Excel/CSV Exports
│   ├── notifications.py        # Notifications & Broadcast Alerts
│   ├── profile.py              # Admin Profile & Password Change
│   ├── settings.py             # System Settings & Preferences
│   └── api.py                  # JSON REST Endpoints for Charts
├── services/
│   ├── stats_calculator.py     # Aggregation algorithms & rates
│   ├── state_data_service.py   # State-wise Excel dataset importer & calculations
│   ├── export_service.py       # PDF (ReportLab) & Excel (OpenPyXL) Exporter
│   └── logger_service.py       # Audit & Security Logger
├── templates/
│   ├── base.html               # Master Layout
│   ├── layout/                 # Sidebar & Sticky Navbar
│   ├── auth/                   # Login & Forgot Password
│   ├── dashboard/              # 12 Stat Cards & Charts
│   ├── places/                 # Place CRUD & View
│   ├── members/                # Member CRUD & Health Card
│   ├── cases/                  # Case Surveillance & Admission
│   ├── vaccinations/           # Vaccination Records & Certificate
│   ├── analytics/              # Multi-Chart Studio
│   ├── reports/                # Reports & Print View
│   ├── notifications/          # Alerts Center
│   ├── profile/                # Profile & Security
│   ├── settings/               # System Preferences
│   └── errors/                 # 404 & 500 Error Handlers
├── static/
│   ├── css/                    # Custom Design System, Glassmorphism, Dark Mode
│   └── js/                     # State Surveillance Engine, Theme Manager, Charts.js
└── database/
    ├── schema.sql              # MySQL DDL Table Schema Script
    ├── seed_data.sql           # MySQL Sample Data Inserts
    └── covid_dashboard_full.sql # All-in-One MySQL Dump
```

---

## 🚀 Installation & Setup Instructions

### 1. Prerequisites
- **Python 3.9+** (Tested on Python 3.12)
- **Pip package manager**
- (Optional) **MySQL Server 5.7+ / 8.0+** or **XAMPP / WampServer**

### 2. Clone or Extract Project
Open a terminal in the project directory:
```bash
cd "COVID 19 DASHBOARD"
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Database Setup

#### Option A: Instant Zero-Setup (SQLite - Default)
The application is pre-configured with SQLite support out-of-the-box. Simply run:
```bash
python init_db.py
```
This will automatically create all tables and populate realistic sample data (65+ members, 15+ places across 5 districts, clinical cases, vaccination batches, hospitals, and logs).

#### Option B: Using MySQL (phpMyAdmin / MySQL Workbench)
1. Open MySQL Workbench or phpMyAdmin.
2. Import `database/covid_dashboard_full.sql` (or run `database/schema.sql` followed by `database/seed_data.sql`).
3. Set your environment variables in PowerShell / Command Prompt:
   ```bash
   $env:USE_MYSQL="True"
   $env:MYSQL_HOST="localhost"
   $env:MYSQL_USER="root"
   $env:MYSQL_PASSWORD="your_mysql_password"
   $env:MYSQL_DB="covid19_dashboard"
   ```

### 5. Run the Application
```bash
python run.py
```
Open your web browser and navigate to:
```
http://127.0.0.1:5000
```

---

## 🔑 Default Login Credentials

| Role | Username | Password | Access Level |
| :--- | :--- | :--- | :--- |
| **Admin** | `admin` | `admin123` | Full System Access, User Management, Reports Export |
| **Doctor** | `doctor` | `doctor123` | Clinical Case Admission, Vitals Updates, Patient Discharge |
| **Staff** | `staff` | `staff123` | Citizen Registration, Vaccination Drive Logging |

---

## 📡 REST API Endpoints

- `GET /api/stats/summary`: Returns the 12 dashboard metric counts and KPI percentages.
- `GET /api/charts/data`: Returns Chart.js datasets for all 7 visualizations.
- `GET /api/districts/data`: Returns district-wise aggregates.
- `GET /api/notifications/unread`: Returns unread notifications list and count.
- `GET /api/places/search?q=query`: Live AJAX search for places.
- `GET /reports/export/pdf?type=place_wise`: Download formatted PDF report.
- `GET /reports/export/excel?type=place_wise`: Download Excel `.xlsx` workbook.
- `GET /reports/export/csv?type=place_wise`: Download CSV stream.

---

## 🎓 Academic Project Information
- **Project Title**: COVID-19 Health & Epidemiological Visualization Dashboard
- **Technologies Used**: HTML5, CSS3, JavaScript, Bootstrap 5.3, Chart.js 4.4, Python 3.12, Flask, SQLAlchemy, MySQL, OpenPyXL, ReportLab.
- **Design Pattern**: MVC (Model - View - Controller) Architecture with Blueprints and Services Layer.

---
© 2026 COVID-19 Surveillance Portal. All rights reserved.
