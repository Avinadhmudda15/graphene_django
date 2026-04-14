# Graphene Trace — Sensore Django Platform

Full-stack Django web application for the Graphene Trace MedTech live brief.
Module: MOD004364 Advanced Web Solutions — Anglia Ruskin University.

The platform processes 32x32 pressure sensor CSV data from the Sensore smart mat
to prevent pressure ulcers. Role-based dashboards for patients, clinicians, and admins
with live heatmap, time-series charts, automated alerts, daily reports, and a
patient comment / clinician reply system.

Author: MUDDA AVINADH
GitHub: https://github.com/Avinadhmudda15/graphene_django
Module: MOD004364 Advanced Web Solutions
Submitted: April 2026

---

## Case Study Requirements Coverage

| # | Requirement | Status | Where |
|---|-------------|--------|-------|
| 1 | Database structure for time-ordered data per user | Done | PressureFrame model, indexed on (patient, timestamp) |
| 2 | Three user roles: patient, clinician, admin | Done | accounts/models.py — custom User with RBAC |
| 3 | Analyse pressure map, generate alerts, flag frames | Done | parser.py check_alert(), Alert model, is_flagged |
| 4a | Peak Pressure Index (PPI), exclude regions < 10 px | Done | parser.py _ppi() — BFS flood-fill algorithm |
| 4b | Contact Area % | Done | parser.py analyse_frame() |
| 5 | Graphs with selectable time periods (1h, 6h, 24h) | Done | charts.js — dashboard and analytics pages |
| 6 | Reports with day-to-day comparison | Done | reports/ app — today vs yesterday, % change, 7-day trend |
| 7 | Comment system with clinician reply thread | Done | Comment model, patient comments, clinician reply |
| N1 | Plain-English explanation for patient | Done | parser.py generate_explanation() |
| N2 | Risk score (additional metric beyond PPI) | Done | risk_score.py — heuristic 0-10 score |

---

## Quick Start — Windows

Project root (where manage.py lives):
    C:\Users\uzmat\Desktop\graphene_trace_django\graphene_django

Open PowerShell in that folder:

    python -m venv venv
    .\venv\Scripts\Activate.ps1
    pip install -r requirements.txt
    python manage.py migrate
    python manage.py seed_data
    python manage.py runserver

Open http://127.0.0.1:8000/

If Activate.ps1 is blocked, run once as Administrator:
    Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser

---

## Quick Start — Mac / Linux

    cd graphene_django
    python3 -m venv venv
    source venv/bin/activate
    pip install -r requirements.txt
    python manage.py migrate
    python manage.py seed_data
    python manage.py runserver

---

## Login Credentials (after seed_data)

| Role      | Username | Password  | Notes |
|-----------|----------|-----------|-------|
| Admin     | admin    | admin123  | Create/edit/delete all users |
| Clinician | dr_jones | jones123  | Sees assigned patients only |
| Clinician | dr_patel | patel123  | can_view_all_patients = True |
| Patient   | alice    | alice123  | Assigned to dr_jones |
| Patient   | bob      | bob123    | Assigned to dr_jones |
| Patient   | carol    | carol123  | Assigned to dr_patel |
| Patient   | david    | david123  | Assigned to dr_patel |
| Patient   | eve      | eve123    | Assigned to dr_patel |

---

## Seeding with Custom CSV Data

    python manage.py seed_data
    python manage.py seed_data --csv-dir "C:\path\to\GTLB-Data"
    python manage.py seed_data --csv-zip "C:\path\to\GTLB-Data.zip"

Creates all 8 demo users and ingests all 15 CSV files (5 patients x 3 days).
The command is idempotent — safe to run multiple times.

---

## GitHub — Push Your Work

First time setup:

    cd C:\Users\uzmat\Desktop\graphene_trace_django\graphene_django
    git init
    git checkout -b feature/graphene
    git add .
    git commit -m "feat: Sensore platform — dashboards, CSV ingest, reports, RBAC"
    git remote add origin https://github.com/Avinadhmudda15/graphene_django.git
    git push -u origin feature/graphene

Subsequent pushes:

    git add .
    git commit -m "your message"
    git push

If push is rejected:

    git pull origin feature/graphene --allow-unrelated-histories
    git push -u origin feature/graphene

Remove venv if accidentally committed:

    git rm -r --cached venv
    git commit -m "chore: stop tracking venv"
    git push

---

