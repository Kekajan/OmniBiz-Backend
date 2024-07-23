from django.contrib import admin

from inventory.models import Category, Item, Inventory

# Register your models here.
admin.site.register(Category)
admin.site.register(Item)
admin.site.register(Inventory)
