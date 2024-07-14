import uuid

from django.db import models


# Create your models here.
class CashBook(models.Model):
    TRANSACTION_CHOICES = (
        ('income', 'Income'),
        ('expense', 'Expense'),
    )
    transaction_id = models.AutoField(primary_key=True)
    transaction_time = models.DateTimeField(auto_now_add=True)
    transaction_type = models.CharField(max_length=100, choices=TRANSACTION_CHOICES)
    transaction_amount = models.FloatField()
    balance = models.FloatField()
    description = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.CharField(max_length=100)

    def __str__(self):
        return self.description
