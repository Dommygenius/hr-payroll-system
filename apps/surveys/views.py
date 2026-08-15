from rest_framework import serializers
from rest_framework.permissions import IsAuthenticated

from apps.core.permissions import IsCompanyMember
from apps.core.viewsets import CompanyScopedModelViewSet

from apps.surveys.models import Survey, SurveyQuestion, SurveyResponse


class SurveySerializer(serializers.ModelSerializer):
    class Meta:
        model = Survey
        fields = '__all__'


class SurveyQuestionSerializer(serializers.ModelSerializer):
    class Meta:
        model = SurveyQuestion
        fields = '__all__'


class SurveyResponseSerializer(serializers.ModelSerializer):
    class Meta:
        model = SurveyResponse
        fields = '__all__'
        read_only_fields = ['company']

    def to_representation(self, instance):
        data = super().to_representation(instance)
        survey = getattr(instance, 'survey', None)
        if survey and getattr(survey, 'is_anonymous', False):
            data['respondent'] = None
        return data


class SurveyViewSet(CompanyScopedModelViewSet):
    queryset = Survey.objects.all()
    serializer_class = SurveySerializer
    permission_classes = [IsAuthenticated, IsCompanyMember]
    search_fields = ['title', 'description']
    filterset_fields = ['company', 'status', 'is_anonymous']


class SurveyQuestionViewSet(CompanyScopedModelViewSet):
    queryset = SurveyQuestion.objects.all()
    serializer_class = SurveyQuestionSerializer
    permission_classes = [IsAuthenticated, IsCompanyMember]
    filterset_fields = ['company', 'survey', 'question_type', 'is_required']


class SurveyResponseViewSet(CompanyScopedModelViewSet):
    queryset = SurveyResponse.objects.all()
    serializer_class = SurveyResponseSerializer
    permission_classes = [IsAuthenticated, IsCompanyMember]
    filterset_fields = ['company', 'survey', 'respondent']

    def perform_create(self, serializer):
        survey = serializer.validated_data.get('survey')
        extra = self._tenant_stamp(serializer)
        extra['respondent'] = None if (survey and getattr(survey, 'is_anonymous', False)) else self.request.user
        serializer.save(**extra)
