from django.urls import path

from inventory.views import CreateCategoryView, CategoryListView, DeleteCategoryView, \
    CreateItemView, UpdateItemView, ItemListView, DeleteItemView, CreateInventoryView, \
    InventoryListView

urlpatterns = [
    path('create-category', CreateCategoryView.as_view(), name='create-category'),
    path('list-category/<str:business_id>', CategoryListView.as_view(), name='list-category'),
    path('delete-category/<str:business_id>/<str:category_id>', DeleteCategoryView.as_view(), name='delete-category'),
    path('create-item', CreateItemView.as_view(), name='create-item'),
    path('update-item/<str:business_id>/<str:item_id>', UpdateItemView.as_view(), name='update-item'),
    path('list-item/<str:business_id>', ItemListView.as_view(), name='list-item'),
    path('delete-item/<str:business_id>/<str:item_id>', DeleteItemView.as_view(), name='delete-item'),
    path('create-inventory', CreateInventoryView.as_view(), name='create-inventory'),
    path('list-inventory/<str:business_id>', InventoryListView.as_view(), name='list-inventory'),
]
