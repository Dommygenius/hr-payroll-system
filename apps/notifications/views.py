from rest_framework import serializers
from rest_framework.permissions import IsAuthenticated

from apps.core.permissions import IsCompanyMember
from apps.core.viewsets import CompanyScopedModelViewSet

from apps.notifications.models import Announcement, Notification


class NotificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Notification
        fields = '__all__'


class AnnouncementSerializer(serializers.ModelSerializer):
    class Meta:
        model = Announcement
        fields = '__all__'


class NotificationViewSet(CompanyScopedModelViewSet):
    queryset = Notification.objects.all()
    serializer_class = NotificationSerializer
    permission_classes = [IsAuthenticated, IsCompanyMember]
    search_fields = ['title', 'message']
    filterset_fields = ['recipient', 'channel', 'priority', 'is_read']

    def get_queryset(self):
        # Owner-scoped; always limited to the current user
        return Notification.objects.filter(recipient=self.request.user)


class AnnouncementViewSet(CompanyScopedModelViewSet):
    queryset = Announcement.objects.all()
    serializer_class = AnnouncementSerializer
    permission_classes = [IsAuthenticated, IsCompanyMember]
    search_fields = ['title', 'content']
    filterset_fields = ['company', 'author', 'is_pinned', 'is_active']
