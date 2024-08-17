from celery import shared_task
from datetime import datetime, timedelta

from notification.models import Notification
from subscription.models import Subscription
from django.core.mail import send_mail


@shared_task
def subscription_have_30_days():
    before_30 = datetime.now() + timedelta(days=30)  # Check subscriptions ending in 3 days
    subscriptions = Subscription.objects.filter(next_billing_date=before_30)

    for subscription in subscriptions:
        user = subscription.owner
        notification = Notification.objects.create(
            message=f"Your subscription for business {subscription.business.business_name} "
                    f"will end in 30 days.",
            target='user',
            target_id=user.user_id,
        )


@shared_task
def subscription_have_7_days():
    before_7 = datetime.now() + timedelta(days=7)
    subscriptions = Subscription.objects.filter(next_billing_date=before_7)

    for subscription in subscriptions:
        user = subscription.owner
        notification = Notification.objects.create(
            message=f"Your subscription for business {subscription.business.business_name} "
                    f"will end in 7 days.",
            target='user',
            target_id=user.user_id,
        )


@shared_task
def subscription_have_1_day():
    before_1 = datetime.now() + timedelta(days=1)
    subscriptions = Subscription.objects.filter(next_billing_date=before_1)
    for subscription in subscriptions:
        user = subscription.owner
        notification = Notification.objects.create(
            message=f"Your subscription for business {subscription.business.business_name} "
                    f"will end in tomorrow.",
            target='user',
            target_id=user.user_id,
        )
