import os

from django.shortcuts import render
from rest_framework import generics, status
from rest_framework.permissions import IsAuthenticated

from Utils.Database.Database_Routing.add_database import add_database
from cash_book.views import create_cash_book_entry
from inventory.serializers import CategorySerializer, ItemSerializer, InventorySerializer
from rest_framework.response import Response
from inventory.models import Category, Item, Inventory
from datetime import datetime


# Create your views here.
class CreateCategoryView(generics.CreateAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = CategorySerializer

    def create(self, request, *args, **kwargs):
        business_id = request.data['business_id']
        user = request.user
        user_id = user.user_id
        db_name = f"{business_id}{os.getenv('DB_NAME_SECONDARY')}"
        add_database(db_name)
        category = {
            'name': request.data['name'],
            'description': request.data['description'],
            'created_by': str(user_id),
        }

        serializer = self.serializer_class(data=category)
        if serializer.is_valid():
            category = Category.objects.using(db_name).create(**category)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class CategoryListView(generics.ListAPIView):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        business_id = kwargs.get('business_id')
        if not business_id:
            return Response({'message': 'Business id is required'}, status=status.HTTP_400_BAD_REQUEST)
        db_name = f"{business_id}{os.getenv('DB_NAME_SECONDARY')}"
        add_database(db_name)

        try:
            category = Category.objects.using(db_name).filter(show_status=1)
            serializer = CategorySerializer(category, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Category.DoesNotExist:
            return Response({'message': 'Category does not exist'}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({'message': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class DeleteCategoryView(generics.UpdateAPIView):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [IsAuthenticated]

    def put(self, request, *args, **kwargs):
        business_id = kwargs.get('business_id')
        category_id = kwargs.get('category_id')
        if not business_id:
            return Response({'message': 'Busine id is required'}, status=status.HTTP_400_BAD_REQUEST)
        if not category_id:
            return Response({'message': 'Category id is required'}, status=status.HTTP_400_BAD_REQUEST)
        db_name = f"{business_id}{os.getenv('DB_NAME_SECONDARY')}"
        add_database(db_name)

        try:
            category = Category.objects.using(db_name).get(category_id=category_id)
            category.show_status = 0
            category.save()
            return Response({'message': 'Category has been deleted'}, status=status.HTTP_200_OK)
        except Category.DoesNotExist:
            return Response({'message': 'Category does not exist'}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({'message': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class CreateItemView(generics.CreateAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = ItemSerializer

    def post(self, request, *args, **kwargs):
        business_id = request.data.get('business_id')
        if not business_id:
            return Response({"error": "business_id is required"}, status=status.HTTP_400_BAD_REQUEST)

        # Dynamic database name
        db_name = f"{business_id}{os.getenv('DB_NAME_SECONDARY')}"

        # Ensure the dynamic database is added to the configuration
        add_database(db_name)
        # Data for creating the item
        item_data = {
            'name': request.data.get('name'),
            'category_id': request.data.get('category_id'),
            'description': request.data.get('description'),
            'unit_price': request.data.get('unit_price'),
            'quantity_type': request.data.get('quantity_type'),
            'stock_alert': request.data.get('stock_alert'),
            'restock_level': request.data.get('restock_level'),
            'created_at': datetime.now(),
            'created_by': str(request.user.user_id)
        }

        # Serializer for validation
        serializer = self.get_serializer(data=item_data)
        serializer.is_valid(raise_exception=True)

        # Create item in the dynamic database
        try:
            Item.objects.using(db_name).create(**serializer.validated_data)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class UpdateItemView(generics.UpdateAPIView):
    queryset = Item.objects.all()
    serializer_class = ItemSerializer
    permission_classes = [IsAuthenticated]

    def put(self, request, *args, **kwargs):
        business_id = kwargs.get('business_id')
        item_id = kwargs.get('item_id')
        if not business_id:
            return Response({"error": "business_id is required"}, status=status.HTTP_400_BAD_REQUEST)
        if not item_id:
            return Response({"error": "item_id is required"}, status=status.HTTP_400_BAD_REQUEST)

        db_name = f"{business_id}{os.getenv('DB_NAME_SECONDARY')}"
        add_database(db_name)

        try:
            item = Item.objects.using(db_name).get(item_id=item_id)
            data = request.data.copy()
            data['created_by'] = item.created_by
            serializer = ItemSerializer(item, data=data, context={'request': request})
            print('item passed to serializer')
            if serializer.is_valid():
                print('serializer is valid')
                serializer.save()
                return Response(serializer.data, status=status.HTTP_200_OK)
            else:
                print('serializer errors:', serializer.errors)
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except Item.DoesNotExist:
            return Response({"error": "Item does not exist"}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class ItemListView(generics.ListAPIView):
    queryset = Item.objects.all()
    serializer_class = ItemSerializer
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        business_id = kwargs.get('business_id')
        if not business_id:
            return Response({"error": "business_id is required"}, status=status.HTTP_400_BAD_REQUEST)
        db_name = f"{business_id}{os.getenv('DB_NAME_SECONDARY')}"
        add_database(db_name)

        try:
            items = Item.objects.using(db_name).filter(show_status=1)
            serializer = ItemSerializer(items, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Item.DoesNotExist:
            return Response({"error": "Item does not exist"}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class DeleteItemView(generics.UpdateAPIView):
    permission_classes = [IsAuthenticated]

    def put(self, request, *args, **kwargs):
        business_id = kwargs.get('business_id')
        item_id = kwargs.get('item_id')
        if not business_id:
            return Response({"error": "business_id is required"}, status=status.HTTP_400_BAD_REQUEST)
        if not item_id:
            return Response({"error": "item_id is required"}, status=status.HTTP_400_BAD_REQUEST)
        db_name = f"{business_id}{os.getenv('DB_NAME_SECONDARY')}"
        add_database(db_name)

        try:
            item = Item.objects.using(db_name).get(item_id=item_id)
            item.show_status = 0
            item.save()
            return Response({'message': 'Item has been deleted'}, status=status.HTTP_200_OK)
        except Item.DoesNotExist:
            return Response({"error": "Item does not exist"}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class CreateInventoryView(generics.CreateAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = InventorySerializer

    def create(self, request, *args, **kwargs):
        business_id = request.data.get('business_id')
        user = request.user
        if not business_id:
            return Response({"error": "business_id is required"}, status=status.HTTP_400_BAD_REQUEST)

        db_name = f"{business_id}{os.getenv('DB_NAME_SECONDARY')}"
        add_database(db_name)

        inventory_data = {
            'item': int(request.data.get('item')),
            'category': int(request.data.get('category')),
            'quantity': request.data.get('quantity'),
            'buying_price': request.data.get('buying_price'),
            'selling_price': request.data.get('selling_price'),
            'suppliers': request.data.get('suppliers'),
            'created_by': str(user.user_id),
            'created_at': datetime.now(),
        }

        serializer = self.get_serializer(data=inventory_data, context={'request': request})
        serializer.is_valid(raise_exception=True)

        try:
            inventory = Inventory.objects.using(db_name).create(**serializer.validated_data)
            change_stock_quantity_status = change_stock_quantity('increase', business_id, inventory.item_id, inventory.quantity)
            cash_book_data = {
                'business_id': business_id,
                'transaction_amount': inventory.quantity * inventory.buying_price,
                'transaction_type': 'expense',
                'description': f'buying Inventory {inventory.inventory_id}',
                'created_by': str(user.user_id),
            }
            cash_book_response = create_cash_book_entry(cash_book_data)
            if change_stock_quantity_status and cash_book_response.status_code == 201:
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            else:
                inventory.delete()
                return Response(serializer.data, status=status.HTTP_204_NO_CONTENT)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class InventoryListView(generics.ListAPIView):
    serializer_class = InventorySerializer
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        business_id = kwargs.get('business_id')
        if not business_id:
            return Response({"error": "business_id is required"}, status=status.HTTP_400_BAD_REQUEST)
        db_name = f"{business_id}{os.getenv('DB_NAME_SECONDARY')}"
        add_database(db_name)

        try:
            inventories = Inventory.objects.using(db_name).all()
            serializer = InventorySerializer(inventories, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Inventory.DoesNotExist:
            return Response({"error": "Inventory does not exist"}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


def change_stock_quantity(action, business_id, item_id, stock_quantity):
    if not business_id:
        response = Response({"error": "business_id is required"}, status=status.HTTP_400_BAD_REQUEST)
        print(response)
        return False
    if not item_id:
        response = Response({"error": "item_id is required"}, status=status.HTTP_400_BAD_REQUEST)
        print(response)
        return False
    if stock_quantity is None:
        response = Response({"error": "stock_quantity is required"}, status=status.HTTP_400_BAD_REQUEST)
        print(response)
        return False
    if not action:
        response = Response({"error": "action is required"}, status=status.HTTP_400_BAD_REQUEST)
        print(response)
        return False

    db_name = f"{business_id}{os.getenv('DB_NAME_SECONDARY')}"
    add_database(db_name)
    try:
        item = Item.objects.using(db_name).get(item_id=item_id)
        if action == 'increase':
            item.stock += stock_quantity
            item.save()
            response = Response({"success": "Stock increased successfully"}, status=status.HTTP_200_OK)
            print(response)
            return True
        elif action == 'decrease':
            if item.stock < stock_quantity:
                response = Response({"error": "Not enough stock to decrease"}, status=status.HTTP_400_BAD_REQUEST)
                print(response)
                return False
            item.stock -= stock_quantity
            item.save()
            response = Response({"success": "Stock decreased successfully"}, status=status.HTTP_200_OK)
            print(response)
            return True
        else:
            response = Response({"error": "Invalid action"}, status=status.HTTP_400_BAD_REQUEST)
            print(response)
            return False
    except Item.DoesNotExist:
        response = Response({"error": "Item does not exist"}, status=status.HTTP_404_NOT_FOUND)
        print(response)
        return False
    except Exception as e:
        print(e)
        response = Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        print(response)
        return False
