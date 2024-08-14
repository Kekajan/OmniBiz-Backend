from rest_framework import generics, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework_simplejwt.authentication import JWTAuthentication

from Utils.Core.permissions import IsAdmin
from owner.models import Owner
from owner.serializer import OwnerSerializer


class CreateOwnerView(generics.CreateAPIView):
    queryset = Owner.objects.all()
    serializer_class = OwnerSerializer

    def perform_create(self, serializer):
        serializer.save()


class UpdateOwnerView(generics.UpdateAPIView):
    queryset = Owner.objects.all()
    serializer_class = OwnerSerializer
    permission_classes = [IsAuthenticated]
    lookup_field = 'user_id'

    def get_queryset(self):
        return Owner.objects.filter(user_id=self.request.user)

    def perform_update(self, serializer):
        serializer.save()


class GetOwnerView(generics.RetrieveAPIView):
    queryset = Owner.objects.all()
    permission_classes = [IsAuthenticated]
    lookup_field = 'user_id'

    def get(self, request, *args, **kwargs):
        user = request.user
        owner = self.get_object()  # Automatically fetches the owner based on user_id
        owner_data = {
            'owner_id': owner.owner_id,
            'first_name': owner.first_name,
            'last_name': owner.last_name,
            'phone_number': owner.phone_number,
            'business_count': owner.business_count,
            'profit': owner.profit,
            'subscription_amount': owner.subscription_amount,
            'is_active': user.is_active,
        }
        return Response(owner_data)