## Project Structure

    graphene_django/
    |-- manage.py
    |-- requirements.txt
    |-- setup.sh / setup.bat
    |-- REPORT.md                      university report (full text, all sections)
    |-- LOGBOOK.md                     development logbook (week-by-week)
    |
    |-- graphene_trace/                Django project config
    |   |-- settings.py                thresholds, SITE_NAME, CSRF origins
    |   |-- urls.py
    |   |-- context_processors.py
    |   `-- wsgi.py
    |
    |-- accounts/                      Authentication and user management
    |   |-- models.py                  User (3 roles), PatientProfile, ClinicianProfile
    |   |-- views.py                   Login, logout, create/edit/delete users
    |   |-- forms.py                   LoginForm, CreateUserForm, EditUserForm
    |   |-- decorators.py              @role_required
    |   `-- templates/accounts/        login, user_list, create_user, edit_user
    |
    |-- data_processing/               CSV ingestion and sensor analysis
    |   |-- models.py                  UploadSession, PressureFrame, Alert, Comment, Metrics
    |   |-- parser.py                  CSV parser, BFS PPI, contact area, alerts, explanation
    |   |-- risk_score.py              Heuristic 0-10 risk score
    |   |-- reporting.py               Shared date/window helpers
    |   |-- views.py                   UploadView (patient + clinician)
    |   |-- management/commands/
    |   |   `-- seed_data.py           Auto-ingest GTLB CSV + create demo users
    |   `-- templates/data_processing/ upload.html
    |
    |-- dashboard/                     All dashboards and JSON API
    |   |-- views.py                   Patient/Clinician/Admin dashboards + API
    |   |-- urls.py                    /api/metrics/ /api/frame/ /api/frames/ /api/explanation/
    |   `-- templates/
    |       |-- patient/               dashboard, alerts, comments
    |       |-- clinician/             dashboard, patient_detail, alerts
    |       `-- admin_panel/           dashboard
    |
    |-- analytics/                     Risk score + 7-day analytics + time-series charts
    |   |-- views.py
    |   |-- urls.py
    |   `-- templates/analytics/       analytics.html
    |
    |-- reports/                       Daily comparison report
    |   |-- views.py
    |   |-- urls.py
    |   `-- templates/reports/         report.html
    |
    |-- static/
    |   |-- css/main.css               Dark medical dashboard theme
    |   `-- js/
    |       |-- heatmap.js             HTML5 Canvas 32x32 renderer + frame playback
    |       `-- charts.js              Chart.js time-series (1h/6h/24h)
    |
    |-- templates/
    |   `-- base.html                  Sidebar layout, nav, alert badge
    |
    `-- GTLB-Data (1)/                 Sample CSV files (15 files, 5 users x 3 days)

---

## Features

### Patient Dashboard  /dashboard/patient/
- Risk score card (0-10) with colour-coded label (green/amber/red)
- Stat cards: Peak Pressure (PPI), Avg Contact Area %, Total Frames, Alert count
- 32x32 live heatmap on HTML5 Canvas — thermal colour scale (blue to red)
- Frame playback: Play/Pause auto-advance at 5fps, timeline scrubber
- Session selector — switch between uploaded CSV sessions
- Per-frame metrics: Peak, Contact %, Average
- Time-series charts (1h / 6h / 24h) — Peak Pressure and Contact Area %
- Plain-English pressure explanation banner (loaded via API on page load)
- Recent alerts list with severity badges (INFO / WARNING / CRITICAL)

### Patient Alerts  /dashboard/patient/alerts/
- Full alert history with severity, timestamp, and message
- Alerts auto-marked as read on visit

### Patient Comments  /dashboard/patient/comments/
- Submit a comment optionally linked to a specific pressure frame
- View clinician replies in-thread

### Clinician Dashboard  /dashboard/clinician/
- Assigned patient list with avatar initials and click-through to detail
- Aggregated unread alert count across all patients
- Recent alert feed across all assigned patients

### Clinician Patient Detail  /dashboard/clinician/patient/<pk>/
- Full stat cards for the selected patient
- Heatmap + playback + session selector
- Time-series charts (1h / 6h / 24h)
- Alert list for this patient
- Comment/reply thread — clinician can reply in-thread
- Upload CSV data on behalf of the patient
- Link to patient report

### Admin Dashboard  /dashboard/admin/
- System-wide stats: total users, frames, alerts, sessions
- Full user list

### Admin User Management  /accounts/users/
- Create patient, clinician, or admin accounts
- Edit user details, assign patients to clinicians, reset passwords
- Delete users (cannot delete own account)

