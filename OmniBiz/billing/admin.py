from django.contrib import admin

from billing.models import Invoice, InvoiceItem

# Register your models here.
admin.site.register(Invoice)
admin.site.register(InvoiceItem)
