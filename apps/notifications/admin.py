from django.contrib import admin

from apps.notifications.models import Announcement, Notification


@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ['title', 'recipient', 'channel', 'priority', 'is_read', 'created_at']
    list_filter = ['channel', 'priority', 'is_read']
    search_fields = ['title', 'message']


@admin.register(Announcement)
class AnnouncementAdmin(admin.ModelAdmin):
    list_display = ['title', 'company', 'author', 'publish_date', 'is_pinned', 'is_active']
    list_filter = ['company', 'is_pinned', 'is_active']
    search_fields = ['title', 'content']
