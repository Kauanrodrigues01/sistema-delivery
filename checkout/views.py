from logging import getLogger

from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import TemplateView

from cart.views import get_cart
from orders.models import Order, OrderItem
from services.mercadopago import MercadoPagoService
from services.notifications import (
    send_order_notifications_with_callmebot,
)

logger = getLogger(__name__)


class CheckoutView(TemplateView):
    template_name = "checkout/checkout.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        cart = get_cart(self.request)
        cart_items = cart.items.select_related("product").all()
        context["cart_items"] = cart_items
        context["cart_total"] = cart.total_price

        # Adicionar dados do cliente se logado
        if self.request.user.is_authenticated and hasattr(
            self.request.user, "customer_profile"
        ):
            customer = self.request.user.customer_profile
            context["customer"] = customer

        return context

    def post(self, request, *args, **kwargs):
        cart = get_cart(request)
        # Uma única consulta otimizada para todos os itens
        cart_items = cart.items.select_related("product").all()

        # Separar itens ativos e inativos em memória (evita query adicional)
        active_items = []
        inactive_items = []

        for item in cart_items:
            if item.product.is_active:
                active_items.append(item)
            else:
                inactive_items.append(item)

        # SEGURANÇA: Verificar se há produtos inativos no carrinho
        if inactive_items:
            context = self.get_context_data()
            context["error_message"] = (
                "Seu carrinho contém produtos que não estão mais disponíveis. Remova-os antes de continuar."
            )
            context["inactive_products"] = [
                item.product.name for item in inactive_items
            ]
            return render(request, "checkout/error.html", context)

        if not active_items:
            context = self.get_context_data()
            context["error_message"] = (
                "Seu carrinho está vazio ou todos os produtos estão indisponíveis."
            )
            return render(request, "checkout/error.html", context)

        # Calcular total usando os itens ativos em memória
        total = sum(item.quantity * item.product.price for item in active_items)
        name = request.POST.get("name")
        phone = request.POST.get("phone")
        cpf = request.POST.get("cpf", "").strip()
        address = request.POST.get("address")
        payment_method = request.POST.get("payment_method")
        cash_value = request.POST.get("cash_value")
        context = self.get_context_data()

        # Validação do troco
        if payment_method == "dinheiro":
            try:
                cash_value = float(cash_value.replace(",", "."))
            except Exception:
                cash_value = 0
            if cash_value < total:
                return render(request, "checkout/error.html", context)

        try:
            # Pega ou cria ClientSession
            from utils.session import get_or_create_client_session

            client_session = get_or_create_client_session(self.request)

            # Cria o pedido vinculado à ClientSession
            order = Order.objects.create(
                customer_name=name,
                phone=phone,
                cpf=cpf if cpf else None,
                address=address,
                payment_method=payment_method,
                cash_value=cash_value if payment_method == "dinheiro" else None,
                payment_status="pending",
                client_session=client_session,
                customer=(
                    self.request.user.customer_profile
                    if (
                        self.request.user.is_authenticated
                        and hasattr(self.request.user, "customer_profile")
                    )
                    else None
                ),
            )
            for item in active_items:
                OrderItem.objects.create(
                    order=order,
                    product=item.product,
                    quantity=item.quantity,
                )

            # Enviar atualização via WebSocket para dashboard
            # NOTA: O cliente NÃO precisa estar conectado ao WebSocket
            # Esta mensagem é enviada para o grupo "orders_updates" onde os ADMINS
            # do dashboard estão conectados e receberão a notificação em tempo real
            try:
                channel_layer = get_channel_layer()
                async_to_sync(channel_layer.group_send)(
                    "orders_updates",
                    {
                        "type": "new_order",
                        "data": {
                            "order_id": order.id,
                            "customer_name": order.customer_name,
                            "status": order.status,
                            "payment_status": order.payment_status,
                            "total": float(order.total_price),
                        },
                    },
                )
            except Exception as e:
                logger.error(f"Erro ao enviar atualização via WebSocket: {e}")

            # Envia notificação de novo pedido para todos os métodos de pagamento
            def send_notification(order):
                try:
                    send_order_notifications_with_callmebot(order)
                except Exception as e:
                    logger.error(f"Erro ao enviar notificação de novo pedido: {e}")
                    return render(request, "checkout/error.html", context)

            # Se o pagamento for PIX, cria o pagamento e redireciona
            if payment_method == "pix":
                try:
                    payment_data = create_payment_charge(order)
                    # Salva o ID do pagamento no pedido para rastreamento
                    order.payment_id = payment_data.get("id")
                    order.payment_url = (
                        payment_data.get("point_of_interaction", {})
                        .get("transaction_data", {})
                        .get("ticket_url")
                    )
                    order.save()

                    # Limpa o carrinho e redireciona para página de aguardar pagamento
                    cart.items.all().delete()
                    return redirect("checkout:awaiting_payment", order_id=order.id)
                except Exception as e:
                    # Se falhar integração com MercadoPago, continua com pagamento manual
                    logger.error(
                        f"Erro ao criar pagamento PIX (fallback para manual): {e}"
                    )

                    # Marca que a integração falhou
                    order.payment_integration_failed = True
                    order.save()

                    # Atualiza contexto para informar que será pagamento manual
                    context["payment_fallback"] = True
                    context["fallback_message"] = (
                        "Não foi possível gerar o QR Code PIX automaticamente. "
                        "Entre em contato conosco para receber os dados de pagamento."
                    )

                    # Limpa o carrinho e mostra página de sucesso com aviso
                    cart.items.all().delete()
                    return render(request, "checkout/success.html", context)
                finally:
                    send_notification(order)

            if payment_method == "cartao_online":
                try:
                    preference_data = create_payment_charge(order)
                    # Salva a URL de pagamento no pedido, pagamento por preferência não gera ID de pagamento imediato, só depois do pagamento no webhook
                    order.payment_id = None
                    order.payment_url = preference_data.get("init_point")
                    order.save()

                    # Limpa o carrinho e redireciona para página de aguardar pagamento
                    cart.items.all().delete()
                    return redirect("checkout:awaiting_payment", order_id=order.id)
                except Exception as e:
                    # Se falhar integração com MercadoPago, converte para pagamento presencial
                    logger.error(
                        f"Erro ao criar pagamento com cartão online (fallback para presencial): {e}"
                    )

                    # Converte para cartão presencial e marca que a integração falhou
                    order.payment_method = "cartao_presencial"
                    order.payment_integration_failed = True
                    order.save()

                    # Atualiza contexto para informar que será pagamento presencial
                    context["payment_fallback"] = True
                    context["fallback_message"] = (
                        "Não foi possível processar o pagamento online. "
                        "O pagamento será realizado presencialmente na entrega."
                    )

                    # Limpa o carrinho e mostra página de sucesso com aviso
                    cart.items.all().delete()
                    return render(request, "checkout/success.html", context)
                finally:
                    send_notification(order)

            if payment_method == "cartao_presencial":
                try:
                    # Pagamento presencial não precisa de processamento online
                    # Limpa o carrinho e redireciona para sucesso
                    cart.items.all().delete()
                    return render(request, "checkout/success.html", context)
                except Exception as e:
                    order.delete()
                    logger.error(
                        f"Erro ao processar pagamento com cartão presencial: {e}"
                    )
                    context["error_message"] = (
                        "Erro ao finalizar pedido. Tente novamente."
                    )
                    return render(request, "checkout/error.html", context)
                finally:
                    send_notification(order)

            if payment_method == "dinheiro":
                try:
                    # Limpa o carrinho
                    cart.items.all().delete()
                    return render(request, "checkout/success.html", context)
                except Exception as e:
                    order.delete()
                    logger.error(f"Erro ao processar pagamento em dinheiro: {e}")
                    context["error_message"] = (
                        "Erro ao finalizar pedido. Tente novamente."
                    )
                    return render(request, "checkout/error.html", context)
                finally:
                    send_notification(order)

            # Fallback para outros métodos de pagamento
            cart.items.all().delete()
            context = self.get_context_data()
            send_notification(order)
            return render(request, "checkout/success.html", context)

        except Exception as e:
            logger.error(f"Error processing order: {e}")
            return render(request, "checkout/error.html", context)


