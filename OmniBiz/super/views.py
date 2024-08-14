from rest_framework import generics, status
from rest_framework.permissions import IsAuthenticated, AllowAny

from Utils.Core.permissions import IsAdmin
from owner.models import Owner
from super.models import Super
from super.serializer import SuperSerializer
from rest_framework.response import Response
from owner.serializer import OwnerSerializer
from business.models import Business
from authentication.models import User, HigherStaffAccess


# Create your views here.
class SuperCreateView(generics.CreateAPIView):
    queryset = Super.objects.all()
    serializer_class = SuperSerializer
    permission_classes = [IsAuthenticated, IsAdmin]


class GetAllOwners(generics.ListAPIView):
    queryset = Owner.objects.all()
    permission_classes = [IsAuthenticated, IsAdmin]

    def get(self, request, *args, **kwargs):
        owners_details = []
        owners = Owner.objects.all()
        for owner in owners:
            user = User.objects.get(pk=owner.user_id)
            businesses = Business.objects.filter(owner=user.user_id)
            business_list = [{'business_id': business.business_id, 'business_name': business.business_name} for business
                             in businesses]
            owner_data = {
                'owner_id': owner.owner_id,
                'user_id': user.user_id,
                'owner_name': owner.first_name,
                'phone_number': owner.phone_number,
                'business_count': owner.business_count,
                'subscription_amount': owner.subscription_amount,
                'is_active': user.is_active,
                'businesses': business_list,
            }
            owners_details.append(owner_data)
        return Response(owners_details, status=status.HTTP_200_OK)


class GetAllBusinesses(generics.ListAPIView):
    queryset = Business.objects.all()
    permission_classes = [IsAuthenticated, IsAdmin]

    def get(self, request, *args, **kwargs):
        try:
            business_data = []
            businesses = Business.objects.all()
            for business in businesses:
                owner = Owner.objects.get(user_id=business.owner_id)
                owner_details = [
                    {'owner_id': business.owner_id, 'owner': owner.first_name, 'phone_number': owner.phone_number}]
                business_details = {
                    'business_id': business.business_id,
                    'business_name': business.business_name,
                    'business_address': business.business_address,
                    'phone_number': business.phone_number,
                    'created_at': business.created_at,
                    'subscription_trial_ended_at': business.subscription_trial_ended_at,
                    'subscription_ended_at': business.subscription_ended_at,
                    'subscription_count': business.subscription_count,
                    'owner': owner_details,
                    'is_active': business.is_active,
                }
                business_data.append(business_details)
            return Response(business_data, status=status.HTTP_200_OK)
        except Business.DoesNotExist:
            return Response({'business_data': []}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class GetAllAccesses(generics.ListAPIView):
    permission_classes = [AllowAny]

    def get(self, request, *args, **kwargs):
        accesses = []
        try:
            staff_accesses = Super.objects.all()
            for staff_access in staff_accesses:
                staff_access_details = {
                    'permission_id': staff_access.id,
                    'permission_name': staff_access.permission,
                    'description': staff_access.description,
                }
                accesses.append(staff_access_details)
            return Response(accesses, status=status.HTTP_200_OK)
        except Super.DoesNotExist:
            return Response({'accesses': []}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class GetHigherStaffAccess(generics.ListAPIView):
    permission_classes = [AllowAny]

    def get(self, request, *args, **kwargs):
        user_id = kwargs.get('user_id')
        if not user_id:
            return Response({'higher_staff_access': []}, status=status.HTTP_404_NOT_FOUND)

        try:
            higher_staff_accesses = HigherStaffAccess.objects.filter(user_id=user_id)
            access_business = []
            for higher_staff_access in higher_staff_accesses:
                if higher_staff_access.status:
                    access_business.append(higher_staff_access.business_id)
                else:
                    continue
            return Response(access_business, status=status.HTTP_200_OK)
        except HigherStaffAccess.DoesNotExist:
            return Response({'higher_staff_access': []}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)