from django.urls import path

from super.views import (SuperCreateView,
                         GetAllOwners,
                         GetAllBusinesses, GetAllAccesses, GetHigherStaffAccess)

urlpatterns = [
    path('create-access', SuperCreateView.as_view(), name='create-access'),
    path('get-owners', GetAllOwners.as_view(), name='get-all-owners'),
    path('get-businesses', GetAllBusinesses.as_view(), name='get-all-businesses'),
    path('get-staff-accesses', GetAllAccesses.as_view(), name='get-staff-accesses'),
    path('get-higher-staff-accesses/<str:user_id>', GetHigherStaffAccess.as_view(), name='get-higher-staff-accesses'),
]
