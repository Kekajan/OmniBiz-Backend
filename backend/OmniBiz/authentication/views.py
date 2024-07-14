import logging
import os

from django.utils import timezone

from Utils.Common.email_or_username import email_to_username
from django.shortcuts import get_object_or_404

from django.contrib.auth import authenticate
from rest_framework import generics, status
from rest_framework.permissions import AllowAny, IsAuthenticated

from Utils.Core.permissions import IsOwner, IsAdmin, IsHigherStaff
from Utils.Database.Database_Routing.add_database import add_database
from authentication.models import User, HigherStaffUser
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken

from authentication.serializers import UserSerializer, PasswordResetRequestSerializer, \
    PasswordResetConfirmSerializer, PasswordChangeSerializer, HigherStaffSerializer
from notification.views import create_notification
from owner.models import Owner
from staff.models import Staff


# Create your views here.

def block_or_unblock(action, user_id):
    user = get_object_or_404(User, pk=user_id)
    if action == 'block':
        user.is_active = False
        user.save()
        return user
    elif action == 'unblock':
        user.is_active = True
        user.save()
        return user
    else:
        return None


class CreateUserView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [AllowAny]


class CreateAdminView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated, IsAdmin]


class CreateStaffView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated, IsOwner]


class ActivateAccountView(generics.GenericAPIView):
    permission_classes = [AllowAny]

    def get(self, request, *args, **kwargs):
        user_id = kwargs.get('user_id')
        token = kwargs.get('token')

        try:
            user = User.objects.get(user_id=user_id)

            if not user.is_active:
                if user.token == token:
                    user.is_active = True
                    user.save()
                    return Response({'message': 'Account is activated'}, status=status.HTTP_200_OK)
                else:
                    return Response({'message': 'Invalid Credential'}, status=status.HTTP_400_BAD_REQUEST)
            else:
                return Response({'message': 'Account already active'}, status=status.HTTP_400_BAD_REQUEST)
        except User.DoesNotExist:
            return Response({'message': 'User not found'}, status=status.HTTP_404_NOT_FOUND)


# authentication/views.py
class LoginView(APIView):
    permission_classes = [AllowAny]

    def post(self, request, *args, **kwargs):
        email = request.data.get('email')
        password = request.data.get('password')
        username = email_to_username(email)

        if email and password:
            user = authenticate(username=username, password=password)
            if user is not None:
                if not user.is_active:
                    return Response({'message': 'Account is not activated'}, status=status.HTTP_401_UNAUTHORIZED)

                refresh = RefreshToken.for_user(user)
                user_role = user.role
                owner_created = Owner.objects.filter(user_id=user.user_id).exists()
                higher_staff_created = HigherStaffUser.objects.filter(user_id=user.user_id).exists()
                staff_created = False

                created = False
                if higher_staff_created and user_role == 'higher-staff':
                    created = True
                elif owner_created and user_role == 'owner':
                    created = True

                if user_role == 'staff':
                    business_id = user.business_id
                    business_db_name = f'{business_id}{os.getenv('DB_NAME_SECONDARY')}'
                    add_database(business_db_name)
                    staff = Staff.objects.using(business_db_name).get(user_id=user.user_id)
                    staff_created = True if staff.updated_at else False
                else:
                    primary_db_name = os.getenv('DB_NAME_PRIMARY')
                    add_database(primary_db_name)

                if user.last_login is None:
                    user.last_login = timezone.now()
                    user.save(update_fields=['last_login'])
                    return Response({
                        'refresh': str(refresh),
                        'access': str(refresh.access_token),
                        'message': 'Welcome, first-time user!',
                        'user_role': user_role,
                        'user_id': user.user_id,
                        f'{user_role}_created': created if user_role == 'owner' or user_role == 'higher-staff' else staff_created,
                    }, status=status.HTTP_200_OK)
                else:
                    user.last_login = timezone.now()
                    user.save(update_fields=['last_login'])
                    return Response({
                        'refresh': str(refresh),
                        'access': str(refresh.access_token),
                        'message': 'Welcome back!',
                        'user_role': user_role,
                        'user_id': user.user_id,
                        f'{user_role}_created': created if user_role == 'owner' or user_role == 'higher-staff' else staff_created,
                    }, status=status.HTTP_200_OK)
            else:
                return Response({'message': 'Invalid credentials'}, status=status.HTTP_401_UNAUTHORIZED)
        else:
            return Response({'message': 'Email or password not provided'}, status=status.HTTP_400_BAD_REQUEST)


class PasswordResetRequestView(generics.GenericAPIView):
    serializer_class = PasswordResetRequestSerializer
    permission_classes = [AllowAny]

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response({"message": "Password reset link has been sent to your email."})


class PasswordResetConfirmView(generics.GenericAPIView):
    serializer_class = PasswordResetConfirmSerializer
    permission_classes = [AllowAny]

    def post(self, request, uid, token, *args, **kwargs):
        data = {'uid': uid, 'token': token, 'new_password': request.data.get('new_password')}
        serializer = self.get_serializer(data=data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response({"message": "Password has been reset successfully."})


class PasswordChangeView(generics.GenericAPIView):
    serializer_class = PasswordChangeSerializer
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        try:
            serializer = self.get_serializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response({"message": "Password has been changed successfully."})
        except Exception as e:
            return Response({"message": str(e)}, status=status.HTTP_400_BAD_REQUEST)


class OwnerAction(generics.UpdateAPIView):
    queryset = User.objects.all()
    permission_classes = [IsAuthenticated, IsAdmin]
    lookup_field = 'pk'

    def update(self, request, *args, **kwargs):
        user_id = kwargs.get('user_id')
        action = request.data.get('action')
        if not action:
            return Response({'message': 'Please select valid action.'}, status=status.HTTP_400_BAD_REQUEST)

        result = block_or_unblock(action, user_id)
        if result:
            return Response({'message': f'Owner has been {action}.'}, status=status.HTTP_200_OK)
        return Response({'message': 'Owner does not exist.'}, status=status.HTTP_404_NOT_FOUND)


class AdminAction(generics.UpdateAPIView):
    queryset = User.objects.all()
    permission_classes = [IsAuthenticated, IsAdmin]
    lookup_field = 'user_id'

    def update(self, request, *args, **kwargs):
        user_id = kwargs.get('user_id')
        action = kwargs.get('action')
        result = block_or_unblock(action, user_id)
        if result:
            return Response({'message': f'Admin has been {action}.'}, status=status.HTTP_200_OK)
        return Response({'message': f'Admin does not exist.'}, status=status.HTTP_404_NOT_FOUND)


class StaffAction(generics.UpdateAPIView):
    queryset = User.objects.all()
    permission_classes = [IsAuthenticated, IsOwner]
    lookup_field = 'user_id'

    def update(self, request, *args, **kwargs):
        user_id = kwargs.get('user_id')
        action = kwargs.get('action')
        result = block_or_unblock(action, user_id)
        if result:
            return Response({'message': f'Staff has been {action}.'}, status=status.HTTP_200_OK)
        return Response({'message': f'Staff does not exist.'}, status=status.HTTP_404_NOT_FOUND)


class CreateHigherStaffView(generics.UpdateAPIView):
    queryset = HigherStaffUser.objects.all()
    serializer_class = HigherStaffSerializer
    permission_classes = [IsAuthenticated, IsHigherStaff]
    lookup_field = 'user_id'

    def get_queryset(self):
        user_id = self.kwargs.get('user_id')
        return HigherStaffUser.objects.filter(user_id=user_id)

    def perform_update(self, serializer):
        serializer.save()
