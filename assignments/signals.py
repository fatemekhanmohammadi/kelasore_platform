from django.core.mail import send_mail
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.conf import settings

from .models import Assignment
from classes.models import MemberShip

#================================================================================================

@receiver(post_save, sender=Assignment)
def send_assignment_email(sender, instance, created, **kwargs):
    classroom = instance.classroom
    members = MemberShip.objects.filter(classroom=classroom).select_related("user")

    emails = [
        member.user.email
        for member in members
        if member.user.email]
    if not emails:
        return
    if created:
        subject = f"تمرین جدید در کلاس {classroom.title}"
        message = (
            f"یک تمرین جدید با عنوان '{instance.title}' "
            f"در کلاس {classroom.title} ایجاد شده است.")
    else:
        subject = f"بروزرسانی تمرین در کلاس {classroom.title}"
        message = (
            f"تمرین '{instance.title}' "
            f"در کلاس {classroom.title} بروزرسانی شد.")

    send_mail(subject=subject,message=message,from_email=settings.EMAIL_HOST_USER,recipient_list=emails,fail_silently=False,)


#================================================================================================
