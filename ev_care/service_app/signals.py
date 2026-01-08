from django.db.models.signals import pre_save, post_save
from django.dispatch import receiver
from django.core.mail import send_mail
from django.conf import settings

from user_app.models import EVService


@receiver(pre_save, sender=EVService)
def cache_old_status(sender, instance, **kwargs):
    if instance.pk:
        try:
            old = EVService.objects.get(pk=instance.pk)
            instance._old_status = old.status
        except EVService.DoesNotExist:
            instance._old_status = None
    else:
        instance._old_status = None


@receiver(post_save, sender=EVService)
def send_service_completed_mail(sender, instance, created, **kwargs):
    old_status = getattr(instance, "_old_status", None)

    if old_status != "completed" and instance.status == "completed":
        send_mail(
            subject="Your vehicle service is completed 🚗",
            message=(
                f"Hello {instance.user.username},\n\n"
                f"Your vehicle service ({instance.get_category_display()}) "
                f"has been successfully completed.\n"
                f"You can now visit the service center and take your car.\n\n"
                f"Thank you for choosing EV Care."
            ),
            from_email=settings.EMAIL_HOST_USER,
            recipient_list=[instance.user.email],
            fail_silently=False,
        )
