from django.urls import include, path
from rest_framework.routers import DefaultRouter

from apps.recruitment.views import (
    ApplicantViewSet,
    InterviewViewSet,
    JobPostingViewSet,
    OfferLetterViewSet,
    OnboardingChecklistViewSet,
)

router = DefaultRouter()
router.register('jobs', JobPostingViewSet, basename='job-posting')
router.register('applicants', ApplicantViewSet, basename='applicant')
router.register('interviews', InterviewViewSet, basename='interview')
router.register('offers', OfferLetterViewSet, basename='offer-letter')
router.register('onboarding', OnboardingChecklistViewSet, basename='onboarding-checklist')

urlpatterns = [path('', include(router.urls))]
