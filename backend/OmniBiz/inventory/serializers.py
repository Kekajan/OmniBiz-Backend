import os

from django.core.exceptions import ObjectDoesNotExist
from rest_framework import serializers

from Utils.Database.Database_Routing.add_database import add_database
from inventory.models import Category, Item, Inventory
from suppliers.models import Supplier


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['category_id', 'name', 'description', 'created_by']
        read_only_fields = ['category_id']


class ItemSerializer(serializers.ModelSerializer):
    category_id = serializers.UUIDField()

    class Meta:
        model = Item
        fields = [
            'item_id', 'name', 'category_id', 'description', 'unit_price',
            'quantity_type', 'stock_alert', 'restock_level',
            'created_at', 'created_by'
        ]
        read_only_fields = ['item_id']

    def validate_category_id(self, value):
        request = self.context.get("request")
        business_id = request.data.get("business_id")
        db_name = f"{business_id}{os.getenv('DB_NAME_SECONDARY')}"
        if not business_id:
            raise serializers.ValidationError({'error': 'No business id'})

        try:
            category = Category.objects.using(db_name).get(category_id=value)
        except Category.DoesNotExist:
            raise serializers.ValidationError("Category does not exist in the specified business database.")

        return category.category_id


# Corrected InventorySerializer
class InventorySerializer(serializers.ModelSerializer):
    category = serializers.UUIDField()
    item = serializers.UUIDField()
    suppliers = serializers.UUIDField()

    class Meta:
        model = Inventory
        fields = [
            'item', 'category', 'quantity', 'buying_price', 'selling_price',
            'suppliers', 'created_by', 'created_at'
        ]

    def validate_category(self, value):
        request = self.context.get("request")
        business_id = request.data.get("business_id")
        if not business_id:
            raise serializers.ValidationError('No business id')

        db_name = f"{business_id}{os.getenv('DB_NAME_SECONDARY')}"
        try:
            category = Category.objects.using(db_name).get(category_id=value)
        except Category.DoesNotExist:
            raise serializers.ValidationError("Category does not exist in the specified business database.")

        return category

    def validate_item(self, value):
        request = self.context.get("request")
        business_id = request.data.get("business_id")
        if not business_id:
            raise serializers.ValidationError('No business id')

        db_name = f"{business_id}{os.getenv('DB_NAME_SECONDARY')}"
        try:
            item = Item.objects.using(db_name).get(item_id=value)
        except Item.DoesNotExist:
            raise serializers.ValidationError("Item does not exist in the specified business database.")

        return item

    def validate_suppliers(self, value):
        request = self.context.get("request")
        business_id = request.data.get("business_id")
        if not business_id:
            raise serializers.ValidationError('No business id')

        db_name = f"{business_id}{os.getenv('DB_NAME_SECONDARY')}"
        try:
            suppliers = Supplier.objects.using(db_name).get(supplier_id=value)
        except Supplier.DoesNotExist:
            raise serializers.ValidationError("Supplier does not exist in the specified business database.")

        return suppliers
