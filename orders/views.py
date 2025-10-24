from django.contrib import messages
from django.http import Http404, JsonResponse
from django.shortcuts import get_object_or_404, render
from django.views.decorators.http import require_POST

from orders.models import Order
from utils.session import get_or_create_client_session


def order_list(request):
    """Lista todos os pedidos da sessão atual do cliente"""
    client_session = get_or_create_client_session(request)
    orders = Order.objects.filter(client_session=client_session).order_by("-created_at")

    context = {
        "orders": orders,
    }
    return render(request, "orders/order_list.html", context)


def order_detail(request, order_id):
    """Exibe os detalhes de um pedido específico"""
    client_session = get_or_create_client_session(request)

    # Buscar o pedido e verificar se pertence à sessão atual
    order = get_object_or_404(Order, id=order_id)

    # Verificar se o pedido pertence à sessão atual
    if order.client_session != client_session:
        raise Http404("Pedido não encontrado.")

    context = {
        "order": order,
    }
    return render(request, "orders/order_detail.html", context)


@require_POST
def cancel_order(request, order_id):
    """Cancela um pedido se ambos os status forem pendentes"""
    client_session = get_or_create_client_session(request)

    # Buscar o pedido e verificar se pertence à sessão atual
    order = get_object_or_404(Order, id=order_id)

    # Verificar se o pedido pertence à sessão atual
    if order.client_session != client_session:
        return JsonResponse(
            {"success": False, "error": "Pedido não encontrado."}, status=404
        )

    # Verificar se ambos os status são pendentes
    if order.status == "pending" and order.payment_status == "pending":
        order.status = "cancelled"
        order.payment_status = "cancelled"
        order.save()

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
