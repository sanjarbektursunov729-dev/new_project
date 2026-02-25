from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    class Role(models.TextChoices):
        SUPERADMIN = "SUPERADMIN", "Superadmin"
        ADMIN = "ADMIN", "Kichik admin"
        USER = "USER", "User"

    role = models.CharField(max_length=20, choices=Role.choices, default=Role.USER)

    created_by = models.ForeignKey(
        "self",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="created_users",
        limit_choices_to={"role": "SUPERADMIN"},
    )

    def is_superadmin(self) -> bool:
        return self.role == self.Role.SUPERADMIN

    def is_admin(self) -> bool:
        return self.role == self.Role.ADMIN
