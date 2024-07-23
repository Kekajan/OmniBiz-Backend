# serializers.py
from rest_framework import serializers

from authentication.models import StaffAccess, User
from .models import Staff


class StaffSerializer(serializers.ModelSerializer):
    class Meta:
        model = Staff
        fields = '__all__'


class UpdateStaffAccessSerializer(serializers.ModelSerializer):
    permissions = serializers.ListField(child=serializers.CharField(), write_only=True)

    class Meta:
        model = StaffAccess
        fields = '__all__'
        read_only_fields = ('user', 'permission')

    def update_permissions(self, user_id, new_permissions):
        # Get current permissions
        current_permissions = StaffAccess.objects.filter(user_id=user_id).values_list('permission', flat=True)

        # Determine permissions to remove and add
        permissions_to_remove = set(current_permissions) - set(new_permissions)
        permissions_to_add = set(new_permissions) - set(current_permissions)

        # Remove permissions
        if permissions_to_remove:
            StaffAccess.objects.filter(user_id=user_id, permission__in=permissions_to_remove).delete()

        # Add new permissions
        for permission in permissions_to_add:
            StaffAccess.objects.create(user_id=user_id, permission=permission)

        return StaffAccess.objects.filter(user_id=user_id)
