from django.urls import include, path
from rest_framework.routers import DefaultRouter

from apps.disciplinary.views import (
    DisciplinaryHearingViewSet,
    IncidentViewSet,
    SuspensionViewSet,
    WarningViewSet,
)

router = DefaultRouter()
router.register('incidents', IncidentViewSet, basename='incident')
router.register('warnings', WarningViewSet, basename='warning')
router.register('suspensions', SuspensionViewSet, basename='suspension')
router.register('hearings', DisciplinaryHearingViewSet, basename='disciplinary-hearing')

urlpatterns = [path('', include(router.urls))]
