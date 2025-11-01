from datetime import timedelta

from django.contrib.auth.decorators import login_required
from django.db.models import Count, F, FloatField, Q, Sum
from django.db.models.functions import Coalesce
from django.http import HttpResponseForbidden, JsonResponse
from django.utils import timezone

from orders.models import Order
from products.models import Product


@login_required
def get_daily_report(request):
    # Verify is is admin user
    if not request.user.is_staff:
        return HttpResponseForbidden("You are not authorized to view this report.")

    cutoff_time = timezone.now() - timedelta(minutes=25)

    order_stats = Order.objects.today().aggregate(
        total_orders=Count("id"),
        completed_orders=Count("id", filter=Q(status="completed")),
        cancelled_orders=Count("id", filter=Q(status="cancelled")),
        pending_orders=Count("id", filter=Q(status="pending")),
        late_orders=Count("id", filter=Q(status="pending", created_at__lt=cutoff_time)),
        revenue_paid=Coalesce(
            Sum(
                F("items__quantity") * F("items__product__price"),
                filter=Q(payment_status="paid"),
                output_field=FloatField()
            ),
            0.0
        ),
        revenue_pending=Coalesce(
            Sum(
                F("items__quantity") * F("items__product__price"),
                filter=Q(payment_status="pending"),
                output_field=FloatField()
            ),
            0.0
        )
    )

    products_stats = Product.objects.aggregate(
        total_products=Count("id"),
        active_products=Count("id", filter=Q(is_active=True)),
        inactive=Count("id", filter=Q(is_active=False))
    )

    context = {
        "quantity_orders": order_stats["total_orders"],
        "quantity_orders_status_completed": order_stats["completed_orders"],
        "quantity_orders_status_cancelled": order_stats["cancelled_orders"],
        "quantity_orders_status_pending": order_stats["pending_orders"],
        "quantity_orders_late": order_stats["late_orders"],
        "revenue_today": order_stats["revenue_paid"],
        "revenue_pending_today": order_stats["revenue_pending"],
        "quantity_products": products_stats["total_products"],
        "quantity_products_active": products_stats["active_products"],
        "quantity_products_inactive": products_stats["inactive"],
    }

    return JsonResponse(context)
