from django.urls import path

from . import views

app_name = "customers"

urlpatterns = [
    path("login/", views.customer_login_view, name="login"),
    path("logout/", views.customer_logout_view, name="logout"),
]
