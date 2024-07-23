from django.urls import path

from billing.views import CreateBillView, ListBillView, ListBillViewByCreator, CheckoutBillView, CreateCustomerView, \
    ListCustomerView, ReturnItemView

urlpatterns = [
    path('create-bill', CreateBillView.as_view(), name='create-bill'),
    path('list-bill/<str:business_id>', ListBillView.as_view(), name='list-bill'),
    path('list-bill-creator/<str:business_id>', ListBillViewByCreator.as_view(), name='list-bill-by-creator'),
    path('checkout-bill/<str:business_id>/<str:invoice_id>', CheckoutBillView.as_view(), name='checkout-bill'),
    path('create-customer', CreateCustomerView.as_view(), name='create-customer'),
    path('list-customer/<str:business_id>', ListCustomerView.as_view(), name='list-customer'),
    path('return-item/<str:sales_id>', ReturnItemView.as_view(), name='Return-item'),
]
