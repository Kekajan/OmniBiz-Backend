from django.urls import path

from subscription.views import CreatePaymentCardView, GetPaymentCardView, UpdatePaymentCardView, CreateSubscriptionView, \
    GetSubscriptionView, ListSubscriptionView

urlpatterns = [
    path('create-card', CreatePaymentCardView.as_view(), name='create_payment_card'),
    path('get-card/<str:card_id>', GetPaymentCardView.as_view(), name='get_payment_card'),
    path('update-card/<str:card_id>', UpdatePaymentCardView.as_view(), name='update_payment_card'),
    path('create-subscription', CreateSubscriptionView.as_view(), name='create_subscription'),
    path('get-subscription/<str:subscription_id>', GetSubscriptionView.as_view(), name='get_subscription'),
    path('list-subscriptions', ListSubscriptionView.as_view(), name='list_subscriptions'),
]