### Analytics  /analytics/
- Risk score gauge bar with colour-coded fill
- Time-series charts (1h / 6h / 24h) — Peak Pressure and Contact Area %
- 7-day daily summary bar chart (Max Peak + Alerts on dual Y-axis)
- Daily breakdown table: frames, max peak, avg peak, avg contact, alerts

### Reports  /reports/
- Today vs yesterday side-by-side comparison panels
- Day-on-day % change indicators for peak, contact, alerts
- Same clock-hour comparison (this hour today vs same hour yesterday)
- 7-day trend bar chart
- Recent alerts table
- Print button

### Data Upload  /upload/
- Drag-and-drop or click-to-browse CSV / ZIP upload
- Multiple files in one upload
- ZIP archives automatically extracted
- Upload history table with filename, date, frame count, status

---

## Algorithm Details

### Peak Pressure Index (PPI)
File: data_processing/parser.py  Function: _ppi()

BFS flood-fill identifies connected pressure regions above the contact threshold.
Regions with fewer than MIN_REGION_PIXELS (default 10) pixels are excluded.
PPI = maximum sensor value across all qualifying regions.
Matches the case study specification exactly.

### Contact Area %
    (pixels > CONTACT_THRESHOLD) / 1024 * 100

### Alert Thresholds
    peak >= PRESSURE_ALERT_THRESHOLD        -> WARNING
    peak >= PRESSURE_ALERT_THRESHOLD * 1.5  -> CRITICAL

### Risk Score (0-10)
File: data_processing/risk_score.py  Function: compute_patient_risk()
Computed over the last 24 hours (with fallback to latest stored frame):
    avg_peak > 800  -> +3 pts    avg_peak > 400  -> +1 pt
    max_peak > 1500 -> +3 pts    max_peak > 700  -> +1 pt
    alerts > 10     -> +2 pts    alerts > 3      -> +1 pt
    flag_pct > 20%  -> +2 pts    flag_pct > 5%   -> +1 pt
    Score capped at 10.

---

## Configuration (settings.py)

    PRESSURE_ALERT_THRESHOLD = 500   # Alert trigger (sensor units 0-4095)
    CONTACT_THRESHOLD        = 50    # Pixel counts as contact above this
    MIN_REGION_PIXELS        = 10    # Min connected pixels for PPI (case study)
    DATA_UPLOAD_MAX_MB       = 200   # Max upload file size

---

## CSV Data Format

Filename format:  <user_id_hash>_<YYYYMMDD>.csv
Example:          1c0fd777_20251011.csv

- No header row
- Each frame = 32 consecutive rows x 32 comma-separated integers
- Values: 1-4095 (1 = idle, 4095 = saturation)
- Frames stacked vertically: rows 0-31 = frame 0, rows 32-63 = frame 1, etc.
- Timestamps assigned from midnight on the file date, 5 seconds apart

---

## Tech Stack

| Layer | Technology |
|-------|-----------|
| Backend | Python 3.10+, Django 4.2+ |
| Database | SQLite (development) |
| Frontend | HTML5, CSS3, Vanilla JavaScript |
| Charts | Chart.js 4.4 (CDN) |
| Heatmap | HTML5 Canvas API |
| Numerical analysis | NumPy (BFS flood-fill PPI) |
| Fonts | Google Fonts — DM Sans, Space Grotesk |
| Version control | Git + GitHub |

---

## URL Reference

| URL | Access |
|-----|--------|
| /accounts/login/ | Public |
| /accounts/users/ | Admin |
| /accounts/users/create/ | Admin |
| /dashboard/ | All logged-in (role redirect) |
| /dashboard/patient/ | Patient |
| /dashboard/patient/alerts/ | Patient |
| /dashboard/patient/comments/ | Patient |
| /dashboard/clinician/ | Clinician |
| /dashboard/clinician/patient/<pk>/ | Clinician |
| /dashboard/admin/ | Admin |
| /dashboard/api/metrics/ | Authenticated |
| /dashboard/api/frame/<pk>/ | Authenticated |
| /dashboard/api/frames/ | Authenticated |
| /dashboard/api/explanation/ | Authenticated |
| /upload/ | Patient (own data) |
| /upload/patient/<pk>/ | Clinician / Admin |
| /analytics/ | All logged-in |
| /analytics/patient/<pk>/ | Clinician / Admin |
| /reports/ | All logged-in |
| /reports/patient/<pk>/ | Clinician / Admin |