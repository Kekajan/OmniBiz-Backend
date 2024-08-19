from django.urls import path

from owner_dashboard.views import ListAllTransaction

urlpatterns = [
    path("owner-accounts", ListAllTransaction.as_view(), name="owner-accounts"),
]