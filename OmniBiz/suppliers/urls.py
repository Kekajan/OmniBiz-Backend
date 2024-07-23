from django.urls import path

from suppliers.views import CreateSuppliersView, ListSuppliersView, UpdateSuppliersView, BlockOrUnBlockSuppliersView, \
    CreateContractView, SupplierContractListView, CreateOrderView, ListAllOrdersView

urlpatterns = [
    path('create-supplier', CreateSuppliersView.as_view(), name='create-supplier'),
    path('update-supplier/<str:supplier_id>', UpdateSuppliersView.as_view(), name='list-supplier'),
    path('get-supplier/<str:business_id>', ListSuppliersView.as_view(), name='update-supplier'),
    path('action-supplier/<str:action>/<str:business_id>/<str:supplier_id>', BlockOrUnBlockSuppliersView.as_view(), name='block_or_unblock-supplier'),
    path('create-contract', CreateContractView.as_view(), name='Create-contract'),
    path('get-all-contract/<str:business_id>', SupplierContractListView.as_view(), name='get-all-contract'),
    path('create-order', CreateOrderView.as_view(), name='create-order'),
    path('list-order/<str:business_id>', ListAllOrdersView.as_view(), name='list-order'),
]