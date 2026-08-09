from rest_framework import serializers
from rest_framework.permissions import IsAuthenticated

from apps.core.permissions import IsCompanyMember
from apps.core.viewsets import CompanyScopedModelViewSet

from apps.recruitment.models import Applicant, Interview, JobPosting, OfferLetter, OnboardingChecklist


class JobPostingSerializer(serializers.ModelSerializer):
    class Meta:
        model = JobPosting
        fields = '__all__'


class ApplicantSerializer(serializers.ModelSerializer):
    class Meta:
        model = Applicant
        fields = '__all__'


class InterviewSerializer(serializers.ModelSerializer):
    class Meta:
        model = Interview
        fields = '__all__'


class OfferLetterSerializer(serializers.ModelSerializer):
    class Meta:
        model = OfferLetter
        fields = '__all__'


class OnboardingChecklistSerializer(serializers.ModelSerializer):
    class Meta:
        model = OnboardingChecklist
        fields = '__all__'


class JobPostingViewSet(CompanyScopedModelViewSet):
    queryset = JobPosting.objects.all()
    serializer_class = JobPostingSerializer
    permission_classes = [IsAuthenticated, IsCompanyMember]
    search_fields = ['title', 'description']
    filterset_fields = ['company', 'department', 'branch', 'status', 'employment_type', 'is_published']


class ApplicantViewSet(CompanyScopedModelViewSet):
    queryset = Applicant.objects.all()
    serializer_class = ApplicantSerializer
    permission_classes = [IsAuthenticated, IsCompanyMember]
    search_fields = ['first_name', 'last_name', 'email', 'phone']
    filterset_fields = ['company', 'job', 'status', 'source']


class InterviewViewSet(CompanyScopedModelViewSet):
    queryset = Interview.objects.all()
    serializer_class = InterviewSerializer
    permission_classes = [IsAuthenticated, IsCompanyMember]
    filterset_fields = ['company', 'applicant', 'interviewer', 'is_completed']


class OfferLetterViewSet(CompanyScopedModelViewSet):
    queryset = OfferLetter.objects.all()
    serializer_class = OfferLetterSerializer
    permission_classes = [IsAuthenticated, IsCompanyMember]
    filterset_fields = ['company', 'applicant', 'is_accepted']


class OnboardingChecklistViewSet(CompanyScopedModelViewSet):
    queryset = OnboardingChecklist.objects.all()
    serializer_class = OnboardingChecklistSerializer
    permission_classes = [IsAuthenticated, IsCompanyMember]
    search_fields = ['task', 'description']
    filterset_fields = ['company', 'employee', 'assigned_to', 'is_completed']
