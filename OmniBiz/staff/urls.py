from django.urls import path

from authentication.views import ActivateAccountView
from staff.views import StaffListView, UpdateStaffView, StaffView, UpdateStaffAccessView

urlpatterns = [
    path('get-staff/<str:business_id>/staff/', StaffListView.as_view(), name='staff_list'),
    path('update-staff/<str:user_id>/', UpdateStaffView.as_view(), name='staff_update'),
    path('get-staff-profile/<str:user_id>/', StaffView.as_view(), name='get_staff_profile'),
    path('update-staff-access/<str:user_id>/', UpdateStaffAccessView.as_view(), name='update_staff_access'),
]
