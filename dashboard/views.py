from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.core.paginator import Paginator
from django.db import models, transaction
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_http_methods, require_POST

from customers.models import Customer
from orders.models import Order, OrderItem
from products.models import Category, Product
from reports.models import DailyReport
from utils.normalize import normalize_cpf, normalize_phone

from .utils.metrics import calculate_metrics


# Login view
def login_view(request):
    if request.method == "POST":
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)
        if user is not None:
            if not user.is_superuser:
                return render(
                    request,
                    "dashboard/login.html",
                    {"error": "Acesso negado. Usuário não é administrador."},
                )
            login(request, user)
            return redirect("dashboard:dashboard")
        else:
            return render(
                request, "dashboard/login.html", {"error": "Credenciais inválidas"}
            )
    return render(request, "dashboard/login.html")


# Dashboard view
@login_required
def dashboard_view(request):
    if not request.user.is_superuser:
        return redirect("product_list")
    metrics = calculate_metrics()
    return render(request, "dashboard/dashboard.html", {"metrics": metrics})


# Product CRUD views
@login_required
def product_list(request):
    if not request.user.is_superuser:
        return redirect("product_list")

    # Get filter parameters from the request
    status_filter = request.GET.get("status")
    category_filter = request.GET.get("category")
    search_query = request.GET.get("search", "")

    # Filter products based on the status
    if status_filter == "active":
        products = Product.objects.filter(is_active=True)
    elif status_filter == "inactive":
        products = Product.objects.filter(is_active=False)
    else:
        products = Product.objects.all()

    # Filter by category
    if category_filter:
        products = products.filter(category_id=category_filter)

    # Filter by search query
    if search_query:
        products = products.filter(name__icontains=search_query)

    # Order by most recent
    products = products.order_by("-created_at")

    # Get all categories for filter dropdown
    categories = Category.objects.all().order_by("name")

    # Paginação
    from django.core.paginator import Paginator

    paginator = Paginator(products, 9)  # 9 produtos por página
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)

    return render(
        request,
        "dashboard/product_list.html",
        {
            "products": page_obj,
            "categories": categories,
            "status_filter": status_filter,
            "category_filter": category_filter,
            "search_query": search_query,
            "page_obj": page_obj,
            "is_paginated": page_obj.has_other_pages(),
        },
    )


@login_required
@require_POST
def product_create(request):
    if not request.user.is_superuser:
        return redirect("product_list")

    name = request.POST.get("name")
    price = request.POST.get("price")
    image = request.FILES.get("image")
    category_id = request.POST.get("category")
    is_active = request.POST.get("is_active") == "true"

    category = get_object_or_404(Category, pk=category_id)
    Product.objects.create(
        name=name, price=price, image=image, category=category, is_active=is_active
    )

    return redirect("dashboard:product_list")


@login_required
@require_POST
def product_edit(request, pk):
    if not request.user.is_superuser:
        return redirect("product_list")

    product = Product.objects.get(pk=pk)
    product.name = request.POST["name"]
    product.price = request.POST["price"]
    product.image = request.FILES.get("image", product.image)

    category_id = request.POST.get("category")
    if category_id:
        product.category = get_object_or_404(Category, pk=category_id)

    product.save()
    return redirect("dashboard:product_list")


@login_required
@require_http_methods(["DELETE"])
def product_delete(request, pk):
    if not request.user.is_superuser:
        return redirect("product_list")

    product = Product.objects.get(pk=pk)
    product.delete()
    return redirect("dashboard:product_list")


@login_required
@require_POST
def product_toggle_active(request, pk):
    if not request.user.is_superuser:
        return redirect("product_list")

    product = Product.objects.get(pk=pk)
    product.is_active = not product.is_active
    product.save()
    return redirect("dashboard:product_list")


# Logout view
@login_required
def logout_view(request):
    if not request.user.is_superuser:
        return redirect("product_list")

    logout(request)
    return redirect("dashboard:login")


