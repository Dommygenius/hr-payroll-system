from rest_framework import serializers
from rest_framework.permissions import IsAuthenticated

from apps.core.permissions import IsCompanyMember
from apps.core.viewsets import CompanyScopedModelViewSet

from apps.relations.models import ExitInterview, Grievance, Recognition


class GrievanceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Grievance
        fields = '__all__'


class RecognitionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Recognition
        fields = '__all__'


class ExitInterviewSerializer(serializers.ModelSerializer):
    class Meta:
        model = ExitInterview
        fields = '__all__'


class GrievanceViewSet(CompanyScopedModelViewSet):
    queryset = Grievance.objects.all()
    serializer_class = GrievanceSerializer
    permission_classes = [IsAuthenticated, IsCompanyMember]
    search_fields = ['subject', 'description']
    filterset_fields = ['company', 'employee', 'status', 'priority', 'assigned_to']


class RecognitionViewSet(CompanyScopedModelViewSet):
    queryset = Recognition.objects.all()
    serializer_class = RecognitionSerializer
    permission_classes = [IsAuthenticated, IsCompanyMember]
    search_fields = ['title', 'description', 'category']
    filterset_fields = ['company', 'employee', 'awarded_by', 'category']


class ExitInterviewViewSet(CompanyScopedModelViewSet):
    queryset = ExitInterview.objects.all()
    serializer_class = ExitInterviewSerializer
    permission_classes = [IsAuthenticated, IsCompanyMember]
    filterset_fields = ['company', 'employee', 'interviewer']
