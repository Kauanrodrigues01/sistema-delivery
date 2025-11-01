from django.db import models


class DailyReport(models.Model):
    """
    Modelo para armazenar os dados dos relatórios diários.
    Os PDFs são gerados dinamicamente a partir desses dados.
    """

    # Data do relat�rio
    date = models.DateField(unique=True, db_index=True)

    # M�tricas de pedidos
    quantity_orders = models.IntegerField(default=0)
    quantity_orders_status_completed = models.IntegerField(default=0)
    quantity_orders_status_cancelled = models.IntegerField(default=0)
    quantity_orders_status_pending = models.IntegerField(default=0)
    quantity_orders_late = models.IntegerField(default=0)

    # M�tricas de receita
    revenue_today = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    revenue_pending_today = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)

    # M�tricas de produtos
    quantity_products = models.IntegerField(default=0)
    quantity_products_active = models.IntegerField(default=0)
    quantity_products_inactive = models.IntegerField(default=0)

    # M�tricas calculadas
    ticket_medio = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    taxa_conclusao = models.DecimalField(max_digits=5, decimal_places=2, default=0.00)
    taxa_cancelamento = models.DecimalField(max_digits=5, decimal_places=2, default=0.00)

    # Metadados
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Relat�rio Di�rio"
        verbose_name_plural = "Relat�rios Di�rios"
        ordering = ["-date"]
        indexes = [
            models.Index(fields=["-date"]),
            models.Index(fields=["created_at"]),
        ]

    def __str__(self):
        return f"Relat�rio de {self.date.strftime('%d/%m/%Y')}"

    def get_data_dict(self):
        """
        Retorna os dados do relat�rio em formato de dicion�rio
        para ser usado no template de PDF.
        """
        return {
            "quantity_orders": self.quantity_orders,
            "quantity_orders_status_completed": self.quantity_orders_status_completed,
            "quantity_orders_status_cancelled": self.quantity_orders_status_cancelled,
            "quantity_orders_status_pending": self.quantity_orders_status_pending,
            "quantity_orders_late": self.quantity_orders_late,
            "revenue_today": float(self.revenue_today),
            "revenue_pending_today": float(self.revenue_pending_today),
            "quantity_products": self.quantity_products,
            "quantity_products_active": self.quantity_products_active,
            "quantity_products_inactive": self.quantity_products_inactive,
            "ticket_medio": float(self.ticket_medio),
            "taxa_conclusao": float(self.taxa_conclusao),
            "taxa_cancelamento": float(self.taxa_cancelamento),
        }
