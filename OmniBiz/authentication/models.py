from django.contrib.auth.models import AbstractUser, Group, Permission
from django.db import models
import uuid

from business.models import Business
from super.models import Super


class User(AbstractUser):
    ROLE_CHOICES = (
        ('admin', 'Admin'),
        ('staff', 'Staff'),
        ('owner', 'Owner'),
        ('higher-staff', 'Higher-Staff'),
    )
    role = models.CharField(max_length=30, choices=ROLE_CHOICES, default='owner')
    token = models.CharField('Token', max_length=255, default=000000000000000)
    user_id = models.UUIDField(default=uuid.uuid4, editable=False, unique=True, primary_key=True)
    business_id = models.CharField(null=True, blank=True, max_length=255)

    groups = models.ManyToManyField(
        Group,
        related_name='custom_user_set',
        blank=True,
        help_text=('The groups this user belongs to. A user will get all permissions '
                   'granted to each of their groups.'),
        related_query_name='user',
    )
    user_permissions = models.ManyToManyField(
        Permission,
        related_name='custom_user_set',
        blank=True,
        help_text='Specific permissions for this user.',
        related_query_name='user',
    )

    def __str__(self):
        return self.username


class HigherStaffUser(models.Model):
    staff_id = models.UUIDField(default=uuid.uuid4, editable=False, unique=True, primary_key=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    first_name = models.CharField(max_length=255)
    last_name = models.CharField(max_length=255)
    email = models.EmailField()
    phone_number = models.CharField(max_length=255)
    address = models.CharField(max_length=255)
    status = models.CharField(max_length=255)
    created_by = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(default=None, null=True)

    def __str__(self):
        return self.first_name


class StaffAccess(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    permission = models.CharField(max_length=255)

    def __str__(self):
        return str(self.user)


class HigherStaffAccess(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    business = models.ForeignKey(Business, on_delete=models.CASCADE)
    provided_date = models.DateTimeField(auto_now_add=True)
    status = models.BooleanField(default=True)

    def __str__(self):
        return str(self.user)
