import os

from rest_framework import generics
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status

from Utils.Core.permissions import IsOwner, IsAdmin
from Utils.Database.Database_Routing.add_database import add_database
from authentication.models import User
from business.models import Business
from business.serializer import BusinessSerializer
from staff.models import Staff


# Create your views here.
class CreateBusinessView(generics.CreateAPIView):
    queryset = Business.objects.all()
    serializer_class = BusinessSerializer
    permission_classes = [IsAuthenticated, IsOwner]


class UpdateBusinessView(generics.UpdateAPIView):
    queryset = Business.objects.all()
    serializer_class = BusinessSerializer
    permission_classes = [IsAuthenticated]
    lookup_field = 'business_id'

    def get_queryset(self):
        business = Business.objects.filter(business_id=self.kwargs['business_id'])
        return business

    def perform_update(self, serializer):
        serializer.save(business_id=self.kwargs['business_id'])
        return serializer


class GetBusinessView(generics.RetrieveAPIView):
    queryset = Business.objects.all()
    serializer_class = BusinessSerializer
    permission_classes = [IsAuthenticated]
    lookup_field = 'business_id'

    def get_queryset(self):
        business = Business.objects.filter(business_id=self.kwargs['business_id'])
        return business


class BlockBusinessView(generics.GenericAPIView):
    queryset = Business.objects.all()
    permission_classes = [IsAuthenticated, IsAdmin]

    def get(self, request, *args, **kwargs):
        business_id = kwargs.get('business_id')
        action = kwargs.get('action')
        db_name = f'{business_id}{os.getenv('DB_NAME_SECONDARY')}'

        add_database(db_name)

        try:
            staffs = Staff.objects.using(db_name).all()
            print(staffs)
            staff_user_id = [staff.user_id for staff in staffs]
            print(staff_user_id)
            for staff_id in staff_user_id:
                print(staff_id)
                if action == 'block':
                    User.objects.filter(user_id=staff_id).update(is_active=False)
                    Business.objects.filter(business_id=business_id).update(is_active=False)
                elif action == 'unblock':
                    User.objects.filter(user_id=staff_id).update(is_active=True)
                    Business.objects.filter(business_id=business_id).update(is_active=True)
                else:
                    return Response({'message': 'Please select valid action'}, status=status.HTTP_400_BAD_REQUEST)
            return Response({'message': f'{business_id} is {action}ed'}, status=status.HTTP_200_OK)
        except Staff.DoesNotExist:
            return Response({'error': 'There are have no users.'}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class GetBusinessByOwnerView(generics.GenericAPIView):
    queryset = Business.objects.all()
    serializer_class = BusinessSerializer
    permission_classes = [IsAuthenticated, IsOwner]

    def get(self, request, *args, **kwargs):
        owner_user_id = kwargs.get('user_id')

        businesses = Business.objects.filter(owner_id=owner_user_id)
        serializer = BusinessSerializer(businesses, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
