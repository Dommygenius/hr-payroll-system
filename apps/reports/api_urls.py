from django.urls import path

from apps.reports.views import DashboardStatsView, ReportExportView

urlpatterns = [
    path('dashboard-stats/', DashboardStatsView.as_view(), name='dashboard-stats'),
    path('export/', ReportExportView.as_view(), name='report-export'),
]
