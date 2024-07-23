from django.urls import path

from cash_book.views import CashBookView

urlpatterns = [
    path('view-cashbook/<str:business_id>', CashBookView.as_view(), name='cashbook'),
]
