from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render


def customer_login_view(request):
    """
    View de login específico para clientes (não superusers)

    Permite que clientes fiéis façam login para ter vantagens no checkout.
    Bloqueia acesso de superusers (que devem usar /dashboard/login/).
    """
    # Se já está logado, redirecionar
    if request.user.is_authenticated:
        if request.user.is_superuser:
            return redirect("dashboard:dashboard")
        return redirect("product_list")

    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")
        user = authenticate(request, username=username, password=password)

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
        else:
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
