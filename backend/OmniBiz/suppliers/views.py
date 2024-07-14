import os
from datetime import timedelta

from django.db import transaction
from django.utils import timezone

from django.shortcuts import render
from rest_framework import generics, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from datetime import datetime

from Utils.Database.Database_Routing.add_database import add_database
from cash_book.views import create_cash_book_entry
from suppliers.models import Supplier, SupplierContract, Order
from suppliers.serializers import SupplierSerializer, SupplierContractSerializer, OrderSerializer


# Create your views here.
class CreateSuppliersView(generics.CreateAPIView):
    serializer_class = SupplierSerializer
    permission_classes = [IsAuthenticated]

    def create(self, request, *args, **kwargs):
        business_id = request.data.get('business_id')
        if not business_id:
            return Response({"error": "business_id is required"}, status=status.HTTP_400_BAD_REQUEST)

        db_name = f"{business_id}{os.getenv('DB_NAME_SECONDARY')}"
        add_database(db_name)

        # Extract supplier data from request
        supplier_data = {
            'supplier_name': request.data.get('supplier_name'),
            'supplier_address': request.data.get('supplier_address'),
            'supplier_phone': request.data.get('supplier_phone'),
            'supplier_email': request.data.get('supplier_email'),
            'supplier_website': request.data.get('supplier_website')
        }

        serializer = self.get_serializer(data=supplier_data)
        serializer.is_valid(raise_exception=True)
        supplier = Supplier.objects.using(db_name).create(**serializer.validated_data)

        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)


