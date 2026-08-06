from rest_framework import serializers, viewsets
from rest_framework.permissions import IsAuthenticated

from apps.notifications.models import Announcement, Notification


class NotificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Notification
        fields = '__all__'


class AnnouncementSerializer(serializers.ModelSerializer):
    class Meta:
        model = Announcement
        fields = '__all__'


class NotificationViewSet(viewsets.ModelViewSet):
    queryset = Notification.objects.all()
    serializer_class = NotificationSerializer
    permission_classes = [IsAuthenticated]
    search_fields = ['title', 'message']
    filterset_fields = ['recipient', 'channel', 'priority', 'is_read']

    def get_queryset(self):
        return Notification.objects.filter(recipient=self.request.user)


class AnnouncementViewSet(viewsets.ModelViewSet):
    queryset = Announcement.objects.all()
    serializer_class = AnnouncementSerializer
    permission_classes = [IsAuthenticated]
    search_fields = ['title', 'content']
    filterset_fields = ['company', 'author', 'is_pinned', 'is_active']
