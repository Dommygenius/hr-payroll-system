from django.urls import include, path
from rest_framework.routers import DefaultRouter

from apps.surveys.views import SurveyQuestionViewSet, SurveyResponseViewSet, SurveyViewSet

router = DefaultRouter()
router.register('', SurveyViewSet, basename='survey')
router.register('questions', SurveyQuestionViewSet, basename='survey-question')
router.register('responses', SurveyResponseViewSet, basename='survey-response')

urlpatterns = [path('', include(router.urls))]