# Order CRUD views
@login_required
def order_list(request):
    if not request.user.is_superuser:
        return redirect("product_list")

    # Get filter parameters from the request
    status_filter = request.GET.get("status")
    payment_status_filter = request.GET.get("payment_status")
    search_query = request.GET.get("search", "")

    # Start with optimized queryset using select_related
    orders = Order.objects.select_related().prefetch_related("items__product")

    # Filter orders based on the status
    if status_filter == "pending":
        orders = orders.filter(status="pending")
    elif status_filter == "completed":
        orders = orders.filter(status="completed")
    elif status_filter == "cancelled":
        orders = orders.filter(status="cancelled")
    elif status_filter == "late":
        # Filtrar pedidos atrasados (pendentes há mais de 25 minutos)
        from datetime import timedelta

        from django.utils import timezone

        cutoff_time = timezone.now() - timedelta(minutes=25)
        orders = orders.filter(status="pending", created_at__lt=cutoff_time)

    # Filter by payment status
    if payment_status_filter == "pending":
        orders = orders.filter(payment_status="pending")
    elif payment_status_filter == "paid":
        orders = orders.filter(payment_status="paid")
    elif payment_status_filter == "cancelled":
        orders = orders.filter(payment_status="cancelled")

    # Filter by search query (customer name or phone)
    if search_query:
        orders = orders.filter(
            models.Q(customer_name__icontains=search_query)
            | models.Q(phone__icontains=search_query)
        )

    # Order by most recent
    orders = orders.order_by("-created_at")

    # Paginação
    from django.core.paginator import Paginator

    paginator = Paginator(orders, 10)  # 10 pedidos por página
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)

    return render(
        request,
        "dashboard/order_list.html",
        {
            "orders": page_obj,
            "status_filter": status_filter,
            "payment_status_filter": payment_status_filter,
            "search_query": search_query,
            "page_obj": page_obj,
            "is_paginated": page_obj.has_other_pages(),
        },
    )


@login_required
def order_detail(request, pk):
    if not request.user.is_superuser:
        return redirect("product_list")

    order = get_object_or_404(Order, pk=pk)
    return render(request, "dashboard/order_detail.html", {"order": order})


@login_required
def order_create(request):
    if not request.user.is_superuser:
        return redirect("product_list")

    if request.method == "POST":
        customer_name = request.POST.get("customer_name")
        phone = request.POST.get("phone")
        address = request.POST.get("address")
        status = request.POST.get("status", "pending")

        # Get product IDs and quantities from the form
        product_ids = request.POST.getlist("product_id")
        quantities = request.POST.getlist("quantity")

        # Create order with items in a transaction
        with transaction.atomic():
            order = Order.objects.create(
                customer_name=customer_name, phone=phone, address=address, status=status
            )

            # Create order items
            for product_id, quantity in zip(product_ids, quantities, strict=False):
                if product_id and quantity and int(quantity) > 0:
                    product = Product.objects.get(pk=product_id)
                    OrderItem.objects.create(
                        order=order, product=product, quantity=int(quantity)
                    )

        return redirect("dashboard:order_list")

    # GET request - show form
    products = Product.objects.filter(is_active=True)
    return render(request, "dashboard/order_create.html", {"products": products})


@login_required
def order_edit(request, pk):
    if not request.user.is_superuser:
        return redirect("product_list")

    order = get_object_or_404(Order, pk=pk)

    # Não permitir editar pedido se não pode editar informações básicas (finalizado)
    if not order.can_edit_basic_info:
        return redirect("dashboard:order_detail", pk=order.pk)

    if request.method == "POST":
        # Sempre permitir edição de informações básicas se can_edit_basic_info é True
        order.customer_name = request.POST.get("customer_name")
        order.phone = request.POST.get("phone")
        order.address = request.POST.get("address")
        order.status = request.POST.get("status")

        # Só permitir edição de itens se can_edit_items for True
        if order.can_edit_items:
            # Get product IDs and quantities from the form
            product_ids = request.POST.getlist("product_id")
            quantities = request.POST.getlist("quantity")

            # Update order and items in a transaction
            with transaction.atomic():
                order.save()

                # Delete existing items and create new ones
                order.items.all().delete()

                # Create new order items
                for product_id, quantity in zip(product_ids, quantities, strict=False):
                    if product_id and quantity and int(quantity) > 0:
                        product = Product.objects.get(pk=product_id)
                        OrderItem.objects.create(
                            order=order, product=product, quantity=int(quantity)
                        )
        else:
            # Se não pode editar itens, apenas salva as informações básicas
            order.save()

        return redirect("dashboard:order_detail", pk=order.pk)

    # GET request - show form
    products = Product.objects.filter(is_active=True)

    # Prepare products with order information
    order_items = {item.product.id: item for item in order.items.all()}
    products_with_order_info = []
    for product in products:
        product_info = {
            "product": product,
            "is_in_order": product.id in order_items,
            "quantity": order_items[product.id].quantity
            if product.id in order_items
            else 1,
        }
        products_with_order_info.append(product_info)

    return render(
        request,
        "dashboard/order_edit.html",
        {
            "order": order,
            "products": products,
            "products_with_order_info": products_with_order_info,
        },
    )


