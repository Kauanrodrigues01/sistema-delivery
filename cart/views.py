from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django.views.decorators.http import require_POST
from django.views.generic import TemplateView, View

from products.models import Product

from .models import Cart, CartItem


# AJAX: aumentar quantidade
@require_POST
def increase_cart_item(request):
    product_id = request.POST.get("product_id")
    cart = get_cart(request)
    item = get_object_or_404(
        CartItem.objects.select_related("product"), cart=cart, product_id=product_id
    )

    # SEGURANÇA: Verificar se produto ainda está ativo
    if not item.product.is_active:
        return JsonResponse({"error": "Produto não está mais disponível"}, status=400)

    item.quantity += 1
    item.save()
    cart_total = cart.total_price
    return JsonResponse(
        {"success": True, "quantity": item.quantity, "cart_total": float(cart_total)}
    )


# AJAX: diminuir quantidade
@require_POST
def decrease_cart_item(request):
    product_id = request.POST.get("product_id")
    cart = get_cart(request)
    item = get_object_or_404(
        CartItem.objects.select_related("product"), cart=cart, product_id=product_id
    )

    # SEGURANÇA: Verificar se produto ainda está ativo (permite remoção mesmo se inativo)
    if not item.product.is_active:
        # Se produto inativo, só permite remoção, não diminuição
        item.delete()
        cart_total = cart.total_price
        return JsonResponse(
            {
                "success": True,
                "quantity": 0,
                "cart_total": float(cart_total),
                "message": "Produto removido (não disponível)",
            }
        )

    if item.quantity > 1:
        item.quantity -= 1
        item.save()
        cart_total = cart.total_price
        return JsonResponse(
            {
                "success": True,
                "quantity": item.quantity,
                "cart_total": float(cart_total),
            }
        )
    else:
        item.delete()
        cart_total = cart.total_price
        return JsonResponse(
            {"success": True, "quantity": 0, "cart_total": float(cart_total)}
        )


# AJAX: remover item
@require_POST
def remove_cart_item(request):
    product_id = request.POST.get("product_id")
    cart = get_cart(request)
    item = get_object_or_404(
        CartItem.objects.select_related("product"), cart=cart, product_id=product_id
    )
    item.delete()
    cart_total = cart.total_price
    return JsonResponse({"success": True, "cart_total": float(cart_total)})


def get_cart(request):
    """
    Pega ou cria um carrinho vinculado à ClientSession.
    Mantém compatibilidade com cart_id na sessão Django.
    """
    from utils.session import get_or_create_client_session

    # Obter ou criar ClientSession
    client_session = get_or_create_client_session(request)

    # Tentar pegar carrinho pela ClientSession
    try:
        cart = Cart.objects.get(client_session=client_session)
    except Cart.DoesNotExist:
        # Se não existe, criar novo carrinho vinculado à sessão
        cart = Cart.objects.create(client_session=client_session)

    return cart


class AddToCartView(View):
    def post(self, request, *args, **kwargs):
        product_id = request.POST.get("product_id")
        # SEGURANÇA: Só permite adicionar produtos ativos
        product = get_object_or_404(Product, pk=product_id, is_active=True)
        cart = get_cart(request)
        item, created = CartItem.objects.get_or_create(cart=cart, product=product)
        if not created:
            item.quantity += 1
            item.save()
        return JsonResponse({"success": True, "cart_count": cart.total_quantity})


class CartDetailView(TemplateView):
    template_name = "cart/cart_detail.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        cart = get_cart(self.request)
        cart_items = cart.items.select_related("product").all()
        total = cart.total_price
        context["cart"] = cart
        context["cart_items"] = cart_items
        context["cart_total"] = total
        return context
