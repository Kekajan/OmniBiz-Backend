from django.contrib import admin
from django.urls import path, include
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/auth/', include('authentication.urls')),
    path('api/token', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh', TokenRefreshView.as_view(), name='token_refresh'),
    path('api-path', include('rest_framework.urls')),
    path('api/owner/', include('owner.urls')),
    path('api/business/', include('business.urls')),
    path('api/staff/', include('staff.urls')),
    path('api/super/', include('super.urls')),
    path('api/cashbook/', include('cash_book.urls')),
    path('api/suppliers/', include('suppliers.urls')),
    path('api/inventory/', include('inventory.urls')),
    path('api/billing/', include('billing.urls')),
    path('api/notification/', include('notification.urls')),
    path('api/payment/', include('subscription.urls')),
    path('api/transaction/', include('owner_dashboard.urls')),
]
