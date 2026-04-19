from django.core.exceptions import PermissionDenied
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.views import View
from django.db.models import Avg, Max, Count, Q
from django.utils import timezone
from datetime import datetime, time as dtime, timezone as dt_timezone, timedelta, date

from accounts.decorators import role_required
from accounts.models import User
from data_processing.models import PressureFrame, Alert
from data_processing.reporting import patient_metrics_end_date


def _day_summary(uid, day):
    # ✅ FIXED (no timezone.make_aware needed)
    start = datetime.combine(day, datetime.min.time()).replace(tzinfo=dt_timezone.utc)
    end   = datetime.combine(day, datetime.max.time()).replace(tzinfo=dt_timezone.utc)

    agg = PressureFrame.objects.filter(
        patient_id=uid, timestamp__range=(start, end)
    ).aggregate(
        frames=Count('id'),
        max_peak=Max('peak_pressure'),
        avg_peak=Avg('peak_pressure'),
        avg_contact=Avg('contact_area_pct'),
        flagged=Count('id', filter=Q(is_flagged=True)),
    )

    alerts = Alert.objects.filter(
        patient_id=uid, timestamp__range=(start, end)
    ).count()

    return {
        'frames':      agg['frames'] or 0,
        'max_peak':    round(agg['max_peak'] or 0, 1),
        'avg_peak':    round(agg['avg_peak'] or 0, 1),
        'avg_contact': round(agg['avg_contact'] or 0, 1),
        'flagged':     agg['flagged'] or 0,
        'alerts':      alerts,
    }


def _pct_change(new, old):
    if not old:
        return None
    return round((new - old) / old * 100, 1)


def _hour_window_local(d, hour):
    """Start/end aware datetimes for one local clock hour on calendar day d."""
    start = timezone.make_aware(datetime.combine(d, dtime(hour, 0, 0)))
    return start, start + timedelta(hours=1)


def _hour_summary(uid, day, hour):
    start, end = _hour_window_local(day, hour)
    agg = PressureFrame.objects.filter(
        patient_id=uid, timestamp__gte=start, timestamp__lt=end
    ).aggregate(
        frames=Count('id'),
        max_peak=Max('peak_pressure'),
        avg_peak=Avg('peak_pressure'),
        avg_contact=Avg('contact_area_pct'),
    )
    alerts = Alert.objects.filter(
        patient_id=uid, timestamp__gte=start, timestamp__lt=end
    ).count()
    return {
        'frames':      agg['frames'] or 0,
        'max_peak':    round(agg['max_peak'] or 0, 1),
        'avg_peak':    round(agg['avg_peak'] or 0, 1),
        'avg_contact': round(agg['avg_contact'] or 0, 1),
        'alerts':      alerts,
    }


@method_decorator([login_required, role_required('patient','clinician','admin')], name='dispatch')
class ReportView(View):
    def get(self, request, patient_pk=None):
        if patient_pk:
            patient = get_object_or_404(User, pk=patient_pk, role='patient')
            if not request.user.can_access_patient_data(patient):
                raise PermissionDenied()
        elif request.user.role == 'patient':
            patient = request.user
        elif request.user.role == 'clinician':
            # Show patient picker for clinician with no patient selected
            profile = getattr(request.user, 'clinician_profile', None)
            if profile and profile.can_view_all_patients:
                patients = User.objects.filter(role='patient').order_by('last_name')
            else:
                patients = User.objects.filter(
                    patient_profile__clinician=request.user).order_by('last_name')
            return render(request, 'reports/patient_picker.html', {
                'patients': patients, 'page': 'reports'})
        elif request.user.role == 'admin':
            # Show patient picker for admin with no patient selected
            patients = User.objects.filter(role='patient').order_by('last_name')
            return render(request, 'reports/patient_picker.html', {
                'patients': patients, 'page': 'reports'})
        else:
            return redirect('dashboard:home')

        uid = patient.pk
        generated_date = date.today()
        primary = patient_metrics_end_date(uid)
        prev = primary - timedelta(days=1)

        primary_data = _day_summary(uid, primary)
        prev_data = _day_summary(uid, prev)

        comparison = {
            'peak':    _pct_change(primary_data['max_peak'], prev_data['max_peak']),
            'contact': _pct_change(primary_data['avg_contact'], prev_data['avg_contact']),
            'alerts':  _pct_change(primary_data['alerts'], prev_data['alerts']),
        }

        hour_compare = None
        latest_frame = (
            PressureFrame.objects.filter(patient_id=uid).order_by('-timestamp').first()
        )
        if latest_frame:
            loc = timezone.localtime(latest_frame.timestamp)
            ch = loc.hour
            hour_today = _hour_summary(uid, primary, ch)
            hour_yesterday = _hour_summary(uid, prev, ch)
            hour_compare = {
                'hour_label': loc.strftime('%H:00'),
                'today': hour_today,
                'yesterday': hour_yesterday,
                'peak_delta': _pct_change(
                    hour_today['max_peak'], hour_yesterday['max_peak']),
                'contact_delta': _pct_change(
                    hour_today['avg_contact'], hour_yesterday['avg_contact']),
            }

        weekly = []
        for i in range(6, -1, -1):
            d = primary - timedelta(days=i)
            s = _day_summary(uid, d)
            weekly.append({'date': d.strftime('%d %b'), **s})

        recent_alerts = Alert.objects.filter(
            patient_id=uid
        ).order_by('-created_at')[:20]

        return render(request, 'reports/report.html', {
            'patient':          patient,
            'generated_date':   generated_date,
            'report_primary':   primary,
            'report_prev':      prev,
            'is_primary_today': primary == generated_date,
            'primary_data':     primary_data,
            'prev_data':        prev_data,
            'comparison':       comparison,
            'hour_compare':     hour_compare,
            'weekly':           weekly,
            'recent_alerts':    recent_alerts,
        })