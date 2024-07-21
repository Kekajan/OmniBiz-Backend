from django.db import models

from suppliers.models import Supplier


# Create your models here.
class Category(models.Model):
    category_id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=100)
    description = models.TextField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.CharField(max_length=100)
    show_status = models.BooleanField(default=True)

    def __str__(self):
        return self.name


class Item(models.Model):
    STOCK_AVAILABLE_CHOICES = (
        ('available', 'Available'),
        ('unavailable', 'Unavailable'),
        ('low', 'Low')
    )
    item_id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=100)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    description = models.TextField(null=True, blank=True)
    unit_price = models.DecimalField(default=0.00, max_digits=15, decimal_places=2)
    stock = models.IntegerField(default=0)
    quantity_type = models.CharField(max_length=50, default=None)
    stock_alert = models.BooleanField(default=True)
    stock_alert_available = models.CharField(max_length=30, default='available', choices=STOCK_AVAILABLE_CHOICES)
    restock_level = models.PositiveIntegerField(help_text="Alert when stock falls below this level")
    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.CharField(max_length=100)
    updated_at = models.DateTimeField(null=True)
    updated_by = models.CharField(max_length=100, null=True)
    show_status = models.BooleanField(default=True)

    def __str__(self):
        return self.name

    def is_stock_low(self):
        return self.stock < self.restock_level


class Inventory(models.Model):
    inventory_id = models.AutoField(primary_key=True)
    suppliers = models.ForeignKey(Supplier, null=True, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True, null=True)
    created_by = models.CharField(max_length=100, null=True)


class InventoryItem(models.Model):
    inventory_item_id = models.AutoField(primary_key=True)
    item = models.ForeignKey(Item, on_delete=models.CASCADE)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    quantity = models.IntegerField(default=0)
    buying_price = models.DecimalField(max_digits=20, decimal_places=2)
    selling_price = models.DecimalField(max_digits=20, decimal_places=2)
