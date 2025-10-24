from django.db import models


class ClientSession(models.Model):
    """
    Representa uma sessão de cliente para rastrear carrinho e pedidos
    mesmo entre diferentes dispositivos e após expiração da sessão Django
    """

    session_key = models.CharField(
        max_length=40, unique=True, db_index=True, help_text="Chave da sessão Django"
    )
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    last_activity = models.DateTimeField(auto_now=True, db_index=True)
    user_agent = models.TextField(blank=True, help_text="User agent do navegador")
    ip_address = models.GenericIPAddressField(
        null=True, blank=True, help_text="IP do cliente"
    )

    class Meta:
        verbose_name = "Sessão de Cliente"
        verbose_name_plural = "Sessões de Clientes"
        ordering = ["-last_activity"]

    def __str__(self):
        return f"Session {self.session_key[:8]}... - {self.created_at.strftime('%d/%m/%Y %H:%M')}"

    @property
    def total_orders(self):
        """Total de pedidos desta sessão"""
        return self.orders.count()

    @property
    def total_spent(self):
        """Total gasto em pedidos finalizados"""
        from decimal import Decimal

        total = self.orders.filter(status="completed", payment_status="paid").aggregate(
            total=models.Sum(
                models.F("items__quantity") * models.F("items__product__price")
            )
        )["total"]
        return Decimal(str(total)) if total else Decimal("0.00")

    @property
    def has_active_cart(self):
        """Verifica se tem carrinho com itens"""
        return hasattr(self, "cart") and self.cart.items.exists()