class ListSuppliersView(generics.ListAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = SupplierSerializer

    def get(self, request, *args, **kwargs):
        business_id = kwargs.get('business_id')
        if not business_id:
            return Response({"error": "business_id is required"}, status=status.HTTP_400_BAD_REQUEST)

        db_name = f"{business_id}{os.getenv('DB_NAME_SECONDARY')}"
        add_database(db_name)
        try:
            suppliers = Supplier.objects.using(db_name).all()
            serializer = SupplierSerializer(suppliers, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Supplier.DoesNotExist:
            return Response({"error": "Supplier does not exist"}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)


class UpdateSuppliersView(generics.UpdateAPIView):
    serializer_class = SupplierSerializer
    permission_classes = [IsAuthenticated]
    lookup_field = 'pk'

    def update(self, request, *args, **kwargs):
        supplier_id = kwargs.get('supplier_id')
        business_id = request.data.get('business_id')

        if not business_id:
            return Response({"error": "business_id is required"}, status=status.HTTP_400_BAD_REQUEST)

        db_name = f"{business_id}{os.getenv('DB_NAME_SECONDARY')}"
        add_database(db_name)

        try:
            supplier = Supplier.objects.using(db_name).get(pk=supplier_id)
        except Supplier.DoesNotExist:
            return Response({"error": "Supplier not found"}, status=status.HTTP_404_NOT_FOUND)

        serializer = self.get_serializer(supplier, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)

        return Response(serializer.data, status=status.HTTP_200_OK)

    def perform_update(self, serializer):
        supplier = serializer.save()
        # Update the database used for saving the instance
        supplier.save(using=supplier._state.db)


class BlockOrUnBlockSuppliersView(generics.UpdateAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = SupplierSerializer
    lookup_field = 'pk'

    def update(self, request, *args, **kwargs):
        supplier_id = kwargs.get('supplier_id')
        action = kwargs.get('action')
        business_id = kwargs.get('business_id')
        if not business_id:
            return Response({"error": "business_id is required"}, status=status.HTTP_400_BAD_REQUEST)
        if not action:
            return Response({"error": "action is required"}, status=status.HTTP_400_BAD_REQUEST)
        if not supplier_id:
            return Response({"error": "supplier_id is required"}, status=status.HTTP_400_BAD_REQUEST)
        db_name = f"{business_id}{os.getenv('DB_NAME_SECONDARY')}"
        add_database(db_name)

        try:
            supplier = Supplier.objects.using(db_name).get(pk=supplier_id)
            if action == 'block':
                supplier.show_status = False
                supplier.save()
                return Response({"success": f"{supplier.supplier_name} is Blocked"}, status=status.HTTP_200_OK)
            elif action == 'unblock':
                supplier.show_status = True
                supplier.save()
                return Response({"message": f"{supplier.supplier_name} is Unblock"}, status=status.HTTP_200_OK)
            else:
                return Response({"error": "action is required"}, status=status.HTTP_400_BAD_REQUEST)
        except Supplier.DoesNotExist:
            return Response({"error": "Supplier does not exist"}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class CreateContractView(generics.CreateAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = SupplierContractSerializer

    def post(self, request, *args, **kwargs):
        business_id = request.data.get('business_id')
        if not business_id:
            return Response({"error": "business_id is required"}, status=status.HTTP_400_BAD_REQUEST)

        # Dynamic database name
        db_name = f"{business_id}{os.getenv('DB_NAME_SECONDARY')}"

        # Ensure the dynamic database is added to the configuration
        add_database(db_name)

        # Calculate the contract end date
        contact_period = int(request.data.get('contact_period'))
        contract_end_date = timezone.now() + timedelta(days=contact_period * 365)

        # Data for creating the supplier contract
        supplier_contract_data = {
            'supplier_id': request.data.get('supplier_id'),
            'date_contracted': timezone.now(),
            'contract_end_date': contract_end_date,
        }

        # Serializer for validation
        serializer = self.get_serializer(data=supplier_contract_data)
        serializer.is_valid(raise_exception=True)

        # Create contract in the dynamic database
        try:
            supplier = SupplierContract.objects.using(db_name).create(**serializer.validated_data)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class SupplierContractListView(generics.ListAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = SupplierContractSerializer

    def get_queryset(self):
        return SupplierContract.objects.all()

    def get(self, request, *args, **kwargs):
        business_id = kwargs.get('business_id')
        if not business_id:
            return Response({"error": "business_id is required"}, status=status.HTTP_400_BAD_REQUEST)
        db_name = f"{business_id}{os.getenv('DB_NAME_SECONDARY')}"
        add_database(db_name)

        try:
            supplier_contract_data = SupplierContract.objects.using(db_name).all()
            serializer = self.get_serializer(supplier_contract_data, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except SupplierContract.DoesNotExist:
            return Response({"error": "Supplier contract does not exist"}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class CreateOrderView(generics.CreateAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = OrderSerializer

    def post(self, request, *args, **kwargs):
        business_id = request.data.get('business_id')
        user_id = request.user.user_id
        if not business_id:
            return Response({"error": "business_id is required"}, status=status.HTTP_400_BAD_REQUEST)
        db_name = f"{business_id}{os.getenv('DB_NAME_SECONDARY')}"
        add_database(db_name)

        # Parse delivery_date and amount_due_date from request data
        try:
            delivery_date = datetime.strptime(request.data.get('delivery_date'), '%Y-%m-%d')
            amount_due_date = datetime.strptime(request.data.get('amount_due_date'), '%Y-%m-%d')
        except ValueError as e:
            return Response({"error": f"Date format error: {str(e)}"}, status=status.HTTP_400_BAD_REQUEST)

        order_data = {
            'supplier_id': request.data.get('supplier_id'),
            'date_ordered': timezone.now(),
            'delivery_date': delivery_date,
            'amount_ordered': request.data.get('amount_ordered'),
            'amount_paid': request.data.get('amount_paid'),
            'amount_due_date': amount_due_date,
            'order_status': 'pending'
        }
        serializer = self.get_serializer(data=order_data)
        serializer.is_valid(raise_exception=True)
        try:
            order = Order.objects.using(db_name).create(**serializer.validated_data)
            if float(order_data.get('amount_paid')) > 0.00:
                cashbook_date = {
                    'business_id': business_id,
                    'transaction_type': 'expense',
                    'transaction_amount': order.amount_paid,
                    'description': f'paid for order {order.order_id}',
                    'created_by': str(user_id)
                }
                cash_book_status = create_cash_book_entry(cashbook_date)
                print(cash_book_status)
                if cash_book_status.status_code == 201:
                    return Response(serializer.data, status=status.HTTP_201_CREATED)
                else:
                    order.delete()
                    return Response({'message': 'Try again'}, status=status.HTTP_400_BAD_REQUEST)
            else:
                return Response(serializer.data, status=status.HTTP_201_CREATED)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class ListAllOrdersView(generics.ListAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = OrderSerializer

    def get(self, request, *args, **kwargs):
        business_id = kwargs.get('business_id')
        if not business_id:
            return Response({"error": "business_id is required"}, status=status.HTTP_400_BAD_REQUEST)
        db_name = f"{business_id}{os.getenv('DB_NAME_SECONDARY')}"
        add_database(db_name)

        try:
            orders = Order.objects.using(db_name).all().order_by('-date_ordered')
            serializer = self.get_serializer(orders, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Order.DoesNotExist:
            return Response({"error": "Order does not exist"}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)