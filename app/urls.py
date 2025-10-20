from django.contrib import admin
from django.urls import include, path, reverse_lazy
from django.views.generic.base import RedirectView

urlpatterns = [
    path("", RedirectView.as_view(url=reverse_lazy("product_list"), permanent=False)),
    path("admin/", admin.site.urls),
    path("", include("core.urls")),
    path("customers/", include("customers.urls")),
    path("products/", include("products.urls")),
    path("cart/", include("cart.urls")),
    path("checkout/", include("checkout.urls")),
    path("dashboard/", include("dashboard.urls")),
    path("services/", include("services.urls")),
]
