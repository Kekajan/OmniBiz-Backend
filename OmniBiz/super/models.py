
from django.db import models
from django.utils import timezone


# Create your models here.
class Super(models.Model):
    id = models.AutoField(primary_key=True)
    permission = models.CharField(max_length=255, unique=True)
    description = models.CharField(max_length=255, null=True)
    created_by = models.CharField(max_length=255, null=True)
    created_at = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return self.permission
