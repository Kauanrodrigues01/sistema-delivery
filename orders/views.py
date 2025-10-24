from django.http import Http404
from django.shortcuts import get_object_or_404, render

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
