"""Shared date logic for analytics and reports."""
from datetime import date, timedelta

from django.db.models import Max
from django.utils import timezone

from .models import PressureFrame


def chart_metrics_window(patient_id, hours):
    """
    (start, end) datetimes for time-series charts.
    Uses the last wall-clock window; if empty (e.g. historical CSVs), anchors end
    to the latest stored frame so demo data still plots.
    """
    end = timezone.now()
    start = end - timedelta(hours=hours)
    if PressureFrame.objects.filter(
        patient_id=patient_id, timestamp__gte=start, timestamp__lte=end
    ).exists():
        return start, end
    latest = (
        PressureFrame.objects.filter(patient_id=patient_id)
        .order_by('-timestamp')
        .values_list('timestamp', flat=True)
        .first()
    )
    if latest is not None:
        end = latest
        start = end - timedelta(hours=hours)
    return start, end


def patient_latest_frame_date(patient_id):
    """Calendar date (in TIME_ZONE) of the newest frame, or None."""
    latest = PressureFrame.objects.filter(patient_id=patient_id).aggregate(
        m=Max('timestamp')
    )['m']
    if latest is None:
        return None
    return timezone.localdate(latest)


def patient_metrics_end_date(patient_id):
    """Last day that has sensor data, or today if there are no frames yet."""
    d = patient_latest_frame_date(patient_id)
    return d if d is not None else date.today()
