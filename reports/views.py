from datetime import timedelta

from django.contrib.auth.decorators import login_required
from django.db.models import Sum
from django.http import HttpResponseForbidden, JsonResponse
from django.utils import timezone

from orders.models import Order
from products.models import Product


@login_required
def get_daily_report(request):
    # Verify is is admin user
    if not request.user.is_staff:
        return HttpResponseForbidden("You are not authorized to view this report.")

    today = timezone.now()
    orders_today = Order.objects.filter(created_at=today)
    quantity_orders = orders_today.count()
    quantity_orders_status_completed = orders_today.filter(status="completed").count()
    quantity_orders_status_cancelled = orders_today.filter(status="cancelled").count()
    quantity_orders_status_pending = orders_today.filter(status="pending").count()

    cutoff_time = timezone.now() - timedelta(minutes=25)
    quantity_orders_late = orders_today.filter(
        status="pending",
        created_at__lt=cutoff_time
    ).count()

    # revenue_today = (
    #     orders_today.filter(payment_status="paid").aggregate(
    #         total_revenue=Sum("total_price")
    #     )["total_revenue"]
    #     or 0
    # )
    # revenue_pending_today = (
    #     orders_today.filter(payment_status="pending").aggregate(
    #         total_revenue=Sum("total_price")
    #     )["total_revenue"]
    #     or 0
    # )

    products_today = Product.objects.filter(created_at=today)
    quantity_products = products_today.count()
    quantity_products_active = products_today.filter(is_active=True).count()
    quantity_products_inactive = products_today.filter(is_active=False).count()

    context = {
        "quantity_orders": quantity_orders,
        "quantity_orders_status_completed": quantity_orders_status_completed,
        "quantity_orders_status_cancelled": quantity_orders_status_cancelled,
        "quantity_orders_status_pending": quantity_orders_status_pending,
        "quantity_orders_late": quantity_orders_late,
        # "revenue_today": revenue_today,
        # "revenue_pending_today": revenue_pending_today,
        "quantity_products": quantity_products,
        "quantity_products_active": quantity_products_active,
        "quantity_products_inactive": quantity_products_inactive,
    }

    return JsonResponse(context)
