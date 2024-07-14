# views.py
from django.utils import timezone
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django.views.generic import UpdateView
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, generics

from Utils.Core.permissions import IsStaff, IsOwner
from Utils.Database.Database_Routing.add_database import add_database
from authentication.models import User, StaffAccess
from .models import Staff

import os
import logging

from .serializer import StaffSerializer, UpdateStaffAccessSerializer


class StaffListView(APIView):
    def get(self, request, business_id):
        db_name = f"{business_id}{os.getenv('DB_NAME_SECONDARY')}"

        # Ensure the dynamic database connection is set up
        add_database(db_name)

        try:
            # Query the Staff model using the determined database
            staff_list = Staff.objects.using(db_name).all()
            serializer = StaffSerializer(staff_list, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Exception as e:
            logging.error(f"Error retrieving staff list for database {db_name}: {e}")
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class UpdateStaffView(generics.UpdateAPIView):
    queryset = User.objects.all()
    permission_classes = [IsAuthenticated, IsStaff]

    def update(self, request, *args, **kwargs):
        user_id = kwargs.get('user_id')
        update_data = request.data

        user = get_object_or_404(User, user_id=user_id)
        db_user_id = user.user_id
        business_id = user.business_id

        db_name = f'{business_id}{os.getenv('DB_NAME_SECONDARY')}'

        add_database(db_name)

        firstname = update_data.get('firstname')
        lastname = update_data.get('lastname')

        try:
            staff = Staff.objects.using(db_name).get(user_id=db_user_id)

            staff.firstname = firstname
            staff.lastname = lastname
            staff.updated_at = timezone.now()

            staff.save(using=db_name)
            serializer = StaffSerializer(staff)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Staff.DoesNotExist:
            return Response({'error': 'Staff not found'}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({'error': f'{str(e)}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class StaffView(generics.GenericAPIView):
    permission_classes = [IsAuthenticated, IsStaff]

    def get(self, request, *args, **kwargs):
        user_id = kwargs.get('user_id')
        user = get_object_or_404(User, user_id=user_id)
        business_id = user.business_id
        db_name = f"{business_id}{os.getenv('DB_NAME_SECONDARY')}"

        add_database(db_name)

        try:
            staff = Staff.objects.using(db_name).get(user_id=user.user_id)
            serializer = StaffSerializer(staff)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Exception as e:
            logging.error(f"Error retrieving staff list for database {db_name}: {e}")
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class UpdateStaffAccessView(generics.UpdateAPIView):
    queryset = User.objects.all()
    permission_classes = [IsAuthenticated, IsOwner]
    serializer_class = UpdateStaffAccessSerializer
    lookup_field = 'user_id'

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        user_id = instance.user_id

        new_permissions = request.data.get('permissions', [])
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        # Update permissions
        updated_permissions = serializer.update_permissions(user_id=user_id, new_permissions=new_permissions)

        # Serialize and return the updated permissions
        response_serializer = UpdateStaffAccessSerializer(updated_permissions, many=True)
        return Response(response_serializer.data)
