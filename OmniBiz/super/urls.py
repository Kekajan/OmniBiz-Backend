from django.urls import path

from super.views import (SuperCreateView,
                         GetAllOwners,
                         GetAllBusinesses, GetAllAccesses)

urlpatterns = [
    path('create-access', SuperCreateView.as_view(), name='create-access'),
    path('get-owners', GetAllOwners.as_view(), name='get-all-owners'),
    path('get-businesses', GetAllBusinesses.as_view(), name='get-all-businesses'),
    path('get-staff-accesses', GetAllAccesses.as_view(), name='get-staff-accesses'),
]
