import uuid

from django.db import models

from inventory.models import Category, Item


# Create your models here.
class Customer(models.Model):
    customer_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255)
    address = models.CharField(max_length=255)
    phone = models.CharField(unique=True, max_length=255)
    points = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    created_at = models.DateTimeField(auto_now_add=True, null=True)
    created_by = models.CharField(max_length=255, null=True)

    def __str__(self):
        return self.name


class Invoice(models.Model):
    INVOICE_STATUS_CHOICES = (
        ('draft', 'Draft'),
        ('paid', 'Paid'),
        ('checked', 'Checked'),
    )
    invoice_id = models.UUIDField(default=uuid.uuid4, editable=False, unique=True, primary_key=True)
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, blank=True, null=True)
    date_and_time = models.DateTimeField(auto_now_add=True)
    amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    created_by = models.CharField(max_length=255)
    invoice_status = models.CharField(max_length=255)
    checked_by = models.CharField(max_length=255, null=True, blank=True)
    checked_on = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return str(self.invoice_id)


class InvoiceItem(models.Model):
    sales_id = models.UUIDField(default=uuid.uuid4, editable=False, unique=True, primary_key=True)
    invoice = models.ForeignKey(Invoice, on_delete=models.CASCADE)
    category = models.ForeignKey(Category, default=None, null=True, on_delete=models.CASCADE)
    item = models.ForeignKey(Item, default=None, null=True, on_delete=models.CASCADE)
    price = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    quantity = models.IntegerField(default=0)

    def __str__(self):
        return str(self.sales_id)
