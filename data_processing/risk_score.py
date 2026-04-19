"""24h rolling risk score from pressure frames and alerts (shared by dashboard + analytics)."""
from datetime import timedelta

from django.db.models import Avg, Max
from django.utils import timezone

from .models import PressureFrame, Alert


def compute_patient_risk(patient_id):
    """
    Returns (score 0–10, short label).
    If no recent data in wall-clock window, uses the latest recorded frame as window end
    (matches historical CSV demo data).
    """
    now = timezone.now()
    start = now - timedelta(hours=24)
    frames = PressureFrame.objects.filter(patient_id=patient_id, timestamp__gte=start)
    if not frames.exists():
        latest = (
            PressureFrame.objects.filter(patient_id=patient_id)
            .order_by('-timestamp')
            .first()
        )
        if latest:
            end = latest.timestamp
            start = end - timedelta(hours=24)
            frames = PressureFrame.objects.filter(
                patient_id=patient_id,
                timestamp__gte=start,
                timestamp__lte=end,
            )
    if not frames.exists():
        return 0, 'No recent data.'

    agg = frames.aggregate(
        avg_peak=Avg('peak_pressure'),
        max_peak=Max('peak_pressure'),
        end_ts=Max('timestamp'),
    )
    end_ts = agg['end_ts']
    alert_count = Alert.objects.filter(
        patient_id=patient_id,
        timestamp__gte=start,
        timestamp__lte=end_ts,
    ).count()
    flagged = frames.filter(is_flagged=True).count()
    total = frames.count()
    flag_pct = (flagged / total * 100) if total else 0

    score = 0
    if agg['avg_peak'] > 800:
        score += 3
    elif agg['avg_peak'] > 400:
        score += 1
    if agg['max_peak'] > 1500:
        score += 3
    elif agg['max_peak'] > 700:
        score += 1
    if alert_count > 10:
        score += 2
    elif alert_count > 3:
        score += 1
    if flag_pct > 20:
        score += 2
    elif flag_pct > 5:
        score += 1

    score = min(score, 10)
    if score >= 7:
        label = 'High risk — contact clinician immediately.'
    elif score >= 4:
        label = 'Moderate risk — monitor closely and reposition regularly.'
    else:
        label = 'Low risk — pressure levels look acceptable.'
    return score, label
