from django.shortcuts import render
from rest_framework import generics, status
from rest_framework.exceptions import NotFound, PermissionDenied
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

from datetime import datetime
from dateutil.relativedelta import relativedelta

from business.models import Business
from notification.models import Notification
from notification.views import create_notification
from subscription.models import PaymentCard, Subscription
from subscription.serializers import CardSerializer, SubscriptionSerializer


# Create your views here.
class CreatePaymentCardView(generics.CreateAPIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        user = request.user
        data = request.data

        data['card_holder'] = user.user_id

        serializer = CardSerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class GetPaymentCardView(generics.RetrieveAPIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        card_id = kwargs.get('card_id')

        try:
            card = PaymentCard.objects.get(pk=card_id)
            serializer = CardSerializer(card)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except PaymentCard.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({f"Error while get card: {e}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class UpdatePaymentCardView(generics.UpdateAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = CardSerializer

    def put(self, request, *args, **kwargs):
        card_id = kwargs.get('card_id')
        user = request.user

        # Retrieve the card instance
        try:
            card = PaymentCard.objects.get(id=card_id)
        except PaymentCard.DoesNotExist:
            raise NotFound(detail="Payment card not found.")

        # Check if the user is the owner of the card
        if card.card_holder != user:
            raise PermissionDenied(detail="You do not have permission to update this card.")

        # Update the card
        serializer = self.get_serializer(card, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class CreateSubscriptionView(generics.CreateAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = SubscriptionSerializer

    def post(self, request, *args, **kwargs):
        user = request.user
        data = request.data
        current_date = datetime.now()

        # Adding one year
        one_year_later = current_date + relativedelta(years=1)
        data['owner'] = user.user_id
        data['start_date'] = current_date
        data['end_date'] = one_year_later
        data['status'] = 'active'
        data['next_billing_date'] = one_year_later
        data['created_at'] = current_date

        serializer = SubscriptionSerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            try:
                business = Business.objects.get(business_id=data['business'])
                business.subscription_count += 1
                business.subscription_ended_at = one_year_later
                if not business.subscription_started_at:
                    business.subscription_started_at = current_date
                business.save()
                notification = Notification.objects.create(
                    message=f"Your subscription has been started form {current_date}. This subscription want to renew at {one_year_later}.",
                    target='user',
                    target_id=user.user_id,
                )
                create_notification(notification)
            except Business.DoesNotExist:
                return Response("Business Does not exist", status=status.HTTP_404_NOT_FOUND)
            except Exception as e:
                return Response(f"error: {e}", status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class GetSubscriptionView(generics.RetrieveAPIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        subscription_id = kwargs.get('subscription_id')

        if not subscription_id:
            return Response(status=status.HTTP_404_NOT_FOUND)

        try:
            subscription = Subscription.objects.get(id=subscription_id)
            serializer = SubscriptionSerializer(subscription)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Subscription.DoesNotExist:
            return Response({"Subscription Not Found"}, status=status.HTTP_404_NOT_FOUND)


class ListSubscriptionView(generics.ListAPIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        try:
            subscriptions = Subscription.objects.all()
            serializer = SubscriptionSerializer(subscriptions, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Subscription.DoesNotExist:
            return Response({"Subscriptions Not found"}, status=status.HTTP_404_NOT_FOUND)
