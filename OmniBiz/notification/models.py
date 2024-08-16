from django.db import models

from authentication.models import User
from business.models import Business


# Create your models here.
class Notification(models.Model):
    id = models.AutoField(primary_key=True)
    type = models.CharField(max_length=255)
    message = models.TextField()
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    target = models.CharField(max_length=255, null=True, blank=True)
    target_id = models.CharField(max_length=255, null=True, blank=True)

    def __str__(self):
        return self.message

