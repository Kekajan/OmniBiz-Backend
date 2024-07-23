from django.contrib import admin

from suppliers.models import Supplier, SupplierContract, Order

# Register your models here.
admin.site.register(Supplier)
admin.site.register(SupplierContract)
admin.site.register(Order)
