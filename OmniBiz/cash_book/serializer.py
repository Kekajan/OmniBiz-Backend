from rest_framework import serializers

from cash_book.models import CashBook


class CashBookSerializer(serializers.ModelSerializer):
    class Meta:
        model = CashBook
        fields = [
            'transaction_type',
            'transaction_amount',
            'balance',
            'description',
            'created_by'
        ]

