# Graphene Trace Case Study Report

Student: MUDDA AVINADH  
Module: MOD004364 Advanced Web Solutions  
Submission: Coursework Application + Report (text format)

---

## 1. Project Overview

Graphene Trace is a Django web application for pressure-ulcer prevention using 32x32 sensor-mat data.
The system ingests CSV pressure frames, computes key risk metrics, raises alerts for dangerous pressure,
and presents role-specific dashboards for patients, clinicians, and administrators.

The project is implemented with HTML, CSS, JavaScript, Python, Django, Git, and GitHub as required.

---

## 2. Requirements Coverage Matrix

1) Database structure for time-ordered data per user  
- Implemented via `PressureFrame` model (`patient`, `timestamp`, indexed by `(patient, timestamp)`).
- Frames are grouped by `UploadSession`.

2) Three user classes (patient, clinician, admin) with controlled access  
- Custom `User` model with `role`.
- `PatientProfile` links patients to clinicians.
- `ClinicianProfile.can_view_all_patients` supports full or assigned-only access.
- Central RBAC method: `User.can_access_patient_data(patient)`.

3) Analyse pressure maps, raise alerts, and flag risky periods  
- `analyse_frame()` computes per-frame metrics.
- `check_alert()` raises warning/critical alerts from peak pressure.
- Flag stored in `PressureFrame.is_flagged` and full event in `Alert`.

4a) Peak Pressure Index with exclusion of small regions (<10 px)  
- BFS connected-component algorithm in `parser._ppi()`.
- Regions under `MIN_REGION_PIXELS=10` are excluded from PPI.

4b) Contact Area %  
- Computed as proportion of pixels above contact threshold.

5) Graphs with user-selectable windows (1h, 6h, 24h)  
- JSON endpoint `dashboard/api/metrics`.
- Chart.js integration in `static/js/charts.js`.
- Available on patient, clinician, and analytics views.

6) Reports with comparison to previous data  
- `reports` module provides latest day vs previous day comparisons.
- Includes same-hour yesterday comparison and 7-day trend chart.

7) User comments and clinician response linked to pressure timeline  
- `Comment` model supports patient comment + clinician reply.
- Optional frame link on patient comment.
- Thread view provided for patients and clinicians.

Nice-to-have requirements implemented  
- Additional metric: risk score (0-10) in `risk_score.py`.
- Plain-English explanation generated from latest frame + alerts.

---

## 3. Architecture and Data Flow

1) CSV upload (`/data/upload/`)  
2) Parsing into 32x32 frames (`parse_csv_frames`)  
3) Metric calculation (`analyse_frame`)  
4) Alert decision (`check_alert`)  
5) Bulk insert to `PressureFrame` and `Alert`  
6) Role-based dashboard/API retrieval  
7) Visualisation through heatmap and charts

Key apps:
- `accounts`: authentication, RBAC, user management
- `data_processing`: parser, ingestion, models, risk scoring
- `dashboard`: role dashboards and JSON APIs
- `analytics`: risk and trend analytics
- `reports`: day-on-day and weekly reporting

---

## 4. Testing and Verification

### 4.1 System checks
- `python manage.py check` -> pass
- `python manage.py makemigrations --check --dry-run` -> no pending model changes
- `python manage.py migrate --check` -> no unapplied migrations

### 4.2 Automated tests added
File: `dashboard/tests.py`

Covered smoke tests:
- Limited clinician cannot read metrics for unassigned patient (403).
- Full-access clinician can read any patient metrics (200 + valid payload).
- Patient cannot open another patient frame API (403).
- Clinician cannot reply to unassigned patient comment.

Run command:
- `python manage.py test dashboard`

### 4.3 Manual role-flow verification
- Patient: dashboard, alerts, comments, explanation banner.
- Clinician: assigned/all-patient views, patient detail, alerts, reply flow.
- Admin: user management and system dashboard totals.

---

## 5. Fixes Applied During Final Review

1) Clinician "view all patients" alerts gap fixed  
- Updated clinician dashboard and clinician alerts views to include all patient alerts when `can_view_all_patients=True`.

2) Clinician reply permission hardening  
- Added access check in clinician reply endpoint to prevent replying to unassigned patient comments.

3) Added automated RBAC/API tests  
- New test suite to provide evidence and prevent regression.

---

## 6. Known Limits and Production Notes

- Deployment security settings are currently dev-oriented (`DEBUG=True`, local `SECRET_KEY`, HTTPS hardening off).
- This is acceptable for local coursework demo but must be hardened before production hosting.
- Database is SQLite for coursework simplicity.

---

## 7. How to Run for Assessment

From project directory (where `manage.py` is located):

1) Create/activate virtual environment  
2) Install dependencies  
3) Run migrations  
4) Seed demo data (optional, if no DB provided)  
5) Start server

Commands:

```bash
pip install -r requirements.txt
python manage.py migrate
python manage.py seed_data
python manage.py runserver
```

Open:
- `http://127.0.0.1:8000/accounts/login/`

---

## 8. Conclusion

The application satisfies the core case-study requirements:
role-based access control, time-ordered pressure data handling, pressure analytics,
alert generation, interactive visualisations, reporting, and clinician-patient communication.

Final hardening for submission included permission fixes, requirement re-validation,
and an automated smoke test suite for critical RBAC/API behavior.
