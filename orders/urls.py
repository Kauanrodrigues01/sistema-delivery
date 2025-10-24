from django.urls import path

from . import views

app_name = "orders"

urlpatterns = [
    path("", views.order_list, name="order_list"),
    path("<int:order_id>/", views.order_detail, name="order_detail"),
    path("<int:order_id>/cancel/", views.cancel_order, name="cancel_order"),
]
