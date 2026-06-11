from django.contrib.auth.models import AbstractUser
from django.db import models


class CustomUser(AbstractUser):
    BASIC = "basic"
    PRO = "pro"

    ROLE_CHOICES = [
        (BASIC, "Basic"),
        (PRO, "Pro"),
    ]

    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default=BASIC)

    def __str__(self):
        return f"{self.username} ({self.role})"