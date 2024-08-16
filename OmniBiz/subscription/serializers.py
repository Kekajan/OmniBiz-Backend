from rest_framework import serializers

from subscription.models import PaymentCard, Subscription


class CardSerializer(serializers.ModelSerializer):
    class Meta:
        model = PaymentCard
        fields = [
            'id',
            'card_holder',
            'card_holder_name',
            'card_number',
            'card_expiry_date',
            'auto_renew',
            'created_at'
        ]
        read_only_fields = [
            'id',
            'created_at'
        ]

    def validate_card_number(self, value):
        if not value:
            raise serializers.ValidationError("Card number is required.")
        if len(value) < 16:
            raise serializers.ValidationError("Card number must be 16 digits long.")
        return value

    # Custom validation for card expiry date
    def validate_card_expiry_date(self, value):
        if not value:
            raise serializers.ValidationError("Card expiry date is required.")
        # Add additional checks for date format if needed
        return value


class SubscriptionSerializer(serializers.ModelSerializer):
    # Expecting a single payment card ID
    payment_card = serializers.IntegerField(write_only=True)

    class Meta:
        model = Subscription
        fields = [
            'id',
            'owner',
            'business',
            'start_date',
            'end_date',
            'status',
            'auto_renew',
            'next_billing_date',
            'payment_card',
            'amount',
            'created_at',
            'updated_at'
        ]
        read_only_fields = [
            'id'
        ]

    def validate_payment_card(self, value):
        # Validate that the provided payment card ID exists
        try:
            payment_card = PaymentCard.objects.get(pk=value)
        except PaymentCard.DoesNotExist:
            raise serializers.ValidationError("Payment card not found.")
        return payment_card

    def create(self, validated_data):
        # Remove payment_card from validated_data as it will be handled separately
        payment_card = validated_data.pop('payment_card')

        # Create the subscription
        subscription = Subscription.objects.create(**validated_data)

        # Associate the payment card with the subscription
        subscription.payment_card = payment_card
        subscription.save()

        return subscription
