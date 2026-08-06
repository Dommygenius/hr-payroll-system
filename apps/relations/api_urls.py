from django.urls import include, path
from rest_framework.routers import DefaultRouter

from apps.relations.views import ExitInterviewViewSet, GrievanceViewSet, RecognitionViewSet

router = DefaultRouter()
router.register('grievances', GrievanceViewSet, basename='grievance')
router.register('recognitions', RecognitionViewSet, basename='recognition')
router.register('exit-interviews', ExitInterviewViewSet, basename='exit-interview')

urlpatterns = [path('', include(router.urls))]
