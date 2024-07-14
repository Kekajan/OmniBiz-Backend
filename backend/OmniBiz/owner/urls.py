from django.urls import path
from owner.views import (CreateOwnerView,
                         UpdateOwnerView,
                         GetOwnerView,
                         )

urlpatterns = [
    path('createOwner', CreateOwnerView.as_view(), name='create owner'),
    path('updateOwner/<str:owner_id>/', UpdateOwnerView.as_view(), name='update owner'),
    path('get-owner/<str:user_id>', GetOwnerView.as_view(), name='get owner'),
]
