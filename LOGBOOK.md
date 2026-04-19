# Development Logbook — MUDDA AVINADH

**Module:** MOD004364 Advanced Web Solutions
**Project:** Graphene Trace — Sensore (Django)
**Repository:** https://github.com/Avinadhmudda15/graphene_django
**Submitted:** 

---

> HOW TO USE THIS LOGBOOK
> Copy this file into Word or Google Docs.
> Replace every [SCREENSHOT X] marker with an actual screenshot image.
> The logbook supports your report and is evidence of your individual contribution.

---

## Sprint / Week Log

### Week 1 — Project Setup and Database Design
**Date:** 
**Goal:** Set up the Django project and design the database structure.

**What I did:**
- Created the Django project using `django-admin startproject graphene_trace`.
- Created five Django apps: `accounts`, `data_processing`, `dashboard`, `analytics`, `reports`.
- Designed and implemented the custom `User` model in `accounts/models.py` extending `AbstractUser` with a `role` field (patient / clinician / admin).
- Designed `PatientProfile` (one-to-one with User, stores assigned clinician FK) and `ClinicianProfile` (one-to-one with User, stores department and `can_view_all_patients` flag).
- Ran `python manage.py makemigrations` and `python manage.py migrate` to create the initial database tables.
- Set up `AUTH_USER_MODEL = 'accounts.User'` in settings.py.
- Initialised Git repository and made first commit.

**Evidence:** [SCREENSHOT 1 — GitHub commit showing accounts/models.py with User, PatientProfile, ClinicianProfile]

**Reflection:** Extending Django's `AbstractUser` required careful planning. I had to set `AUTH_USER_MODEL` before running any migrations — doing it after would have caused migration conflicts. The role field approach is simpler than using Django's built-in Groups for this project's scale.

---

### Week 2 — Authentication and Role-Based Access Control
**Date:** 
**Goal:** Implement login/logout and RBAC so each role only sees what they should.

**What I did:**
- Implemented `LoginView` and `LogoutView` in `accounts/views.py` using Django's `authenticate()` and `login()`.
- Created `@role_required` decorator in `accounts/decorators.py` that checks `request.user.role` and raises a 403 or redirects if the role does not match.
- Applied `@role_required` to all dashboard views using `@method_decorator`.
- Implemented `can_access_patient_data()` method on the User model — centralises all access control logic for patient data.
- Built admin user management views: `UserListView`, `CreateUserView`, `EditUserView`, `delete_user`.
- Created `LoginForm`, `CreateUserForm`, `EditUserForm` in `accounts/forms.py`.
- Built login, user list, create user, and edit user HTML templates.

**Evidence:** [SCREENSHOT 2 — GitHub commit showing accounts/views.py, decorators.py, and forms.py]

**Reflection:** Using `method_decorator` with class-based views was new to me. I also had to think carefully about the `can_access_patient_data()` logic — a clinician with `can_view_all_patients=True` should see everyone, otherwise only their assigned patients.

---

### Week 3 — CSV Parser and PPI Algorithm
**Date:** 
**Goal:** Parse the 32x32 sensor CSV files and compute the required metrics.

**What I did:**
- Studied the case study CSV format: 32 rows x 32 values per frame, values 1-4095, stacked vertically.
- Implemented `parse_csv_frames()` in `data_processing/parser.py` to read CSV text and split it into flat 1024-integer lists (one per frame).
- Implemented `_ppi()` — a BFS (Breadth-First Search) flood-fill algorithm that:
  1. Creates a binary mask of pixels above the contact threshold.
  2. Finds all connected regions using BFS.
  3. Discards regions with fewer than 10 pixels (case study requirement).
  4. Returns the maximum sensor value from qualifying regions.
- Implemented `analyse_frame()` which calls `_ppi()` and also computes Contact Area % and average pressure.
- Implemented `check_alert()` which returns severity (warning/critical) based on peak vs threshold.
- Implemented `generate_explanation()` for plain-English patient summaries.
- Implemented `parse_filename()` to extract user hash and date from filenames like `1c0fd777_20251011.csv`.

