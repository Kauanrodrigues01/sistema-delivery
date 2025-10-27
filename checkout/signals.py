from logging import getLogger

from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
from django.db.models.signals import post_delete, post_save
from django.dispatch import receiver

from orders.models import Order, OrderItem

logger = getLogger(__name__)


def send_order_update(order, event_type):
    """
    Função helper para enviar atualizações via WebSocket
    """
    try:
        channel_layer = get_channel_layer()

        # Se não há channel layer configurado, apenas ignore
        if not channel_layer:
            return

        # Preparar dados do pedido
        order_data = {
            "order_id": order.id,
            "customer_name": order.customer_name,
            "phone": order.phone,
            "status": order.status,
            "payment_status": order.payment_status,
            "payment_method": order.payment_method,
            "total_price": float(order.total_price),
            "created_at": order.created_at.isoformat(),
            "is_late": order.is_late,
        }

        # Incluir itens do pedido
        order_data["items"] = []
        for item in order.items.select_related("product").all():
            order_data["items"].append(
                {
                    "product_name": item.product.name,
                    "quantity": item.quantity,
                    "price": float(item.product.price),
                }
            )

        # Enviar mensagem para o grupo
        async_to_sync(channel_layer.group_send)(
            "orders_updates", {"type": event_type, "data": order_data}
        )

    except Exception:
        # Falhas do WebSocket não devem impedir operações normais
        pass


@receiver(post_save, sender=Order)
def order_saved(sender, instance, created, **kwargs):
    """
    Signal chamado quando um pedido é criado ou atualizado
    """
    try:
        if created:
            logger.info(f"SIGNALS DE ORDER CREATED: {instance.id}")
            # Novo pedido criado
            send_order_update(instance, "new_order")
    except Exception:
        # Não pode falhar o signal - isso impediria o save do webhook
        pass


@receiver(post_save, sender=OrderItem)
def order_item_saved(sender, instance, created, **kwargs):
    """
    Signal chamado quando um item do pedido é criado ou atualizado
    """
    try:
        if created:
            # Verificar se o pedido foi criado há menos de 2 segundos
            # Se sim, não enviar notificação de item adicionado (já foi enviada a de novo pedido)
            from django.utils import timezone

            time_diff = (timezone.now() - instance.order.created_at).total_seconds()

            # Se o pedido tem mais de 2 segundos, significa que o item foi adicionado depois
            if time_diff > 2:
                # Novo item adicionado ao pedido existente
                send_order_update(instance.order, "order_item_added")
            # Se o pedido é novo (< 2 segundos), não enviar nada pois já foi enviado "new_order"
        else:
            # Item existente atualizado
            send_order_update(instance.order, "order_update")
    except Exception:
        # Não pode falhar o signal
        pass


@receiver(post_delete, sender=OrderItem)
def order_item_deleted(sender, instance, **kwargs):
    """
    Signal chamado quando um item do pedido é deletado
    """
    try:
        # Item removido do pedido
        send_order_update(instance.order, "order_item_removed")
    except Exception:
        # Não pode falhar o signal
        pass
