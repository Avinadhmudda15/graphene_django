from django.conf import settings


def site_branding(request):
    """Expose friendly site name to all templates (browser tab + UI)."""
    return {
        'SITE_NAME': getattr(settings, 'SITE_NAME', 'Sensore'),
        'SITE_TITLE': getattr(settings, 'SITE_TITLE', 'Sensore — Graphene Trace'),
    }
