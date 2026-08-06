from django.urls import path

from apps.dashboard.views import (
    ai_view,
    clock_in_view,
    index,
    module_create,
    module_delete,
    module_edit,
    module_view,
    reports_view,
)

urlpatterns = [
    path('', index, name='dashboard'),
    path('dashboard/', index, name='dashboard-home'),
    path('module/reports/', reports_view, name='module-reports'),
    path('module/ai/', ai_view, name='module-ai'),
    path('attendance/clock-in/', clock_in_view, name='clock-in'),
    path('module/<str:module>/', module_view, name='module'),
    path('module/<str:module>/<str:tab>/', module_view, name='module-tab'),
    path('module/<str:module>/<str:tab>/create/', module_create, name='module-create'),
    path('module/<str:module>/<str:tab>/<str:pk>/edit/', module_edit, name='module-edit'),
    path('module/<str:module>/<str:tab>/<str:pk>/delete/', module_delete, name='module-delete'),
]
