from django.contrib.auth.models import User
from django.db import models
from rest_framework_api_key.models import AbstractAPIKey

class UserAPIKey(AbstractAPIKey):
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='api_key'
    )
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} - {self.name}"
