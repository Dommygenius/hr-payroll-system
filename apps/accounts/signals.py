from django.db.models.signals import post_save
from django.dispatch import receiver

from apps.accounts.models import User


@receiver(post_save, sender=User)
def set_password_change_date(sender, instance, created, **kwargs):
    if created:
        from django.utils import timezone
        User.objects.filter(pk=instance.pk).update(last_password_change=timezone.now())
