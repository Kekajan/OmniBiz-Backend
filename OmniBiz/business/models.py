from django.contrib.auth.models import User
from django.db import models
from django.conf import settings

from Utils.Common.RandomId import RandomId


# Create your models here.

class Business(models.Model):
    business_id = models.CharField(max_length=100, unique=True, primary_key=True)
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    business_name = models.CharField(max_length=100)
    business_address = models.CharField(max_length=255)
    phone_number = models.CharField(max_length=100)
    logo = models.CharField(max_length=255)
    initial = models.FloatField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    daily_revenue = models.FloatField(default=0)
    subscription_trial_ended_at = models.DateTimeField()
    subscription_amount = models.FloatField(default=0)
    subscription_started_at = models.DateTimeField(null=True)
    subscription_ended_at = models.DateTimeField(null=True)
    subscription_count = models.IntegerField(default=0)
    is_active = models.BooleanField(default=True)

    def save(self, *args, **kwargs):
        if not self.business_id:
            self.business_id = RandomId.generate_id(self, 'business_id', 8)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.business_name
