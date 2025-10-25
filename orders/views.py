from django.contrib import messages
from django.db.models import Q
from django.http import Http404, JsonResponse
from django.shortcuts import get_object_or_404, render
from django.views.decorators.http import require_POST

from orders.models import Order
from utils.session import get_or_create_client_session


def order_list(request):
    """Lista todos os pedidos da sessão atual do cliente e do customer logado"""
    client_session = get_or_create_client_session(request)

    # Buscar pedidos da sessão
    orders_query = Q(client_session=client_session)

    # Se o usuário estiver logado e tiver um customer_profile, incluir pedidos do customer
    if request.user.is_authenticated and hasattr(request.user, "customer_profile"):
        orders_query |= Q(customer=request.user.customer_profile)

    orders = Order.objects.filter(orders_query).distinct().order_by("-created_at")

    context = {
        "orders": orders,
    }
    return render(request, "orders/order_list.html", context)


def order_detail(request, order_id):
    """Exibe os detalhes de um pedido específico"""
    client_session = get_or_create_client_session(request)

    # Buscar o pedido
    order = get_object_or_404(Order, id=order_id)

    # Verificar se o pedido pertence à sessão atual OU ao customer logado
    has_access = order.client_session == client_session
    if request.user.is_authenticated and hasattr(request.user, "customer_profile"):
        has_access = has_access or order.customer == request.user.customer_profile

    if not has_access:
        raise Http404("Pedido não encontrado.")

    context = {
        "order": order,
    }
    return render(request, "orders/order_detail.html", context)


@require_POST
def cancel_order(request, order_id):
    """Cancela um pedido se ambos os status forem pendentes"""
    from logging import getLogger

    from asgiref.sync import async_to_sync
    from channels.layers import get_channel_layer

    from services.notifications import send_order_cancellation_notification

    logger = getLogger(__name__)

    client_session = get_or_create_client_session(request)

    # Buscar o pedido
    order = get_object_or_404(Order, id=order_id)

    # Verificar se o pedido pertence à sessão atual OU ao customer logado
    has_access = order.client_session == client_session
    if request.user.is_authenticated and hasattr(request.user, "customer_profile"):
        has_access = has_access or order.customer == request.user.customer_profile

    if not has_access:
        return JsonResponse(
            {"success": False, "error": "Pedido não encontrado."}, status=404
        )

    # Verificar se ambos os status são pendentes
    if order.status == "pending" and order.payment_status == "pending":
        order.status = "cancelled"
        order.payment_status = "cancelled"
        order.save()

        # Enviar notificação de cancelamento
        try:
            send_order_cancellation_notification(order)
        except Exception as e:
            logger.error(f"Erro ao enviar notificação de cancelamento: {e}")

        # Atualizar dashboard via WebSocket
        try:
            channel_layer = get_channel_layer()
            async_to_sync(channel_layer.group_send)(
                "orders_updates",
                {
                    "type": "order_update",
                    "data": {
                        "order_id": order.id,
                        "status": order.status,
                        "payment_status": order.payment_status,
                        "customer_name": getattr(order, "customer_name", None),
                    },
                },
            )
        except Exception as e:
            logger.error(f"Erro ao enviar atualização via WebSocket: {e}")

        messages.success(request, "Pedido cancelado com sucesso!")
        return JsonResponse({"success": True})
    else:
        return JsonResponse(
            {
                "success": False,
                "error": "Não é possível cancelar este pedido. Apenas pedidos com status pendente podem ser cancelados.",
            },
            status=400,
        )
