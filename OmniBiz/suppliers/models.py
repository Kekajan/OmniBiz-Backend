import uuid

from django.db import models


# Create your models here.
class Supplier(models.Model):
    supplier_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    supplier_name = models.CharField(max_length=100)
    supplier_address = models.CharField(max_length=100)
    supplier_phone = models.CharField(max_length=100)
    supplier_email = models.CharField(max_length=100)
    supplier_website = models.CharField(max_length=100)
    show_status = models.BooleanField(default=True)


class SupplierContract(models.Model):
    contract_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    supplier_id = models.ForeignKey(Supplier, on_delete=models.CASCADE)
    date_contracted = models.DateTimeField(auto_now_add=True)
    contract_end_date = models.DateTimeField(null=True, default=None)

    def __str__(self):
        return str(self.supplier_id)


class Order(models.Model):
    order_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    supplier_id = models.ForeignKey(Supplier, on_delete=models.CASCADE)
    date_ordered = models.DateTimeField(auto_now_add=True)
    delivery_date = models.DateTimeField(null=True, default=None)
    amount_ordered = models.DecimalField(max_digits=10, decimal_places=2, null=True, default=None)
    amount_paid = models.DecimalField(max_digits=10, decimal_places=2, null=True, default=None)
    amount_due_date = models.DateTimeField(null=True, default=None)
    order_status = models.CharField(max_length=100, null=True, default=None)

    def __str__(self):
        return str(self.order_id)

