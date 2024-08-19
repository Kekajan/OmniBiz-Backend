from django.urls import path
from owner.views import (CreateOwnerView,
                         UpdateOwnerView,
                         GetOwnerView, OwnerActionView,
                         )

urlpatterns = [
    path('createOwner', CreateOwnerView.as_view(), name='create owner'),
    path('updateOwner/<str:user_id>/', UpdateOwnerView.as_view(), name='update owner'),
    path('get-owner/<str:user_id>', GetOwnerView.as_view(), name='get owner'),
    path('owner/owner-action/<str:user_id>', OwnerActionView.as_view(), name='owner action'),
]