def create_payment_charge(order: Order) -> dict:
    """
    Função para criar uma cobrança de pagamento via MercadoPago.
    """

    mp_service = MercadoPagoService()

    if order.payment_method == "pix":
        payment_data = mp_service.pay_with_pix(
            amount=float(order.total_price),
            payer_email="cliente@exemplo.com",
            payer_cpf=order.cpf if order.cpf else "00000000000",
            description=f"Pedido #{order.id} - {order.customer_name}",
        )
        return payment_data

    elif order.payment_method == "cartao_online":
        # Criar lista de itens para a preferência
        items = []
        for item in order.items.all():
            items.append(
                {
                    "id": str(item.product.id),
                    "title": item.product.name,
                    "quantity": item.quantity,
                    "currency_id": "BRL",
                    "unit_price": float(item.product.price),
                }
            )

        # Usar o método adequado do serviço MercadoPago
        preference_data = mp_service.create_preference_with_card(
            items, order_id=str(order.id)
        )
        return preference_data

    return {}


class AwaitingPaymentView(TemplateView):
    """View para página de aguardando pagamento (PIX e Cartão)"""

    template_name = "checkout/awaiting_payment.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        order_id = kwargs.get("order_id")
        order = get_object_or_404(Order, id=order_id)

        # Busca informações do pagamento se existir
        payment_info = None
        ticket_url = order.payment_url

        context.update(
            {
                "order": order,
                "payment_info": payment_info,
                "ticket_url": ticket_url,
            }
        )
        return context


