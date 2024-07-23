from rest_framework import serializers

from super.models import Super


class SuperSerializer(serializers.ModelSerializer):
    class Meta:
        model = Super
        fields = '__all__'

    def validate(self, data):
        return data

    def create(self, validated_data):
        validated_data['created_by'] = self.context['request'].user
        return Super.objects.create(**validated_data)
