import os
from django.db import connections
from django.db.models import Sum
from Utils.Database.Database_Routing.add_database import add_database
from business.models import Business
from cash_book.models import CashBook


def aggregate_business_data(owner_id):
    businesses = Business.objects.filter(owner_id=owner_id)  # Get all businesses owned by the owner
    total_income = 0
    total_expense = 0
    total_profit = 0

    for business in businesses:
        db_name = f'{business.business_id}{os.getenv("DB_NAME_SECONDARY")}'
        add_database(db_name)

        # Aggregate income, expenses, and profit from this business
        income = CashBook.objects.using(db_name).filter(transaction_type='income').aggregate(
            total_income=Sum('transaction_amount'))
        expense = CashBook.objects.using(db_name).filter(transaction_type='expense').aggregate(
            total_expense=Sum('transaction_amount'))

        # Handle None values (when no transactions are present)
        income_sum = income['total_income'] or 0
        expense_sum = expense['total_expense'] or 0
        profit = income_sum - expense_sum

        total_income += income_sum
        total_expense += expense_sum
        total_profit += profit

    return {
        'total_income': total_income,
        'total_expense': total_expense,
        'total_profit': total_profit,
    }
