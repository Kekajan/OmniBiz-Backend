from django.urls import path
from business.views import (CreateBusinessView,
                            UpdateBusinessView,
                            GetBusinessView,
                            BlockBusinessView,
                            GetBusinessByOwnerView
                            )

urlpatterns = [
    path('createBusiness', CreateBusinessView.as_view(), name='create-business'),
    path('update-business/<str:business_id>', UpdateBusinessView.as_view(), name='update-business'),
    path('get-business/<str:business_id>', GetBusinessView.as_view(), name='get-business'),
    path('action-business/<str:action>/<str:business_id>', BlockBusinessView.as_view(), name='block-business'),
    path('get-all-businesses/<str:user_id>', GetBusinessByOwnerView.as_view(), name='get-all-businesses-by-owner'),
]
