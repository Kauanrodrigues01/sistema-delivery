from django.urls import path

from .views import get_daily_report

app_name = "reports"

urlpatterns = [
    path("daily/", get_daily_report, name="daily_report"),
]
