from rest_framework import serializers
from rest_framework.permissions import IsAuthenticated

from apps.core.permissions import IsCompanyMember
from apps.core.viewsets import CompanyScopedModelViewSet

from apps.performance.models import Feedback360, Goal, KPI, PerformanceCycle, PerformanceReview


class PerformanceCycleSerializer(serializers.ModelSerializer):
    class Meta:
        model = PerformanceCycle
        fields = '__all__'


class GoalSerializer(serializers.ModelSerializer):
    class Meta:
        model = Goal
        fields = '__all__'


class KPISerializer(serializers.ModelSerializer):
    class Meta:
        model = KPI
        fields = '__all__'


class PerformanceReviewSerializer(serializers.ModelSerializer):
    class Meta:
        model = PerformanceReview
        fields = '__all__'


class Feedback360Serializer(serializers.ModelSerializer):
    class Meta:
        model = Feedback360
        fields = '__all__'


class PerformanceCycleViewSet(CompanyScopedModelViewSet):
    queryset = PerformanceCycle.objects.all()
    serializer_class = PerformanceCycleSerializer
    permission_classes = [IsAuthenticated, IsCompanyMember]
    search_fields = ['name', 'description']
    filterset_fields = ['company', 'status']


class GoalViewSet(CompanyScopedModelViewSet):
    queryset = Goal.objects.all()
    serializer_class = GoalSerializer
    permission_classes = [IsAuthenticated, IsCompanyMember]
    search_fields = ['title', 'description']
    filterset_fields = ['company', 'employee', 'cycle', 'status']


class KPIViewSet(CompanyScopedModelViewSet):
    queryset = KPI.objects.all()
    serializer_class = KPISerializer
    permission_classes = [IsAuthenticated, IsCompanyMember]
    search_fields = ['name', 'description']
    filterset_fields = ['company', 'department', 'is_active']


class PerformanceReviewViewSet(CompanyScopedModelViewSet):
    queryset = PerformanceReview.objects.all()
    serializer_class = PerformanceReviewSerializer
    permission_classes = [IsAuthenticated, IsCompanyMember]
    filterset_fields = ['company', 'employee', 'cycle', 'reviewer', 'status']


class Feedback360ViewSet(CompanyScopedModelViewSet):
    queryset = Feedback360.objects.all()
    serializer_class = Feedback360Serializer
    permission_classes = [IsAuthenticated, IsCompanyMember]
    filterset_fields = ['company', 'review', 'reviewer', 'relationship']
