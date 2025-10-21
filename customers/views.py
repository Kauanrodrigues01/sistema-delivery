from logging import getLogger

from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render

from customers.models import Customer

logger = getLogger(__name__)


def customer_login_view(request):
    """
    View de login específico para clientes (não superusers)

    Permite que clientes fiéis façam login para ter vantagens no checkout.
    Bloqueia acesso de superusers (que devem usar /dashboard/login/).
    Aceita login com username ou CPF.
    """
    # Se já está logado, redirecionar
    if request.user.is_authenticated:
        if request.user.is_superuser:
            return redirect("dashboard:dashboard")
        return redirect("product_list")

    if request.method == "POST":
        username_or_cpf = request.POST.get("username-cpf")
        password = request.POST.get("password")

        # Primeiro, tentar autenticar com username
        user = authenticate(request, username=username_or_cpf, password=password)

        # Se não funcionou, tentar buscar por CPF
        if user is None and username_or_cpf:
            logger.debug("Tentando autenticar por CPF")
            # Remover formatação do CPF (pontos e traços)
            cpf_cleaned = username_or_cpf.replace(".", "").replace("-", "").strip()

            try:
                # Buscar cliente pelo CPF (tenta sem formatação e com formatação)
                customer = (
                    Customer.objects.select_related("user")
                    .filter(cpf__in=[cpf_cleaned, username_or_cpf])
                    .first()
                )

                if customer:
                    # Tentar autenticar com o username do usuário encontrado
                    logger.debug(f"Usuário encontrado pelo CPF: {customer.user.username}")
                    user = authenticate(
                        request, username=customer.user.username, password=password
                    )
                else:
                    logger.debug("Nenhum cliente encontrado com o CPF fornecido.")
            except Exception:
                logger.error("Erro ao buscar cliente por CPF")

        if user is not None:
            # Bloquear superusers
            if user.is_superuser:
                return render(
                    request,
                    "customers/login.html",
                    {
                        "error": "Administradores devem usar o login do dashboard (/dashboard/login/)."
                    },
                )

            # Verificar se tem perfil de cliente
            if not hasattr(user, "customer_profile"):
                return render(
                    request,
                    "customers/login.html",
                    {"error": "Usuário sem perfil de cliente válido."},
                )

            # Verificar se cliente está ativo
            if not user.customer_profile.is_active:
                return render(
                    request,
                    "customers/login.html",
                    {"error": "Sua conta está inativa. Entre em contato conosco."},
                )

            login(request, user)
            # Redirecionar para onde estava tentando acessar
            next_url = request.GET.get("next", "product_list")
            return redirect(next_url)

        return render(
            request,
            "customers/login.html",
            {"error": "Usuário ou senha incorretos."},
        )

    return render(request, "customers/login.html")


@login_required
def customer_logout_view(request):
    """Logout de cliente"""
    logout(request)
    return redirect("product_list")