def get_payment_info(payment_id: str) -> dict:
    """
    Função para buscar informações de um pagamento
    """
    mp_service = MercadoPagoService()
    return mp_service.get_payment_info(payment_id)


@csrf_exempt
def check_payment_status(request, order_id):
    """
    API endpoint para verificar status do pagamento via AJAX (PIX e Cartão)
    """
    if request.method == "GET":
        try:
            order = get_object_or_404(Order, id=order_id)

            if not order.payment_id:
                return JsonResponse(
                    {
                        "status": "error",
                        "message": "Pagamento não encontrado, caso seja cartão, verifique se o pagamento foi efetuado",
                    }
                )

            payment_info = get_payment_info(order.payment_id)

            return JsonResponse(
                {
                    "status": "success",
                    "payment_status": payment_info.get("status"),
                    "payment_detail": payment_info.get("status_detail"),
                    "ticket_url": payment_info.get("point_of_interaction", {})
                    .get("transaction_data", {})
                    .get("ticket_url"),
                    "qr_code": payment_info.get("point_of_interaction", {})
                    .get("transaction_data", {})
                    .get("qr_code"),
                    "order_paid": order.payment_status == "paid",
                }
            )

        except Exception as e:
            logger.error(f"Erro ao verificar status do pagamento: {e}")
            return JsonResponse({"status": "error", "message": str(e)})

    return JsonResponse({"status": "error", "message": "Método não permitido"})


class SuccessPaymentView(TemplateView):
    """View para página de pagamento bem-sucedido"""

    template_name = "checkout/success_payment.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        order_id = kwargs.get("order_id")
        order = get_object_or_404(Order, id=order_id)

        context.update(
            {"order": order, "success_message": "Pagamento realizado com sucesso!"}
        )
        return context


class ErrorPaymentView(TemplateView):
    """View para página de erro no pagamento"""

    template_name = "checkout/error_payment.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        order_id = kwargs.get("order_id")

        # Se o order_id for fornecido, busca o pedido
        if order_id:
            try:
                order = get_object_or_404(Order, id=order_id)
                context["order"] = order
            except Exception:
                pass

        # Pega a mensagem de erro da URL se existir
        error_message = self.request.GET.get(
            "message", "Ocorreu um erro no processamento do pagamento."
        )
        context["error_message"] = error_message

        return context
