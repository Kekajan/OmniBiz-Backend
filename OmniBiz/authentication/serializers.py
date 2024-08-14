import logging
import os
import secrets

from django.db import transaction
from rest_framework_simplejwt.tokens import RefreshToken, TokenError
from django.utils.text import gettext_lazy as _

from Utils.Database.Database_Routing.add_database import add_database
from authentication.models import User, StaffAccess, HigherStaffAccess, HigherStaffUser
from django.urls import reverse
from rest_framework import serializers
from Utils.Common.email_or_username import email_to_username
from Utils.Mail_service.Mail_Service import MailService
from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes
from django.contrib.auth.hashers import make_password
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

from staff.models import Staff
from super.models import Super


class UserSerializer(serializers.ModelSerializer):
    business_id = serializers.ListField(
        child=serializers.CharField(),
        write_only=True,
        required=False
    )
    permissions = serializers.JSONField(write_only=True, required=False)
    role_name = serializers.CharField(write_only=True, required=False)
    password = serializers.CharField(write_only=True, required=False, min_length=5)

    class Meta:
        model = User
        fields = ['email', 'business_id', 'password', 'permissions', 'role_name', 'role', 'token']
        extra_kwargs = {'password': {'write_only': True, 'min_length': 5}}
        read_only_fields = ('token',)

    def validate(self, data):
        role = data.get('role', 'staff')
        business_ids = data.get('business_id', [])

        if role == 'staff' and len(business_ids) != 1:
            raise serializers.ValidationError({'business_id': 'Staff must have exactly one business_id.'})
        if role == 'higher-staff' and not business_ids:
            raise serializers.ValidationError({'business_id': 'Higher staff must have at least one business_id.'})

        return data

    def create(self, validated_data):
        email = validated_data.pop('email')
        username = email_to_username(email)
        role = validated_data.get('role') if 'role' in validated_data else 'staff'
        business_ids = validated_data.pop('business_id', [])
        permissions = validated_data.pop('permissions', [])
        role_name = validated_data.pop('role_name', None)
        password = validated_data.pop('password', 'abcd1234' if role in ['staff', 'admin', 'higher-staff'] else None)

        if not password:
            raise serializers.ValidationError({'password': 'This field is required for owners'})

        activation_token = secrets.token_urlsafe(32)
        if User.objects.filter(email=email).exists():
            raise serializers.ValidationError({'error': 'User already exists'})

        if role != 'staff':
            user = User.objects.create_user(
                email=email,
                username=username,
                password=password,
                is_active=False,
                role=role,
                token=activation_token,
            )
        else:
            user = User.objects.create_user(
                email=email,
                username=username,
                password=password,
                is_active=False,
                role=role,
                token=activation_token,
                business_id=business_ids[0],
            )

        try:
            request = self.context.get('request')
            auth_user = request.user

            if role == 'staff' and business_ids:
                business_id = business_ids[0]
                database_name = f'{business_id}{os.getenv("DB_NAME_SECONDARY")}'
                print(database_name)
                add_database(database_name)

                access_permissions = Super.objects.values_list('permission', flat=True)
                valid_permissions = [permission for permission in permissions if permission in access_permissions]

                for permission in valid_permissions:
                    StaffAccess.objects.create(
                        user=user,
                        permission=permission
                    )

                with transaction.atomic(using=database_name):
                    Staff.objects.using(database_name).create(
                        business_id=business_id,
                        role_name=role_name,
                        user_id=user.user_id,
                        created_by=auth_user.user_id
                    )
            elif role == 'higher-staff' and business_ids:
                HigherStaffUser.objects.create(
                    user=user,
                    status='active',
                    created_by=auth_user.user_id,
                )

                for business_id in business_ids:
                    HigherStaffAccess.objects.create(
                        user=user,
                        business_id=business_id
                    )

            activation_link = reverse('verify', kwargs={'user_id': user.user_id, 'token': activation_token})
            activation_url = self.context['request'].build_absolute_uri(activation_link)

            subject = 'Activate Your Account'
            message1 = f'Please click the following link to activate your account: {activation_url}\n'
            message = message1

            if role in ['staff', 'admin', 'higher-staff']:
                message2 = (f'First, you need to activate your account. Then '
                            f'you can use these credentials\nUsername: {username}\nPassword: {password}\n'
                            f'for login your account')
                message = message1 + message2

            mail_service = MailService()
            mail_service.send_email(subject, message, email)

            return user
        except Exception as e:
            raise serializers.ValidationError({'error': str(e)})


class PasswordResetRequestSerializer(serializers.Serializer):
    email = serializers.EmailField(required=True)

    def validate_email(self, value):
        try:
            User.objects.get(email=value)
        except User.DoesNotExist:
            raise serializers.ValidationError('User does not exist with associated email')
        return value

    def save(self, **kwargs):
        request = self.context.get('request')
        email = self.validated_data.get('email')
        user = User.objects.get(email=email)

        token = default_token_generator.make_token(user)
        uid = urlsafe_base64_encode(force_bytes(user.pk))

        reset_link = reverse('password-reset', kwargs={'uid': uid, 'token': token})
        reset_url = request.build_absolute_uri(reset_link)

        subject = 'Reset Your Account'
        message = f'Please click the following link to reset your password: {reset_url}'

        mail_service = MailService()
        mail_service.send_email(subject, message, email)

        return user


class PasswordResetConfirmSerializer(serializers.Serializer):
    new_password = serializers.CharField(write_only=True)
    uid = serializers.CharField(write_only=True)
    token = serializers.CharField(write_only=True)

    def validate(self, data):
        try:
            uid = urlsafe_base64_decode(data['uid']).decode()
            user = User.objects.get(pk=uid)
        except (TypeError, ValueError, OverflowError, User.DoesNotExist):
            raise serializers.ValidationError("Invalid UID")

        if not default_token_generator.check_token(user, data['token']):
            raise serializers.ValidationError("Invalid token")

        return data

    def save(self):
        uid = urlsafe_base64_decode(self.validated_data['uid']).decode()
        user = User.objects.get(pk=uid)
        user.password = make_password(self.validated_data['new_password'])
        user.save()


class PasswordChangeSerializer(serializers.Serializer):
    new_password = serializers.CharField(write_only=True)
    old_password = serializers.CharField(write_only=True)

    def create(self, validated_data):
        try:
            request = self.context.get('request')
            user = request.user
            logging.info(user)
            if user.check_password(validated_data['old_password']):
                password = make_password(validated_data['new_password'])
                logging.info(validated_data['new_password'])
                logging.info(validated_data['old_password'])
                user.password = password
                user.save()
                return user
            else:
                raise serializers.ValidationError("Incorrect password")
        except (TypeError, ValueError, OverflowError, User.DoesNotExist):
            raise serializers.ValidationError("User does not exist")


class CustomTokenObtainSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        token['role'] = user.role
        return token


class HigherStaffSerializer(serializers.ModelSerializer):
    class Meta:
        model = HigherStaffUser
        fields = ['first_name', 'last_name', 'email', 'phone_number', 'address']

    def update(self, instance, validated_data):
        instance.first_name = validated_data.get('first_name', instance.first_name)
        instance.last_name = validated_data.get('last_name', instance.last_name)
        instance.email = validated_data.get('email', instance.email)
        instance.phone_number = validated_data.get('phone_number', instance.phone_number)
        instance.address = validated_data.get('address', instance.address)
        instance.save()
        return instance
