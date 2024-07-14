import os

from rest_framework import serializers

from suppliers.models import Supplier, SupplierContract, Order


class SupplierSerializer(serializers.ModelSerializer):
    class Meta:
        model = Supplier
        fields = ['supplier_id', 'supplier_name', 'supplier_address', 'supplier_phone', 'supplier_email', 'supplier_website']
        read_only_fields = ['supplier_id']


class SupplierContractSerializer(serializers.ModelSerializer):
    supplier_id = serializers.UUIDField()

    class Meta:
        model = SupplierContract
        fields = ['supplier_id', 'date_contracted', 'contract_end_date']

    def validate_supplier_id(self, value):
        # Access the context passed during serialization
        request = self.context["request"]
        business_id = request.data["business_id"]
        db_name = f"{business_id}{os.getenv('DB_NAME_SECONDARY')}"
        if not db_name:
            raise serializers.ValidationError("Database name not provided.")

        try:
            supplier = Supplier.objects.using(db_name).get(supplier_id=value)
        except Supplier.DoesNotExist:
            raise serializers.ValidationError("Supplier does not exist in the specified business database.")

        return supplier


class OrderSerializer(serializers.ModelSerializer):
    supplier_id = serializers.UUIDField(write_only=True)
    supplier = serializers.PrimaryKeyRelatedField(read_only=True)

    class Meta:
        model = Order
        fields = [
            'supplier_id', 'supplier', 'date_ordered', 'delivery_date',
            'amount_ordered', 'amount_paid', 'order_status', 'amount_due_date'
        ]

    def validate_supplier_id(self, value):
        request = self.context["request"]
        business_id = request.data.get("business_id")
        if not business_id:
            raise serializers.ValidationError("Business ID is required.")

        db_name = f"{business_id}{os.getenv('DB_NAME_SECONDARY')}"
        if not db_name:
            raise serializers.ValidationError("Database name not provided.")

        try:
            supplier = Supplier.objects.using(db_name).get(supplier_id=value)
        except Supplier.DoesNotExist:
            raise serializers.ValidationError("Supplier does not exist in the specified business database.")

        return supplier

