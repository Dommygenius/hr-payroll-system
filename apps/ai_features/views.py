from django.utils import timezone
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import serializers

from apps.ai_features.models import AIAnalysisJob, ChatbotConversation, ChatbotMessage
from apps.ai_features.services import (
    AttendanceAnomalyService,
    AttritionPredictionService,
    CandidateRankingService,
    HRChatbotService,
    PayrollAnomalyService,
    ReportGenerationService,
    ResumeScreeningService,
)
from apps.core.models import Company
from apps.core.permissions import IsCompanyMember
from apps.core.viewsets import CompanyScopedModelViewSet


class AIAnalysisJobSerializer(serializers.ModelSerializer):
    class Meta:
        model = AIAnalysisJob
        fields = '__all__'


class ChatbotConversationSerializer(serializers.ModelSerializer):
    class Meta:
        model = ChatbotConversation
        fields = '__all__'


class ChatbotMessageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ChatbotMessage
        fields = '__all__'


class AIAnalysisJobViewSet(CompanyScopedModelViewSet):
    queryset = AIAnalysisJob.objects.all()
    serializer_class = AIAnalysisJobSerializer
    permission_classes = [IsAuthenticated, IsCompanyMember]
    filterset_fields = ['company', 'job_type', 'status']


class ChatbotConversationViewSet(CompanyScopedModelViewSet):
    queryset = ChatbotConversation.objects.all()
    serializer_class = ChatbotConversationSerializer
    permission_classes = [IsAuthenticated, IsCompanyMember]
    filterset_fields = ['user', 'is_active']

    def get_queryset(self):
        return ChatbotConversation.objects.filter(user=self.request.user)


class ChatbotMessageViewSet(CompanyScopedModelViewSet):
    queryset = ChatbotMessage.objects.all()
    serializer_class = ChatbotMessageSerializer
    permission_classes = [IsAuthenticated, IsCompanyMember]
    filterset_fields = ['conversation', 'role']

    def get_queryset(self):
        return ChatbotMessage.objects.filter(conversation__user=self.request.user)


class ChatbotPostMessageView(APIView):
    """POST a user message and receive an assistant response."""

    permission_classes = [IsAuthenticated, IsCompanyMember]

    def post(self, request):
        if not getattr(request.user, 'company_id', None) and not request.user.is_superuser:
            return Response({'error': 'No company assigned to this user.'}, status=status.HTTP_403_FORBIDDEN)

        message = request.data.get('message', '').strip()
        if not message:
            return Response({'error': 'message is required'}, status=status.HTTP_400_BAD_REQUEST)

        conversation_id = request.data.get('conversation_id')
        if conversation_id:
            conversation = ChatbotConversation.objects.filter(
                pk=conversation_id, user=request.user
            ).first()
            if not conversation:
                return Response({'error': 'Conversation not found'}, status=status.HTTP_404_NOT_FOUND)
        else:
            conversation = ChatbotConversation.objects.create(user=request.user)

        prior = [
            {'role': m.role, 'content': m.content}
            for m in conversation.messages.order_by('created_at')
        ]

        ChatbotMessage.objects.create(
            conversation=conversation,
            role='user',
            content=message,
        )

        response_text = HRChatbotService.respond(message, history=prior, user=request.user)

        assistant_message = ChatbotMessage.objects.create(
            conversation=conversation,
            role='assistant',
            content=response_text['text'],
        )

        return Response({
            'conversation_id': str(conversation.id),
            'session_id': str(conversation.session_id),
            'user_message': message,
            'response': response_text['text'],
            'source': response_text.get('source', 'assistant'),
            'model': response_text.get('model', ''),
            'assistant_message': ChatbotMessageSerializer(assistant_message).data,
        })


class TriggerAIJobView(APIView):
    """Trigger an AI analysis job using the appropriate service."""

    permission_classes = [IsAuthenticated, IsCompanyMember]

    def post(self, request):
        job_type = request.data.get('job_type')
        input_data = request.data.get('input_data', {}) or {}

        valid_types = [choice[0] for choice in AIAnalysisJob.JobType.choices]
        if job_type not in valid_types:
            return Response(
                {'error': f'Invalid job_type. Must be one of: {valid_types}'},
                status=status.HTTP_400_BAD_REQUEST,
            )

        company = getattr(request.user, 'company', None)
        if company is None and request.user.is_superuser:
            company_id = request.data.get('company_id')
            if company_id:
                company = Company.objects.filter(pk=company_id, is_active=True).first()
        if company is None:
            return Response(
                {'error': 'No company assigned. AI jobs require a company context.'},
                status=status.HTTP_403_FORBIDDEN,
            )

        job = AIAnalysisJob.objects.create(
            company=company,
            job_type=job_type,
            status=AIAnalysisJob.Status.PROCESSING,
            input_data=input_data,
            requested_by=request.user,
        )

        handlers = {
            AIAnalysisJob.JobType.RESUME_SCREENING: lambda: ResumeScreeningService.screen_resume(
                input_data.get('applicant_id', ''), company=company
            ),
            AIAnalysisJob.JobType.CANDIDATE_RANKING: lambda: CandidateRankingService.rank(
                input_data.get('job_posting_id', ''), company=company
            ),
            AIAnalysisJob.JobType.PAYROLL_ANOMALY: lambda: PayrollAnomalyService.detect_anomalies(
                input_data.get('payroll_run_id', ''), company=company
            ),
            AIAnalysisJob.JobType.ATTRITION_PREDICTION: lambda: AttritionPredictionService.predict(
                input_data.get('employee_id', ''), company=company
            ),
            AIAnalysisJob.JobType.ATTENDANCE_ANOMALY: lambda: AttendanceAnomalyService.detect(
                input_data.get('employee_id', ''),
                days=int(input_data.get('days', 30)),
                company=company,
            ),
            AIAnalysisJob.JobType.REPORT_GENERATION: lambda: ReportGenerationService.generate(
                company=company,
                report_type=str(input_data.get('report_type') or 'workforce'),
            ),
        }

        handler = handlers.get(job_type)
        if not handler:
            job.status = AIAnalysisJob.Status.FAILED
            job.error_message = f'No handler implemented for job type: {job_type}'
            job.save(update_fields=['status', 'error_message'])
            return Response(
                AIAnalysisJobSerializer(job).data,
                status=status.HTTP_501_NOT_IMPLEMENTED,
            )

        try:
            result = handler()
            if isinstance(result, dict) and result.get('error'):
                job.status = AIAnalysisJob.Status.FAILED
                job.error_message = result['error']
            else:
                job.status = AIAnalysisJob.Status.COMPLETED
                job.result = result if isinstance(result, (dict, list)) else {'data': result}
                job.completed_at = timezone.now()
                if isinstance(result, dict) and 'score' in result:
                    job.confidence_score = result['score']
                elif isinstance(result, dict) and 'risk_score' in result:
                    job.confidence_score = result['risk_score']
        except Exception as exc:
            job.status = AIAnalysisJob.Status.FAILED
            job.error_message = str(exc)

        job.save()
        return Response(AIAnalysisJobSerializer(job).data, status=status.HTTP_201_CREATED)