@login_required
@require_http_methods(["POST"])
def order_cancel(request, pk):
    if not request.user.is_superuser:
        return redirect("product_list")

    order = get_object_or_404(Order, pk=pk)
    # Não permitir cancelar pedido se está finalizado (concluído e pago)
    if order.is_finalized:
        return redirect("dashboard:order_detail", pk=order.pk)

    # Permitir cancelar se a entrega foi concluída mas o pagamento foi cancelado
    # Isso faz sentido quando houve problema com o produto e foi devolvido o dinheiro
    if order.status == "completed" and order.payment_status == "cancelled":
        order.status = "cancelled"
        order.save()
        return redirect("dashboard:order_list")

    # Para outros casos, só permite cancelar se o status for "pending"
    if order.status == "pending":
        order.status = "cancelled"
        # Sempre cancelar também o pagamento automaticamente
        order.payment_status = "cancelled"
        order.save()

    return redirect("dashboard:order_list")


@login_required
@require_POST
def order_toggle_status(request, pk):
    if not request.user.is_superuser:
        return redirect("product_list")

    order = get_object_or_404(Order, pk=pk)
    # Não permitir alterar status de pedidos cancelados
    if order.status == "cancelled":
        return redirect("dashboard:order_detail", pk=order.pk)

    # Não permitir alterar status se pedido está finalizado (concluído e pago)
    if order.is_finalized:
        return redirect("dashboard:order_detail", pk=order.pk)

    if order.status == "pending":
        order.status = "completed"
    else:
        order.status = "pending"
    order.save()
    return redirect("dashboard:order_detail", pk=order.pk)


@login_required
@require_POST
def order_toggle_payment_status(request, pk):
    if not request.user.is_superuser:
        return redirect("product_list")

    order = get_object_or_404(Order, pk=pk)
    # Permitir alteração apenas se o pagamento não estiver cancelado
    if order.payment_status == "cancelled":
        return redirect("dashboard:order_detail", pk=order.pk)

    # Não permitir alterar pagamento se pedido está finalizado (concluído e pago)
    if order.is_finalized:
        return redirect("dashboard:order_detail", pk=order.pk)

    # Permitir alterar pagamento mesmo para pedidos cancelados (exceto se finalizado)
    if order.payment_status == "pending":
        order.payment_status = "paid"
    else:
        order.payment_status = "pending"
    order.save()
    return redirect("dashboard:order_detail", pk=order.pk)


@login_required
@require_POST
def order_cancel_payment(request, pk):
    if not request.user.is_superuser:
        return redirect("product_list")

    order = get_object_or_404(Order, pk=pk)
    # Não permitir cancelar pagamento se pedido está finalizado (concluído e pago)
    if order.is_finalized:
        return redirect("dashboard:order_detail", pk=order.pk)

    # Só permite cancelar pagamento se não estiver já cancelado
    if order.payment_status != "cancelled":
        order.payment_status = "cancelled"
        order.save()
    return redirect("dashboard:order_detail", pk=order.pk)


# Category CRUD views
@login_required
def category_list(request):
    if not request.user.is_superuser:
        return redirect("product_list")

    # Get filter parameters from the request
    search_query = request.GET.get("search", "")

    # Get all categories
    categories = Category.objects.all()

    # Filter by search query
    if search_query:
        categories = categories.filter(name__icontains=search_query)

    # Order by name
    categories = categories.order_by("name")

    # Paginação
    from django.core.paginator import Paginator

    paginator = Paginator(categories, 10)  # 10 categorias por página
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)

    return render(
        request,
        "dashboard/category_list.html",
        {
            "categories": page_obj,
            "search_query": search_query,
            "page_obj": page_obj,
            "is_paginated": page_obj.has_other_pages(),
        },
    )


@login_required
@require_POST
def category_create(request):
    if not request.user.is_superuser:
        return redirect("product_list")

    name = request.POST.get("name")
    description = request.POST.get("description", "")

    Category.objects.create(name=name, description=description)

    return redirect("dashboard:category_list")


@login_required
@require_POST
def category_edit(request, pk):
    if not request.user.is_superuser:
        return redirect("product_list")

    category = Category.objects.get(pk=pk)
    category.name = request.POST["name"]
    category.description = request.POST.get("description", "")
    category.save()
    return redirect("dashboard:category_list")


@login_required
@require_http_methods(["DELETE"])
def category_delete(request, pk):
    if not request.user.is_superuser:
        return redirect("product_list")

    category = Category.objects.get(pk=pk)
    # Verificar se existem produtos usando esta categoria
    if category.products.exists():
        # Retornar erro - não pode deletar categoria com produtos
        return redirect("dashboard:category_list")
    category.delete()
    return redirect("dashboard:category_list")


