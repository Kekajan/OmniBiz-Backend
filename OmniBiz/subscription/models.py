from django.db import models
from authentication.models import User
from business.models import Business


class PaymentCard(models.Model):
    id = models.AutoField(primary_key=True)
    card_holder = models.ForeignKey(User, on_delete=models.CASCADE)
    card_holder_name = models.CharField(max_length=50, blank=True, null=True)
    card_number = models.CharField(max_length=50, blank=True, null=True)
    card_expiry_date = models.DateField(blank=True, null=True)
    auto_renew = models.BooleanField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.card_holder_name


class Subscription(models.Model):
    STATUS_CHOICES = [
        ('active', 'Active'),
        ('cancelled', 'Cancelled'),
        ('expired', 'Expired'),
    ]

    id = models.AutoField(primary_key=True)
    owner = models.ForeignKey(User, on_delete=models.CASCADE)
    business = models.ForeignKey(Business, on_delete=models.CASCADE)
    start_date = models.DateTimeField(auto_now_add=True)
    end_date = models.DateTimeField(null=True, blank=True)
    status = models.CharField(max_length=50, choices=STATUS_CHOICES, default='active')
    auto_renew = models.BooleanField(blank=True, null=True)
    next_billing_date = models.DateTimeField(blank=True, null=True)
    payment_cards = models.ForeignKey(PaymentCard, on_delete=models.CASCADE, blank=True, null=True)
    amount = models.FloatField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.business.business_name
