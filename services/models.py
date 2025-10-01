# models.py
from django.db import models
from django.contrib.auth.models import User
from services.utils.encryption_service import encryption_service

class ThirdPartyService(models.Model):
    name = models.CharField(max_length=100)
    api_endpoint = models.URLField()
    api_key = models.TextField()  # Untuk encrypted data
    rate_limit_per_hour = models.IntegerField(default=100)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def set_api_key(self, plain_text_key):
        """Encrypt dan simpan API key"""
        self.api_key = encryption_service.encrypt(plain_text_key)

    def get_api_key(self):
        """Decrypt dan return API key"""
        return encryption_service.decrypt(self.api_key)

    def save(self, *args, **kwargs):
        """Pastikan API key selalu diencrypt sebelum save"""
        # Check if the api_key is already encrypted
        try:
            encryption_service.decrypt(self.api_key)
        except Exception:
            self.set_api_key(self.api_key)
        super().save(*args, **kwargs)

class APIRequestLog(models.Model):
    service = models.ForeignKey(ThirdPartyService, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    endpoint_called = models.CharField(max_length=255)
    response_status = models.IntegerField()
    response_time_ms = models.IntegerField()
    timestamp = models.DateTimeField(auto_now_add=True)
    cached = models.BooleanField(default=False)

    class Meta:
        indexes = [
            models.Index(fields=['service', 'timestamp']),
            models.Index(fields=['user', 'timestamp']),
        ]

class CacheMetadata(models.Model):
    cache_key = models.CharField(max_length=255, unique=True)
    service_name = models.CharField(max_length=100)
    data = models.JSONField()
    expires_at = models.DateTimeField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        indexes = [
            models.Index(fields=['cache_key']),
            models.Index(fields=['expires_at']),
        ]