# Customer CRUD views
@login_required
def customer_list(request):
    """Lista todos os clientes fiéis"""
    if not request.user.is_superuser:
        return redirect("product_list")

    search_query = request.GET.get("search", "")
    status_filter = request.GET.get("status", "")

    customers = Customer.objects.select_related("user").all()

    # Filtro de busca
    if search_query:
        customers = customers.filter(
            models.Q(full_name__icontains=search_query)
            | models.Q(phone__icontains=search_query)
            | models.Q(cpf__icontains=search_query)
            | models.Q(user__username__icontains=search_query)
        )

    # Filtro por status
    if status_filter == "active":
        customers = customers.filter(is_active=True)
    elif status_filter == "inactive":
        customers = customers.filter(is_active=False)

    customers = customers.order_by("-created_at")

    # Paginação
    from django.core.paginator import Paginator

    paginator = Paginator(customers, 10)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)

    # Pegar mensagens do session
    error_message = request.session.pop("error_message", None)
    success_message = request.session.pop("success_message", None)

    return render(
        request,
        "dashboard/customer_list.html",
        {
            "customers": page_obj,
            "search_query": search_query,
            "status_filter": status_filter,
            "page_obj": page_obj,
            "is_paginated": page_obj.has_other_pages(),
            "error_message": error_message,
            "success_message": success_message,
        },
    )


@login_required
@require_POST
def customer_create(request):
    """Criar novo cliente fiel"""
    if not request.user.is_superuser:
        return redirect("product_list")

    try:
        with transaction.atomic():
            # Criar usuário Django
            username = request.POST.get("username")
            password = request.POST.get("password")
            email = request.POST.get("email", "")

            # Verificar se username já existe
            if User.objects.filter(username=username).exists():
                request.session["error_message"] = (
                    f"O nome de usuário '{username}' já está em uso."
                )
                return redirect("dashboard:customer_list")

            user = User.objects.create_user(
                username=username,
                password=password,
                email=email,
                is_superuser=False,
                is_staff=False,
            )

            cpf = request.POST.get("cpf") or None
            phone = request.POST.get("phone") or None

            normalized_cpf = normalize_cpf(cpf)
            normalized_phone = normalize_phone(phone)

            if normalized_cpf:
                if Customer.objects.filter(cpf=normalized_cpf).exists():
                    request.session["error_message"] = (
                        f"O CPF '{cpf}' já está cadastrado."
                    )
                    return redirect("dashboard:customer_list")

            # Criar perfil de cliente
            Customer.objects.create(
                user=user,
                full_name=request.POST.get("full_name"),
                phone=normalized_phone,
                cpf=normalized_cpf,
                address=request.POST.get("address"),
                is_active=request.POST.get("is_active") == "true",
            )

            request.session["success_message"] = (
                f"Cliente '{request.POST.get('full_name')}' criado com sucesso!"
            )
    except Exception as e:
        # Humanizar mensagens de erro do banco de dados
        error_msg = str(e).lower()

        if "unique constraint" in error_msg or "duplicate" in error_msg:
            if "username" in error_msg:
                request.session["error_message"] = (
                    "Este nome de usuário já está sendo usado por outro cliente."
                )
            elif "cpf" in error_msg:
                request.session["error_message"] = (
                    "Este CPF já está cadastrado no sistema."
                )
            elif "email" in error_msg:
                request.session["error_message"] = (
                    "Este e-mail já está cadastrado no sistema."
                )
            else:
                request.session["error_message"] = (
                    "Já existe um cliente com esses dados cadastrados."
                )
        elif "required" in error_msg or "null" in error_msg or "not-null" in error_msg:
            request.session["error_message"] = (
                "Por favor, preencha todos os campos obrigatórios."
            )
        elif "invalid" in error_msg:
            request.session["error_message"] = (
                "Alguns dados fornecidos são inválidos. Verifique e tente novamente."
            )
        else:
            request.session["error_message"] = (
                "Não foi possível criar o cliente. Tente novamente."
            )

    return redirect("dashboard:customer_list")


