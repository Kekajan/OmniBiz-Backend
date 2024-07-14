from rest_framework import serializers
from owner.models import Owner


class OwnerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Owner
        fields = ['owner_id', 'first_name', 'last_name', 'phone_number', 'business_count', 'profit',
                  'subscription_amount']
        read_only_fields = ['owner_id', 'user_id', 'business_count', 'profit', 'subscription_amount']

    def create(self, validated_data):
        request = self.context['request']
        user = request.user
        owner_instance = Owner(**validated_data, user_id=user.user_id)
        owner_instance.save()
        return owner_instance