**Evidence:** [SCREENSHOT 3 — GitHub commit showing data_processing/parser.py with the _ppi() function visible]

**Reflection:** The BFS flood-fill was the most algorithmically complex part of the project. Using NumPy for the array operations made it significantly faster than pure Python loops. Getting the 10-pixel minimum region filter right was critical to match the case study specification exactly.

---

### Week 4 — Frame Storage, Alert System, and CSV Ingestion
**Date:** 
**Goal:** Store parsed frames in the database and generate alerts automatically.

**What I did:**
- Designed and implemented `UploadSession`, `PressureFrame`, `Alert`, `Comment`, and `Metrics` models in `data_processing/models.py`.
- Added database indexes on `(patient, timestamp)` and `(session, frame_index)` for efficient time-range queries.
- Implemented `ingest_csv()` in `data_processing/views.py`:
  - Parses the CSV file using `parse_csv_frames()`.
  - Computes metrics for each frame using `analyse_frame()`.
  - Uses `PressureFrame.objects.bulk_create()` for performance (hundreds of frames per file).
  - Generates `Alert` objects for flagged frames using `bulk_create()`.
- Implemented `UploadView` supporting both patient self-upload and clinician upload on behalf of a patient.
- Added ZIP file support via `extract_csvs_from_zip()`.
- Built the upload HTML template with drag-and-drop zone and upload history table.

**Evidence:** [SCREENSHOT 4 — GitHub commit showing data_processing/models.py and views.py with ingest_csv()]

**Reflection:** Using `bulk_create()` was essential — individual `save()` calls for each frame were far too slow for files with hundreds of frames. I also had to handle the timezone carefully: CSV filenames give a date, so I construct timestamps starting at midnight on that date, spaced 5 seconds apart.

---

### Week 5 — Patient Dashboard and Heatmap
**Goal:** Build the patient-facing dashboard with the live heatmap visualisation.

**What I did:**
- Built `PatientDashboardView` in `dashboard/views.py` passing stats, sessions, alerts, latest frame, and risk score to the template.
- Implemented the 32x32 heatmap renderer in `static/js/heatmap.js`:
  - Fetches the frame list from `/api/frames/` JSON endpoint.
  - Fetches individual frame matrix data from `/api/frame/<pk>/`.
  - Renders each 32x32 grid on an HTML5 Canvas element using a thermal colour scale (blue for low pressure, red for high pressure).
  - Supports Play/Pause auto-playback at 5fps and a timeline scrubber for manual frame selection.
  - Session selector dropdown to switch between uploaded CSV sessions.
- Implemented `api_frames_list` and `api_frame` JSON endpoints in `dashboard/views.py`.
- Built the patient dashboard HTML template with stat cards, heatmap panel, and recent alerts.

**Evidence:** [SCREENSHOT 5 — GitHub commit showing static/js/heatmap.js and dashboard/templates/patient/dashboard.html]

**Reflection:** Canvas rendering required careful colour interpolation to produce a smooth thermal scale. The playback system needed a clean state machine — I used a `setInterval` for auto-play and cleared it on pause. The session selector required re-fetching the frame list when changed.

---

### Week 6 — Time-Series Charts (1h / 6h / 24h)
**Goal:** Add Chart.js line graphs with selectable time periods as required by the case study.

**What I did:**
- Implemented `api_metrics` JSON endpoint in `dashboard/views.py` that accepts a `?hours=` parameter and returns time-series data for peak pressure, contact area %, and average pressure.
- Implemented `chart_metrics_window()` in `data_processing/reporting.py` — handles the edge case where historical CSV data has no frames in the current wall-clock window by anchoring to the latest stored frame.
- Built `ChartManager` in `static/js/charts.js`:
  - Creates two Chart.js line charts: Peak Pressure and Contact Area %.
  - `ChartManager.init()` takes canvas IDs, default hours, optional patient ID, and the API URL.
  - `ChartManager.setHours(n)` destroys and recreates charts with new data.
  - Tab buttons (1h / 6h / 24h) call `setHours()` on click.
