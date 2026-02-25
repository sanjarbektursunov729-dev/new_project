# projects/signals.py
from django.db.models.signals import pre_delete
from django.dispatch import receiver
from apps.accounts.models import User
from .models import Project

@receiver(pre_delete, sender=User)
def keep_projects_when_admin_deleted(sender, instance: User, **kwargs):
    # Superadmindan boshqa userlar (kichik adminlar) o‘chsa ham projectlar qolsin
    if instance.role != User.Role.SUPERADMIN:
        display = (instance.get_full_name() or instance.username or "").strip()

        # author SET_NULL bo‘ladi, lekin o‘chirishdan oldin author_name ni saqlab qo‘yamiz
        Project.objects.filter(author=instance).update(author_name=display)