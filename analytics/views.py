from django.core.exceptions import PermissionDenied
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.views import View
from django.db.models import Avg, Max, Count
from datetime import timedelta, datetime, timezone as dt_timezone

from accounts.decorators import role_required
from accounts.models import User
from data_processing.models import PressureFrame, Alert
from data_processing.reporting import patient_metrics_end_date
from data_processing.risk_score import compute_patient_risk


@method_decorator([login_required, role_required('patient','clinician','admin')], name='dispatch')
class AnalyticsView(View):
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
            return render(request, 'analytics/patient_picker.html', {
                'patients': patients, 'page': 'analytics'})
        elif request.user.role == 'admin':
            # Show patient picker for admin with no patient selected
            patients = User.objects.filter(role='patient').order_by('last_name')
            return render(request, 'analytics/patient_picker.html', {
                'patients': patients, 'page': 'analytics'})
        else:
            return redirect('dashboard:home')

        uid = patient.pk
        risk_score, risk_label = compute_patient_risk(uid)

        end_day = patient_metrics_end_date(uid)
        daily = []
        for i in range(6, -1, -1):
            d = end_day - timedelta(days=i)

            start = datetime.combine(d, datetime.min.time()).replace(tzinfo=dt_timezone.utc)
            end   = datetime.combine(d, datetime.max.time()).replace(tzinfo=dt_timezone.utc)

            agg = PressureFrame.objects.filter(
                patient_id=uid, timestamp__range=(start, end)
            ).aggregate(
                frames=Count('id'),
                max_peak=Max('peak_pressure'),
                avg_peak=Avg('peak_pressure'),
                avg_contact=Avg('contact_area_pct'),
            )

            alerts = Alert.objects.filter(
                patient_id=uid, timestamp__range=(start, end)
            ).count()

            daily.append({
                'date':        d.strftime('%d %b'),
                'frames':      agg['frames'] or 0,
                'max_peak':    round(agg['max_peak'] or 0, 1),
                'avg_peak':    round(agg['avg_peak'] or 0, 1),
                'avg_contact': round(agg['avg_contact'] or 0, 1),
                'alerts':      alerts,
            })

        return render(request, 'analytics/analytics.html', {
            'patient':     patient,
            'risk_score':  risk_score,
            'risk_label':  risk_label,
            'daily':       daily,
        })