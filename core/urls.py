from django.urls import path

from core.views import cache_stats_view, health_check

urlpatterns = [
    path("health/", health_check, name="health_check"),
    path("cache-stats/", cache_stats_view, name="cache_stats"),
]
