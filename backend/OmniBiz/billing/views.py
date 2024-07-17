import logging
import os
from asgiref.sync import async_to_sync, sync_to_async
from channels.layers import get_channel_layer
from django.db import connections, transaction
from django.utils import timezone

from rest_framework import generics
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status

from authentication.backend import User
from billing.models import InvoiceItem, Invoice, Customer
from datetime import datetime

from Utils.Database.Database_Routing.add_database import add_database
from billing.serializers import InvoiceSerializers, InvoiceItemSerializers, CustomerSerializers
from cash_book.views import create_cash_book_entry
from django.http import JsonResponse

logger = logging.getLogger(__name__)


# Create your views here.
class CreateBillView(generics.CreateAPIView):
    permission_classes = [IsAuthenticated]

    def create(self, request, *args, **kwargs):
        business_id = request.data.get('business_id')
        user = request.user

        if not business_id:
            return Response({'error': 'business_id is required'}, status=status.HTTP_400_BAD_REQUEST)

        db_name = f'{business_id}{os.getenv("DB_NAME_SECONDARY")}'
        add_database(db_name)

        # Prepare invoice data
        invoice_data = {
            'date_and_time': timezone.now(),
            'amount': request.data.get('amount'),
            'created_by': str(user.user_id),
            'invoice_status': request.data.get('invoice_status'),
            'customer': request.data.get('customer') if request.data.get('customer') else None,
            'payment_type': request.data.get('payment_type'),
            'cheque_number': request.data.get('cheque_number') if request.data.get('cheque_number') else None,
            'payee_name': request.data.get('payee_name') if request.data.get('payee_name') else None,
            'due_date': request.data.get('due_date') if request.data.get('due_date') else None,
            'card_number': request.data.get('card_number') if request.data.get('card_number') else None,
        }

        # Start transaction
        with transaction.atomic():
            invoice_serializer = InvoiceSerializers(data=invoice_data, context={'request': request})
            if invoice_serializer.is_valid():
                invoice = Invoice.objects.using(db_name).create(**invoice_serializer.validated_data)

                cash_book_data = {
                    'business_id': business_id,
                    'transaction_amount': invoice_data['amount'],
                    'transaction_type': 'income',
                    'description': f'sales invoice id {invoice.invoice_id}',
                    'created_by': str(user.user_id),
                }
                cash_book_result = create_cash_book_entry(cash_book_data)
                if cash_book_result.status_code == 201:
                    invoice_items_data = request.data.get('invoice_items', [])
                    invoice_items = []
                    for item_data in invoice_items_data:
                        item_data['invoice'] = invoice.invoice_id
                    invoice_item_serializer = InvoiceItemSerializers(data=invoice_items_data, many=True, context=request)
                    if invoice_item_serializer.is_valid():
                        for item_data in invoice_item_serializer.validated_data:
                            invoice_item = InvoiceItem.objects.using(db_name).create(**item_data)
                            invoice_items_once = {
                                'invoice': str(invoice_item.invoice.invoice_id),
                                'item': invoice_item.item.name if invoice_item.item else None,
                                'quantity': invoice_item.quantity,
                                'price': str(invoice_item.price),
                            }
                            invoice_items.append(invoice_items_once)
                    else:
                        return Response(invoice_item_serializer.errors, status=status.HTTP_400_BAD_REQUEST)
                    add_database(os.getenv('DB_NAME_PRIMARY'))
                    created_by = User.objects.using(os.getenv('DB_NAME_PRIMARY')).get(user_id=invoice.created_by)
                    websocket_message = {
                        'invoice_id': str(invoice.invoice_id),
                        'invoice_amount': str(invoice.amount),
                        'payment': invoice.invoice_status,
                        'created_by': created_by.username,
                        'customer': invoice.customer.name if invoice.customer else None,
                        'invoice_items': invoice_items,
                    }
                    # Send WebSocket message synchronously
                    channel_layer = get_channel_layer()
                    async_to_sync(channel_layer.group_send)(
                        f'business_{business_id}',
                        {
                            'type': 'invoice_message',
                            'message': websocket_message,
                        }
                    )

                    return Response({
                        'invoice': websocket_message
                    }, status=status.HTTP_201_CREATED)
                else:
                    return Response({'error': cash_book_result.json()}, status=status.HTTP_400_BAD_REQUEST)
            else:
                return Response(invoice_serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ListBillView(generics.ListAPIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        business_id = kwargs.get('business_id')
        user = request.user
        if not business_id:
            return Response({'error': 'business_id is required'}, status=status.HTTP_400_BAD_REQUEST)
        db_name = f'{business_id}{os.getenv("DB_NAME_SECONDARY")}'
        add_database(db_name)
        data = []

        try:
            invoices = Invoice.objects.using(db_name).all()
            for invoice in invoices:
                invoice_data = {
                    'invoice_id': invoice.invoice_id,
                    'date_and_time': invoice.date_and_time,
                    'amount': invoice.amount,
                    'created_by': invoice.created_by,
                    'invoice_status': invoice.invoice_status,
                    'customer': invoice.customer.name,
                    'items': []
                }
                invoice_items = InvoiceItem.objects.using(db_name).filter(invoice_id=invoice.invoice_id)
                for invoice_item in invoice_items:
                    item_data = {
                        'category': invoice_item.category.name,
                        'item': invoice_item.item.name,
                        'price': invoice_item.price,
                        'quantity': invoice_item.quantity,
                    }
                    invoice_data['items'].append(item_data)
                data.append(invoice_data)
            return JsonResponse(data, safe=False)

        except Invoice.DoesNotExist:
            return Response({'error': 'Invoice does not exist'}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class ListBillViewByCreator(generics.ListAPIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        business_id = kwargs.get('business_id')
        user = request.user
        user_id = user.user_id

        if not business_id:
            return Response({'error': 'business_id is required'}, status=status.HTTP_400_BAD_REQUEST)

        db_name = f'{business_id}{os.getenv("DB_NAME_SECONDARY")}'
        add_database(db_name)

        data = []

        try:
            invoices = Invoice.objects.using(db_name).filter(created_by=user_id)
            for invoice in invoices:
                invoice_data = {
                    'invoice_id': invoice.invoice_id,
                    'date_and_time': invoice.date_and_time,
                    'amount': invoice.amount,
                    'created_by': invoice.created_by,
                    'invoice_status': invoice.invoice_status,
                    'customer': invoice.customer.name,
                    'items': []
                }
                invoice_items = InvoiceItem.objects.using(db_name).filter(invoice_id=invoice.invoice_id)
                for invoice_item in invoice_items:
                    item_data = {
                        'category': invoice_item.category.name,
                        'item': invoice_item.item.name,
                        'price': invoice_item.price,
                        'quantity': invoice_item.quantity,
                    }
                    invoice_data['items'].append(item_data)
                data.append(invoice_data)
            return JsonResponse(data, safe=False)

        except Invoice.DoesNotExist:
            return Response({'error': 'Invoice does not exist'}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class CheckoutBillView(generics.UpdateAPIView):
    permission_classes = [IsAuthenticated]
    lookup_field = 'invoice_id'

    def update(self, request, *args, **kwargs):
        business_id = kwargs.get('business_id')
        invoice_id = kwargs.get('invoice_id')
        user = request.user
        user_id = user.user_id
        if not business_id:
            return Response({'error': 'business_id is required'}, status=status.HTTP_400_BAD_REQUEST)
        db_name = f'{business_id}{os.getenv("DB_NAME_SECONDARY")}'
        add_database(db_name)

        try:
            invoice = Invoice.objects.using(db_name).get(invoice_id=invoice_id)
            invoice.checked_on = timezone.now()
            invoice.checked_by = user_id
            invoice.save()
            return Response({'invoice': str(invoice)}, status=status.HTTP_200_OK)
        except Invoice.DoesNotExist:
            return Response({'error': 'Invoice does not exist'}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class CreateCustomerView(generics.CreateAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = CustomerSerializers

    def post(self, request, *args, **kwargs):
        business_id = request.data.get('business_id')
        user = request.user
        user_id = user.user_id

        if not business_id:
            return Response({'error': 'business_id is required'}, status=status.HTTP_400_BAD_REQUEST)

        db_name = f'{business_id}{os.getenv("DB_NAME_SECONDARY")}'

        # Attempt to add the new database
        try:
            add_database(db_name)
        except Exception as e:
            return Response({'error': f"Error creating or migrating database: {e}"},
                            status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        customer_data = {
            'name': request.data.get('name'),
            'address': request.data.get('address'),
            'phone': request.data.get('phone'),
            'created_by': str(user_id),
            'created_at': timezone.now()
        }

        with connections[db_name].cursor() as cursor:
            with transaction.atomic(using=db_name):
                connections[db_name].ensure_connection()
                try:
                    customer = Customer.objects.using(db_name).create(**customer_data)
                    return Response({'customer': str(customer)}, status=status.HTTP_201_CREATED)
                except Exception as e:
                    return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class ListCustomerView(generics.ListAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = CustomerSerializers

    def get(self, request, *args, **kwargs):
        business_id = kwargs.get('business_id')
        user = request.user
        user_id = user.user_id
        if not business_id:
            return Response({'error': 'business_id is required'}, status=status.HTTP_400_BAD_REQUEST)
        db_name = f'{business_id}{os.getenv("DB_NAME_SECONDARY")}'
        add_database(db_name)

        try:
            customers = Customer.objects.using(db_name).all()
            serializer = CustomerSerializers(customers, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Customer.DoesNotExist:
            return Response({'error': 'Customer does not exist'}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class ReturnItemView(generics.UpdateAPIView):
    permission_classes = [IsAuthenticated]
    lookup_field = 'sales_id'

    def update(self, request, *args, **kwargs):
        sales_id = kwargs.get('sales_id')
        business_id = request.data.get('business_id')
        invoice_id = request.data.get('invoice_id')
        user = request.user

        if not business_id:
            return Response({'error': 'business_id is required'}, status=status.HTTP_400_BAD_REQUEST)

        db_name = f'{business_id}{os.getenv("DB_NAME_SECONDARY")}'
        add_database(db_name)

        try:
            invoice_item = InvoiceItem.objects.using(db_name).get(sales_id=sales_id, invoice_id=invoice_id)
            invoice_item.return_status = True
            invoice_item.save()
            try:
                quantity = invoice_item.quantity
                price = invoice_item.price
                transaction_amount = price * quantity

                cash_book_data = {
                    'business_id': business_id,
                    'transaction_amount': transaction_amount,
                    'transaction_type': 'expense',
                    'description': f'Return item id {invoice_item.sales_id}',
                    'created_by': str(user.user_id),
                }
                result = create_cash_book_entry(cash_book_data)

                if result.status_code == 201:
                    return Response({'Item Returned': invoice_id}, status=status.HTTP_201_CREATED)
                else:
                    return Response({'Error': result.text}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            except Exception as e:
                return Response({'Error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        except InvoiceItem.DoesNotExist:
            return Response({'error': 'Invoice item does not exist'}, status=status.HTTP_400_BAD_REQUEST)

