# Create your views here.
import os
from rest_framework import status, generics
from rest_framework.permissions import IsAuthenticated
from Utils.Database.Database_Routing.add_database import add_database
from cash_book.models import CashBook
from datetime import datetime
from cash_book.serializer import CashBookSerializer
from rest_framework.exceptions import ValidationError
from rest_framework.response import Response


def create_cash_book_entry(data):
    business_id = data['business_id']
    db_name = f"{business_id}{os.getenv('DB_NAME_SECONDARY')}"
    add_database(db_name)

    # Fetch the last entry if it exists
    last_entry = CashBook.objects.using(db_name).last()
    last_balance = last_entry.balance if last_entry else 0.0

    transaction_amount = data.get('transaction_amount')
    transaction_type = data.get('transaction_type')

    # Ensure transaction_amount is valid
    try:
        transaction_amount = float(transaction_amount)
    except (TypeError, ValueError):
        raise ValidationError("Invalid transaction amount")

    if transaction_type == 'expense':
        new_balance = last_balance - transaction_amount
    else:
        new_balance = last_balance + transaction_amount

    cash_book_entry = CashBook(
        transaction_time=datetime.now(),
        transaction_type=transaction_type,
        transaction_amount=transaction_amount,
        balance=new_balance,
        description=data.get('description', ''),  # Default to empty string if description is None
        created_by=str(data.get('created_by')),
    )

    serializer = CashBookSerializer(data=cash_book_entry.__dict__)
    if serializer.is_valid():
        cash_book_entry.save(using=db_name)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    raise ValidationError(serializer.errors)


class CashBookView(generics.ListAPIView):
    serializer_class = CashBookSerializer
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        business_id = kwargs.get('business_id')
        db_name = f"{business_id}{os.getenv('DB_NAME_SECONDARY')}"
        add_database(db_name)

        try:
            cash_books = CashBook.objects.using(db_name).all()
            serializer = CashBookSerializer(cash_books, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
