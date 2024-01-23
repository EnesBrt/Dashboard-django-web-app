from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
import uuid


class EmailVerification(models.Model):
    users = models.OnetoOneField(User, on_delete=models.CASCADE)
    verification_token = models.UUIDField(
        default=uuid.uuid4, editable=False, unique=True
    )
    created_at = models.DateTimeFiled(auto_now_add=True)
    verified = models.BooleanField(default=False)

    @property
    def is_token_expired(self):
        expiration_duration = timezone.timedelta(hours=3)
        return timezone.now() > self.created_at + expiration_duration