- Added the chart panel and time-tab buttons to the patient dashboard template.

**Evidence:** [SCREENSHOT 6 — GitHub commit showing static/js/charts.js and the time-tab buttons in the dashboard template]

**Reflection:** Chart.js requires destroying the existing chart instance before creating a new one with different data — forgetting this causes a "Canvas is already in use" error. The historical data window fallback was a tricky edge case that only appeared when testing with the real GTLB CSV files.

---

### Week 7 — Clinician Dashboard and Patient Detail
**Goal:** Build the clinician-facing views with patient list, alerts, and full patient detail.

**What I did:**
- Built `ClinicianDashboardView` showing the assigned patient list and aggregated alert feed.
- Built `ClinicianPatientView` showing full stats, heatmap, charts, alerts, and comment/reply thread for a selected patient.
- Implemented `ClinicianAlertsView` for the full alert history across all assigned patients.
- Added access control: clinicians can only view patients assigned to them (unless `can_view_all_patients` is set on their profile).
- Added "Upload Data" and "Report" buttons to the patient detail page.
- Wired up `ChartManager` and `HeatmapPlayer` on the clinician patient detail page, passing `patient_id` as a query parameter to the API endpoints.

**Evidence:** [SCREENSHOT 7 — GitHub commit showing clinician/dashboard.html and clinician/patient_detail.html]

**Reflection:** The access control check needed to happen in both the view and the API endpoints — a clinician could bypass the view-level check by calling the API directly with a different `patient_id`. The `_resolve_patient()` helper in `dashboard/views.py` centralises this check for all API endpoints.

---

### Week 8 — Comment System
**Date:** 
**Goal:** Implement the patient comment and clinician reply system required by the case study.

**What I did:**
- The `Comment` model was already in `data_processing/models.py` with fields for `patient`, `frame` (optional FK to PressureFrame), `text`, `clinician_reply`, `reply_by`, and `reply_at`.
- Built `PatientCommentsView` in `dashboard/views.py`:
  - GET: shows all comments for the patient and a dropdown of recent frames to link a comment to.
  - POST: creates a new `Comment` object, optionally linked to a specific frame.
- Built `ClinicianReplyView` that saves the clinician's reply text, `reply_by`, and `reply_at` to the comment.
- Built `patient/comments.html` template with comment submission form and threaded display.
- Added the comment/reply thread to `clinician/patient_detail.html`.

**Evidence:** [SCREENSHOT 8 — GitHub commit showing patient/comments.html and the ClinicianReplyView in dashboard/views.py]

**Reflection:** Linking a comment to a specific frame required a dropdown selector populated with the patient's recent frames. I limited this to the 50 most recent frames to keep the dropdown manageable. The clinician reply is stored on the Comment model itself (not as a separate model) which keeps the data structure simple for this project's scale.

---

### Week 9 — Reports Module
**Date:** 
**Goal:** Build the daily report with day-on-day comparison as required by the case study.

**What I did:**
- Built `ReportView` in `reports/views.py` computing:
  - `primary_data` — metrics for the latest data day (max peak, avg contact, frames, alerts, flagged count).
  - `prev_data` — same metrics for the previous day.
  - `comparison` — percentage change for peak, contact, and alerts using `_pct_change()`.
  - `hour_compare` — same clock-hour comparison between the two days.
  - `weekly` — 7-day daily summary for the trend chart.
- Implemented `_day_summary()` and `_hour_summary()` helper functions.
- Implemented `_pct_change()` with null-safe handling (returns None if previous day has no data).
- Built `reports/report.html` with two-column today/yesterday comparison, delta cards, 7-day bar chart, and print button.
- Made the report accessible to patients (own data), clinicians (assigned patients), and admins.

**Evidence:** [SCREENSHOT 9 — GitHub commit showing reports/views.py and reports/report.html]

