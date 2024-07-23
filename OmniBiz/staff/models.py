from django.utils import timezone

from django.contrib.auth.models import User
from django.db import models

from Utils.Common.RandomId import RandomId
from business.models import Business


class Staff(models.Model):
    staff_id = models.CharField(primary_key=True, max_length=20)
    user_id = models.CharField(max_length=100)
    business_id = models.CharField(max_length=30)
    firstname = models.CharField(max_length=100, null=True, blank=True)
    lastname = models.CharField(max_length=100, null=True, blank=True)
    role_name = models.CharField(max_length=100, null=True, blank=True)
    updated_at = models.DateTimeField(default=None, null=True)
    is_active = models.BooleanField(default=False)
    created_by = models.CharField(max_length=100, null=True, blank=True)
    created_at = models.DateTimeField(default=timezone.now)

    def save(self, *args, **kwargs):
        if not self.staff_id:
            self.staff_id = RandomId.generate_id(self, 'staff_id', 8, using=kwargs.get('using'))
        super(Staff, self).save(*args, **kwargs)

    def __str__(self):
        return f'{self.firstname} {self.lastname} is {self.role_name}'


