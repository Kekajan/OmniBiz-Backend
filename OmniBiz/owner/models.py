from django.db import models
from django.contrib.auth.models import User

from Utils.Common.RandomId import RandomId
from django.conf import settings


class Owner(models.Model):
    owner_id = models.CharField(max_length=100, unique=True, primary_key=True)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    phone_number = models.CharField(max_length=100)
    business_count = models.IntegerField(default=0)
    profit = models.IntegerField(default=0)
    subscription_amount = models.IntegerField(default=0)

    def save(self, *args, **kwargs):
        if not self.owner_id:
            self.owner_id = RandomId.generate_id(self, 'owner_id', 8)
        super(Owner, self).save(*args, **kwargs)

    def __str__(self):
        return self.owner_id
