import os

from rest_framework import serializers

from Utils.Database.Database_Routing.add_database import add_database
from billing.models import Invoice, InvoiceItem, Customer
from inventory.models import Category, Item


class InvoiceSerializers(serializers.ModelSerializer):
    created_by = serializers.UUIDField()
    customer = serializers.UUIDField()

    class Meta:
        model = Invoice
        fields = [
            'invoice_id',
            'date_and_time',
            'amount',
            'created_by',
            'invoice_status',
            'customer'
        ]
        read_only_fields = ['invoice_id']

    def validate_customer(self, value):
        request = self.context
        business_id = request.data.get('business_id')
        if not business_id:
            raise serializers.ValidationError("No business id provided")

        db_name = f"{business_id}{os.getenv('DB_NAME_SECONDARY')}"
        add_database(db_name)

        try:
            customer = Customer.objects.using(db_name).get(customer_id=value)
        except Customer.DoesNotExist:
            raise serializers.ValidationError("Customer not found")
        except Exception as e:
            raise serializers.ValidationError(str(e))
        return customer


class InvoiceItemSerializers(serializers.ModelSerializer):
    invoice = serializers.UUIDField()
    category = serializers.IntegerField()
    item = serializers.IntegerField()

    class Meta:
        model = InvoiceItem
        fields = [
            'invoice',
            'category',
            'item',
            'price',
            'quantity'
        ]

    def validate_invoice(self, invoice):
        request = self.context
        business_id = request.data.get('business_id')
        if not business_id:
            raise serializers.ValidationError("No business id provided")

        db_name = f"{business_id}{os.getenv('DB_NAME_SECONDARY')}"
        add_database(db_name)

        try:
            invoice = Invoice.objects.using(db_name).get(pk=invoice)
        except Invoice.DoesNotExist:
            raise serializers.ValidationError("Invoice not found")
        except Exception as e:
            raise serializers.ValidationError(str(e))
        return invoice

    def validate_category(self, category):
        request = self.context
        business_id = request.data.get('business_id')
        if not business_id:
            raise serializers.ValidationError("No business id provided")

        db_name = f"{business_id}{os.getenv('DB_NAME_SECONDARY')}"
        add_database(db_name)

        try:
            category = Category.objects.using(db_name).get(pk=category)
        except Category.DoesNotExist:
            raise serializers.ValidationError("Category not found")
        except Exception as e:
            raise serializers.ValidationError(str(e))
        return category

    def validate_item(self, item):
        request = self.context
        business_id = request.data.get('business_id')
        if not business_id:
            raise serializers.ValidationError("No business id provided")

        db_name = f"{business_id}{os.getenv('DB_NAME_SECONDARY')}"
        add_database(db_name)

        try:
            item = Item.objects.using(db_name).get(pk=item)
        except Item.DoesNotExist:
            raise serializers.ValidationError("Item not found")
        except Exception as e:
            raise serializers.ValidationError(str(e))
        return item


class CustomerSerializers(serializers.ModelSerializer):
    class Meta:
        model = Customer
        fields = [
            'customer_id',
            'name',
            'address',
            'phone',
            'points',
            'created_by',
            'created_at'
        ]
        read_only_fields = ('customer_id',)
