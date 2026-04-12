# Graphene Trace — Sensore Django Platform

A full Django web application for the Graphene Trace MedTech startup.
Processes 32×32 pressure sensor data from the **Sensore** smart mat
to prevent pressure ulcers.

**Team / author (example):** MUDDA AVINADH  
**GitHub:** [github.com/Avinadhmudda15/graphene_django](https://github.com/Avinadhmudda15/graphene_django)  
**Module:** MOD004364 Advanced Web Solutions

---

## Windows — run from this folder (your PC)

Project root on disk (where `manage.py` is):

`C:\Users\uzmat\Desktop\graphene_trace_django\graphene_django`

Open **PowerShell** and run:

```powershell
cd C:\Users\uzmat\Desktop\graphene_trace_django\graphene_django

# One-time: create virtual environment
python -m venv venv

# Every session: activate it
.\venv\Scripts\Activate.ps1

# One-time (or after pulling updates): install dependencies
python -m pip install --upgrade pip
pip install -r requirements.txt

# One-time: database tables
python manage.py migrate

# Optional: demo users + sample CSV ingest
python manage.py seed_data

# Run the site
python manage.py runserver
```

Browser: **http://127.0.0.1:8000/**

If `Activate.ps1` is blocked: run PowerShell **as Administrator** once:

`Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser`

---

## Fresh machine (any OS) — minimum steps

```bash
cd graphene_django
python -m venv venv
# Windows: venv\Scripts\activate
# Mac/Linux: source venv/bin/activate
pip install -r requirements.txt
python manage.py migrate
python manage.py seed_data
python manage.py runserver
```

---

## Push updates to GitHub (from your Windows folder)

Do **not** commit `venv/` (it is listed in `.gitignore`). If `venv` was committed before, remove it from Git once:

```powershell
cd C:\Users\uzmat\Desktop\graphene_trace_django\graphene_django
git rm -r --cached venv 2>$null; git commit -m "Stop tracking venv"  # only if venv was tracked
```

**First time linking this folder to your existing repo:**

```powershell
cd C:\Users\uzmat\Desktop\graphene_trace_django\graphene_django
git init
git checkout -b feature/graphene
git add .
git status
git commit -m "feat: Sensore platform — dashboards, CSV ingest, reports, RBAC"
git remote add origin https://github.com/Avinadhmudda15/graphene_django.git
git push -u origin feature/graphene
```

If GitHub already has commits and `git push` is **rejected**, either **pull and merge** first:

```powershell
git pull origin feature/graphene --allow-unrelated-histories
# fix any conflicts, then:
git push -u origin feature/graphene
```

…or (only if you intend to **replace** the remote branch — confirm with your team):

```powershell
git push -u origin feature/graphene --force
```

---

## Quick Start (3 commands)

```bash
# Mac / Linux
bash setup.sh

# Windows
setup.bat

# Then run:
source venv/bin/activate          # Windows: venv\Scripts\activate
python manage.py runserver
# Open: http://127.0.0.1:8000
```

---

## Manual Setup

```bash
cd graphene_django

# Create and activate virtual environment
python3 -m venv venv
source venv/bin/activate         # Windows: venv\Scripts\activate

# Install requirements (same on all machines)
pip install -r requirements.txt

# (Optional) place GTLB-Data/ folder or GTLB-Data.zip in project root

# Run migrations
python manage.py migrate

# Create admin superuser
python manage.py createsuperuser --username admin
# or use the shell:
python manage.py shell -c "
from django.contrib.auth import get_user_model
U = get_user_model()
U.objects.create_superuser('admin','admin@gt.com','admin123', role='admin')
"

# Seed sample users + ingest CSV data
python manage.py seed_data
# Custom data location:
python manage.py seed_data --csv-zip /path/to/GTLB-Data.zip
python manage.py seed_data --csv-dir /path/to/GTLB-Data/

# Run development server
python manage.py runserver
```

---

## Login Credentials (after seed_data)

| Role       | Username  | Password  |
|------------|-----------|-----------|
| Admin      | admin     | admin123  |
| Clinician  | dr_jones  | jones123  |
| Clinician  | dr_patel  | patel123  |
| Patient    | alice     | alice123  |
| Patient    | bob       | bob123    |
| Patient    | carol     | carol123  |
| Patient    | david     | david123  |
| Patient    | eve       | eve123    |

---

## Project Structure

```
graphene_django/
├── manage.py
├── requirements.txt
├── setup.sh  /  setup.bat
│
├── graphene_trace/          ← Django project config
│   ├── settings.py
│   ├── urls.py
│   └── wsgi.py
│
├── accounts/                ← Auth: custom User + profiles
│   ├── models.py            User, PatientProfile, ClinicianProfile
│   ├── views.py             Login, logout, user CRUD
│   ├── decorators.py        @role_required
│   └── templates/accounts/
│
├── dashboard/               ← All dashboards + JSON API
│   ├── views.py             Patient/Clinician/Admin dashboards
│   ├── urls.py              + /api/metrics/ /api/frame/ /api/frames/
│   └── templates/
│       ├── patient/         dashboard, alerts, comments
│       ├── clinician/       dashboard, patient_detail, alerts
│       └── admin_panel/     dashboard
│
├── data_processing/         ← CSV ingestion + sensor models
│   ├── models.py            UploadSession, PressureFrame, Alert, Comment
│   ├── parser.py            CSV parser, PPI, contact area, alerts
│   ├── views.py             Upload view (patient + clinician)
│   └── management/commands/seed_data.py
│
├── analytics/               ← Risk scoring + 7-day breakdown
│   └── views.py
│
├── reports/                 ← Daily HTML report (today vs yesterday)
│   └── views.py
│
├── static/
│   ├── css/main.css         Dark medical dashboard theme
│   └── js/
│       ├── heatmap.js       Canvas 32×32 renderer + playback
│       └── charts.js        Chart.js line graphs
│
└── templates/
    └── base.html            Sidebar layout base template
```

---

## Features

### Patient Dashboard
- 32×32 heatmap rendered on HTML5 Canvas — thermal colour scale
- **Playback timeline** — scrub or auto-play frames at 5fps
- Session selector — switch between CSV upload sessions
- Live metrics: Peak Pressure, Contact Area %, Average Pressure
- Time-range charts: 1h / 6h / 24h (Chart.js)
- Plain-English pressure explanation
- Alert log with severity (info / warning / critical)
- Comment system with clinician reply thread

### Clinician Dashboard
- Patient list (assigned patients; `dr_patel` can be set to see **all** patients via clinician profile / seed)
- Upload CSVs on behalf of a patient
- Aggregated alert feed across all patients
- Reply to patient comments in-thread
- Full heatmap + charts per patient

### Admin Panel
- Create / edit / delete users (patient, clinician, admin)
- Assign patients to clinicians
- System-wide statistics

### Analytics
- Heuristic risk score 0–10 (based on last 24h data)
- 7-day daily breakdown table + bar chart

### Reports
- Today vs yesterday comparison (peak, contact, alerts)
- Day-on-day % change indicators
- 7-day trend chart
- Printable HTML output

---

## Tech Stack

| Layer      | Technology                              |
|------------|-----------------------------------------|
| Backend    | Python 3.10+, Django 4.2+               |
| Database   | SQLite (development)                    |
| Frontend   | HTML5, CSS3, Vanilla JavaScript         |
| Charts     | Chart.js 4.4 (CDN)                      |
| Fonts      | Google Fonts (DM Sans, Space Grotesk)   |
| Analysis   | NumPy (BFS flood-fill PPI algorithm)    |

---

## CSV Data Format

Files named: `<user_id_hash>_<YYYYMMDD>.csv`  
Example: `1c0fd777_20251011.csv`

- No header row
- Each **frame** = 32 consecutive rows × 32 comma-separated values
- Values: 1–4095 (1 = idle / no load, 4095 = saturation) per case study
- Frames are assigned timestamps starting at midnight on the file date,
  spaced 5 seconds apart

---

## Configuration (settings.py)

```python
PRESSURE_ALERT_THRESHOLD = 500   # Alert trigger level (0-4095)
CONTACT_THRESHOLD        = 50    # Min value to count as contact pixel
MIN_REGION_PIXELS        = 10    # Min connected pixels for PPI calc
```
