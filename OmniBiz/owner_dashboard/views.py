import os

from django.shortcuts import render
from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

from Utils.Database.Database_Routing.add_database import add_database
from cash_book.models import CashBook


# Create your views here.
class ListAllTransaction(generics.ListCreateAPIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        user = request.user
        data = []
        try:
            from business.models import Business
            businesses = Business.objects.filter(owner_id=user.user_id)
            for business in businesses:
                db_name = f"{business.business_id}{os.getenv("DB_NAME_SECONDARY")}"
                add_database(db_name)
                cash_book_data = CashBook.objects.using(db_name).all()
                from cash_book.serializer import CashBookSerializer
                serializer = CashBookSerializer(cash_book_data, many=True)
                business_account = {
                    "business_id": business.business_id,
                    "cash_book_data": serializer.data
                }
                data.append(business_account)
            return Response(data, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