@login_required
@require_POST
def customer_edit(request, pk):
    """Editar cliente existente"""
    if not request.user.is_superuser:
        return redirect("product_list")

    try:
        customer = get_object_or_404(Customer, pk=pk)

        cpf = request.POST.get("cpf") or None
        phone = request.POST.get("phone") or None

        normalize_cpf = cpf.replace(".", "").replace("-", "").strip() if cpf else None
        normalize_phone = (
            phone.replace(".", "")
            .replace("-", "")
            .replace("(", "")
            .replace(")", "")
            .strip()
            if phone
            else None
        )

        # Verificar se CPF já existe em outro cliente
        if normalize_cpf:
            existing_cpf = (
                Customer.objects.filter(cpf=normalize_cpf).exclude(pk=pk).first()
            )
            if existing_cpf:
                request.session["error_message"] = (
                    f"O CPF '{cpf}' já está cadastrado para outro cliente."
                )
                return redirect("dashboard:customer_list")

        customer.full_name = request.POST.get("full_name")
        customer.phone = normalize_phone
        customer.cpf = normalize_cpf
        customer.address = request.POST.get("address")
        customer.is_active = request.POST.get("is_active") == "true"

        # Atualizar email do usuário
        customer.user.email = request.POST.get("email", "")
        customer.user.save()

        # Se forneceu nova senha, atualizar
        new_password = request.POST.get("password")
        if new_password:
            customer.user.set_password(new_password)
            customer.user.save()

        customer.save()
        request.session["success_message"] = (
            f"Cliente '{customer.full_name}' atualizado com sucesso!"
        )
    except Exception as e:
        # Humanizar mensagens de erro do banco de dados
        error_msg = str(e).lower()

        if "unique constraint" in error_msg or "duplicate" in error_msg:
            if "cpf" in error_msg:
                request.session["error_message"] = (
                    "Este CPF já está cadastrado para outro cliente."
                )
            elif "email" in error_msg:
                request.session["error_message"] = (
                    "Este e-mail já está cadastrado para outro cliente."
                )
            else:
                request.session["error_message"] = (
                    "Já existe outro cliente com esses dados."
                )
        elif "required" in error_msg or "null" in error_msg or "not-null" in error_msg:
            request.session["error_message"] = (
                "Por favor, preencha todos os campos obrigatórios."
            )
        elif "invalid" in error_msg:
            request.session["error_message"] = (
                "Alguns dados fornecidos são inválidos. Verifique e tente novamente."
            )
        else:
            request.session["error_message"] = (
                "Não foi possível atualizar o cliente. Tente novamente."
            )

    return redirect("dashboard:customer_list")


@login_required
@require_POST
def customer_toggle_active(request, pk):
    """Ativar/desativar cliente"""
    if not request.user.is_superuser:
        return redirect("product_list")

    try:
        customer = get_object_or_404(Customer, pk=pk)
        customer.is_active = not customer.is_active
        customer.save()
        status = "ativado" if customer.is_active else "desativado"
        request.session["success_message"] = (
            f"Cliente '{customer.full_name}' foi {status} com sucesso!"
        )
    except Exception:
        status_pretendido = "ativar" if not customer.is_active else "desativar"
        request.session["error_message"] = (
            f"Não foi possível {status_pretendido} o cliente. Tente novamente."
        )

    return redirect("dashboard:customer_list")


@login_required
@require_http_methods(["DELETE"])
def customer_delete(request, pk):
    """Deletar cliente e usuário associado"""
    if not request.user.is_superuser:
        return redirect("product_list")

    try:
        customer = get_object_or_404(Customer, pk=pk)
        customer_name = customer.full_name
        user = customer.user
        customer.delete()
        user.delete()
        request.session["success_message"] = (
            f"Cliente '{customer_name}' foi excluído com sucesso!"
        )
    except Exception:
        request.session["error_message"] = (
            "Não foi possível excluir o cliente. Tente novamente."
        )

    return redirect("dashboard:customer_list")


# Reports list view
@login_required
def reports_list(request):
    """Lista todos os relatórios diários salvos"""
    if not request.user.is_superuser:
        return redirect("product_list")

    date_from = request.GET.get("date_from", "")
    date_to = request.GET.get("date_to", "")

    # Otimizar query para retornar apenas os campos necessários
    reports = DailyReport.objects.only("id", "date", "created_at")

    # Filtro por intervalo de datas
    if date_from:
        reports = reports.filter(date__gte=date_from)
    if date_to:
        reports = reports.filter(date__lte=date_to)

    reports = reports.order_by("-date")

    # Paginação
    paginator = Paginator(reports, 10)  # 10 relatórios por página
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)

    return render(
        request,
        "dashboard/reports_list.html",
        {
            "reports": page_obj,
            "date_from": date_from,
            "date_to": date_to,
            "page_obj": page_obj,
            "is_paginated": page_obj.has_other_pages(),
        },
    )