**Reflection:** The `_pct_change()` null-safe helper was important — without it, days with zero previous data would cause a division-by-zero error. The same-hour comparison was an interesting feature: it finds the clock hour of the latest frame and compares that specific hour across two days.

---

### Week 10 — Analytics Page and Risk Score
**Date:** 
**Goal:** Build the analytics page with risk scoring and time-series charts.

**What I did:**
- Built `AnalyticsView` in `analytics/views.py` computing a 7-day daily breakdown.
- Implemented `compute_patient_risk()` in `data_processing/risk_score.py`:
  - Queries the last 24 hours of frames (with fallback to latest stored frame for historical data).
  - Scores based on average peak (0-3), max peak (0-3), alert count (0-2), flagged frame % (0-2).
  - Returns a score 0-10 and a plain-English label.
- Added the risk gauge bar (CSS progress bar) to the analytics template.
- Added the 1h/6h/24h time-series charts to the analytics page using `ChartManager` — this was the gap identified in the case study review.
- Added the 7-day bar chart and daily breakdown table.

**Evidence:** [SCREENSHOT 10 — GitHub commit showing analytics/views.py, risk_score.py, and analytics.html with the time-series chart panel]

**Reflection:** The risk score thresholds required tuning with the real GTLB data. The fallback logic in `compute_patient_risk()` mirrors the same pattern used in `chart_metrics_window()` — both need to handle historical CSV data that has no frames in the current wall-clock window.

---

### Week 11 — Plain-English Explanation and Seed Data Command
**Date:** 
**Goal:** Add patient-friendly data explanation and automate demo data loading.

**What I did:**
- Implemented `generate_explanation()` in `data_processing/parser.py` — produces a 2-3 sentence plain-English summary based on peak pressure, contact area %, and recent alert count.
- Added `api_explanation` JSON endpoint in `dashboard/views.py` that returns the explanation for the latest frame.
- Added the explanation banner to the patient dashboard template, loaded via `fetch()` on page load.
- Built `seed_data` management command in `data_processing/management/commands/seed_data.py`:
  - Creates admin, 2 clinicians, and 5 patients with correct profiles and assignments.
  - Auto-detects the `GTLB-Data` folder or accepts `--csv-dir` / `--csv-zip` arguments.
  - Ingests all 15 CSV files using the same `ingest_csv()` pipeline as the upload view.
  - Idempotent — skips users that already exist.

**Evidence:** [SCREENSHOT 11 — GitHub commit showing generate_explanation() in parser.py and seed_data.py management command]

**Reflection:** Writing plain-English output that is genuinely useful to a non-technical patient required thinking carefully about the language. I used threshold bands (e.g. peak > 1500 = "very high", > 800 = "significant") to produce contextually appropriate messages. The seed command's idempotency was important for development — running it multiple times should not create duplicate users or data.

---

### Week 12 — Testing, Bug Fixes, and Presentation Prep
**Date:** 
**Goal:** Test all features end-to-end, fix bugs, and prepare for the presentation.

**What I did:**
- Ran manual tests across all three user roles (patient, clinician, admin) — see Testing section of report.
- Fixed timezone-anchoring bug: historical CSV data (October 2025) had no frames in the current wall-clock window, causing charts to show empty. Fixed by adding fallback logic in `chart_metrics_window()` and `compute_patient_risk()` to anchor the window to the latest stored frame.
- Fixed `_day_summary()` timezone issue — replaced `timezone.make_aware()` with `.replace(tzinfo=dt_timezone.utc)` to avoid "naive datetime" errors.
- Tested CSV ingestion with all 15 GTLB files (5 users x 3 days).
- Tested alert generation at warning (>=500) and critical (>=750) thresholds.
- Tested RBAC: confirmed patients cannot access other patients' data.
- Prepared presentation slides covering architecture, features, and live demo.

**Evidence:** [SCREENSHOT 12 — GitHub commit showing bug fixes in reporting.py and risk_score.py]

**Reflection:** The timezone bug was the most subtle issue in the project. Django stores all datetimes in UTC, but the CSV filenames give a local date. The fallback logic to anchor the chart window to the latest stored frame was the correct fix — it means the charts always show meaningful data regardless of when the app is run relative to when the CSV data was recorded.

