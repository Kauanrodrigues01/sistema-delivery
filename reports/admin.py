from django.contrib import admin

from .models import DailyReport


@admin.register(DailyReport)
class DailyReportAdmin(admin.ModelAdmin):
    list_display = [
        "date",
        "quantity_orders",
        "quantity_orders_status_completed",
        "revenue_today",
        "ticket_medio",
        "created_at",
    ]
    list_filter = ["date", "created_at"]
    search_fields = ["date"]
    readonly_fields = [
        "created_at",
        "updated_at",
    ]
    ordering = ["-date"]
    date_hierarchy = "date"

    fieldsets = (
        (
            "Informações Gerais",
            {
                "fields": ("date", "created_at", "updated_at"),
            },
        ),
        (
            "Métricas de Pedidos",
            {
                "fields": (
                    "quantity_orders",
                    "quantity_orders_status_completed",
                    "quantity_orders_status_cancelled",
                    "quantity_orders_status_pending",
                    "quantity_orders_late",
                ),
            },
        ),
        (
            "Métricas de Receita",
            {
                "fields": (
                    "revenue_today",
                    "revenue_pending_today",
                    "ticket_medio",
                ),
            },
        ),
        (
            "Métricas de Produtos",
            {
                "fields": (
                    "quantity_products",
                    "quantity_products_active",
                    "quantity_products_inactive",
                ),
            },
        ),
        (
            "Taxas Calculadas",
            {
                "fields": (
                    "taxa_conclusao",
                    "taxa_cancelamento",
                ),
            },
        ),
    )
