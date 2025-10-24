import logging

from django.conf import settings

logger = logging.getLogger(__name__)


def global_context(request):
    """
    Context processor that adds global company information to all templates
    """
    # Get cart count for the current session (lazy import to avoid circular dependency issues)
    cart_count = 0
    try:
        # Only import and query if apps are ready
        from django.apps import apps

        if apps.ready:
            
            from cart.views import get_cart

            cart = get_cart(request)
            cart_count = cart.total_quantity if cart else 0
    except Exception as e:
        logger.error(f"Error getting cart count: {e}")
        # If any error occurs (apps not ready, etc), default to 0
        cart_count = 0

    return {
        "global_info": {
            "company_name": settings.COMPANY_NAME,
            "company_address": settings.COMPANY_ADDRESS,
            "company_contacts": settings.COMPANY_CONTACTS,
            "company_logo_url": settings.COMPANY_LOGO_URL,
            "header_color_start": settings.HEADER_COLOR_START,
            "header_color_end": settings.HEADER_COLOR_END,
        },
        "cart_count": cart_count,
    }
