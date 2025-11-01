from datetime import timedelta
from typing import TypedDict

from django.db.models import Count, F, FloatField, Q, Sum
from django.db.models.functions import Coalesce
from django.utils import timezone

from orders.models import Order
from products.models import Product


class DailyReportData(TypedDict):
    """Estrutura tipada para os dados do relatório diário."""

    # Métricas de pedidos
    quantity_orders: int
    quantity_orders_status_completed: int
    quantity_orders_status_cancelled: int
    quantity_orders_status_pending: int
    quantity_orders_late: int

    # Métricas de receita
    revenue_today: float
    revenue_pending_today: float

    # Métricas de produtos
    quantity_products: int
    quantity_products_active: int
    quantity_products_inactive: int

    # Métricas calculadas
    ticket_medio: float
    taxa_conclusao: float
    taxa_cancelamento: float


def calculate_daily_report_data() -> DailyReportData:
    """
    Calcula todos os dados do relatório diário.

    Returns:
        DailyReportData: Dicionário tipado com todas as métricas do relatório.
    """
    cutoff_time = timezone.now() - timedelta(minutes=25)

    # Buscar dados dos pedidos do dia
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
                output_field=FloatField(),
            ),
            0.0,
        ),
        revenue_pending=Coalesce(
            Sum(
                F("items__quantity") * F("items__product__price"),
                filter=Q(payment_status="pending"),
                output_field=FloatField(),
            ),
            0.0,
        ),
    )

    # Buscar dados dos produtos
    products_stats = Product.objects.aggregate(
        total_products=Count("id"),
        active_products=Count("id", filter=Q(is_active=True)),
        inactive=Count("id", filter=Q(is_active=False)),
    )

    # Calcular métricas adicionais
    ticket_medio = 0.0
    if order_stats["completed_orders"] > 0:
        ticket_medio = order_stats["revenue_paid"] / order_stats["completed_orders"]

    taxa_conclusao = 0.0
    taxa_cancelamento = 0.0
    if order_stats["total_orders"] > 0:
        taxa_conclusao = (order_stats["completed_orders"] / order_stats["total_orders"]) * 100
        taxa_cancelamento = (order_stats["cancelled_orders"] / order_stats["total_orders"]) * 100

    # Retornar dados tipados
    return DailyReportData(
        quantity_orders=order_stats["total_orders"],
        quantity_orders_status_completed=order_stats["completed_orders"],
        quantity_orders_status_cancelled=order_stats["cancelled_orders"],
        quantity_orders_status_pending=order_stats["pending_orders"],
        quantity_orders_late=order_stats["late_orders"],
        revenue_today=order_stats["revenue_paid"],
        revenue_pending_today=order_stats["revenue_pending"],
        quantity_products=products_stats["total_products"],
        quantity_products_active=products_stats["active_products"],
        quantity_products_inactive=products_stats["inactive"],
        ticket_medio=ticket_medio,
        taxa_conclusao=taxa_conclusao,
        taxa_cancelamento=taxa_cancelamento,
    )
