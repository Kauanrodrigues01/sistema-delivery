from django.urls import path

from .views import daily_report_pdf, get_daily_report, saved_report_pdf

app_name = "reports"

urlpatterns = [
    path("daily/", get_daily_report, name="daily_report"),
    path("daily/pdf/", daily_report_pdf, name="daily_report_pdf"),
    path("saved/<int:report_id>/pdf/", saved_report_pdf, name="saved_report_pdf"),
]
