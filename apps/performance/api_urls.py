from django.urls import include, path
from rest_framework.routers import DefaultRouter

from apps.performance.views import (
    Feedback360ViewSet,
    GoalViewSet,
    KPIViewSet,
    PerformanceCycleViewSet,
    PerformanceReviewViewSet,
)

router = DefaultRouter()
router.register('cycles', PerformanceCycleViewSet, basename='performance-cycle')
router.register('goals', GoalViewSet, basename='goal')
router.register('kpis', KPIViewSet, basename='kpi')
router.register('reviews', PerformanceReviewViewSet, basename='performance-review')
router.register('feedback-360', Feedback360ViewSet, basename='feedback-360')

urlpatterns = [path('', include(router.urls))]
