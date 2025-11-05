from typing import Tuple
from django.conf import settings
from .models import SiteSetting


def get_stripe_keys() -> Tuple[str, str]:
    api_key = getattr(settings, 'STRIPE_API_KEY', '') or ''
    webhook_secret = getattr(settings, 'STRIPE_WEBHOOK_SECRET', '') or ''
    try:
        s = SiteSetting.objects.filter(is_active=True).first()
        if s:
            api_key = s.stripe_api_key or api_key
            webhook_secret = s.stripe_webhook_secret or webhook_secret
    except Exception:
        # DB may not be migrated yet
        pass
    return api_key, webhook_secret