---

## Git Evidence Checklist

Replace each item below with an actual screenshot before submitting.

1. [SCREENSHOT A] — GitHub Commits page filtered by your username (Avinadhmudda15), showing 8-12 commits with descriptive messages like:
   - "feat: custom User model with 3 roles and RBAC"
   - "feat: BFS flood-fill PPI algorithm in parser.py"
   - "feat: patient dashboard with heatmap and Chart.js"
   - "feat: reports module with day-on-day comparison"
   - "fix: timezone anchoring for historical CSV data"

2. [SCREENSHOT B] — One commit opened showing the commit message and the list of changed files (e.g. the parser.py commit showing _ppi() function).

3. [SCREENSHOT C] — Branch graph showing your branch `feature/graphene` or a merged pull request.

4. [SCREENSHOT D] — Terminal output of:
   git log --author="Avinadhmudda15" --oneline -15

---

## Individual Contribution Summary

### Design
- Designed the three-role user model (patient, clinician, admin) and the RBAC access control system including the `can_access_patient_data()` method.
- Designed the full database schema: `UploadSession`, `PressureFrame`, `Alert`, `Comment`, `Metrics` models with appropriate indexes and relationships.
- Designed the BFS flood-fill algorithm for Peak Pressure Index calculation matching the case study specification (min 10 pixels).
- Designed the heuristic risk score formula (0-10) based on peak pressure, alert count, and flagged frame percentage.
- Created wireframes for the patient dashboard, clinician patient detail, and report pages.

### Implementation
- Implemented `accounts/` app: custom User model, PatientProfile, ClinicianProfile, login/logout, admin user CRUD, `@role_required` decorator.
- Implemented `data_processing/` app: CSV parser, BFS PPI algorithm, contact area calculation, alert generation, bulk frame ingestion, plain-English explanation, risk score.
- Implemented `dashboard/` app: patient dashboard, clinician dashboard, admin dashboard, heatmap Canvas renderer, Chart.js time-series charts, all JSON API endpoints.
- Implemented `reports/` app: daily report with day-on-day comparison, same-hour comparison, 7-day trend chart, print support.
- Implemented `analytics/` app: risk score gauge, 7-day breakdown, time-series charts (1h/6h/24h).
- Implemented comment system: patient submission linked to frame, clinician in-thread reply.
- Built `seed_data` management command to auto-ingest all 15 GTLB CSV files and create demo users.
- Fixed timezone-anchoring bug for historical CSV data in charts and risk score.

### Testing
- Manually tested all user roles (patient, clinician, admin) end-to-end — 25 test cases documented in report Section 5.
- Tested CSV ingestion with all 15 GTLB files (5 users x 3 days).
- Tested alert generation at warning (>=500) and critical (>=750) thresholds.
- Tested RBAC: confirmed patients cannot access other patients' data, clinicians cannot access unassigned patients.
- Tested heatmap playback, time-range chart switching, report print function, and comment/reply thread.

---

## Meeting Notes

| Date | Attendees | Decisions Made |
|------|-----------|----------------|
| Week 1 | Team | Agreed on Django as framework, SQLite for dev DB, GitHub for version control. Divided initial tasks: accounts app, data models, CSV parser. |
| Week 3 | Team | Reviewed CSV format from case study. Agreed on BFS flood-fill for PPI. Confirmed alert threshold of 500. Agreed on 5-second frame interval for timestamps. |
| Week 5 | Team | Reviewed dashboard wireframes. Agreed on dark medical theme. Decided to use Chart.js for graphs and HTML5 Canvas for heatmap. |
| Week 8 | Team | Sprint review. Agreed to add plain-English explanation as a nice-to-have. Assigned report module to this sprint. Reviewed comment system design. |
| Week 11 | Team | Final integration testing. Agreed on seed_data command for demo. Reviewed all features against case study requirements. Prepared for presentation. |
