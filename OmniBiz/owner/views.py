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
    lookup_field = 'owner_id'

    def get_queryset(self):
        return Owner.objects.filter(user_id=self.request.user)

    def perform_update(self, serializer):
        serializer.save()


class GetOwnerView(generics.RetrieveAPIView):
    queryset = Owner.objects.all()
    serializer_class = OwnerSerializer
    permission_classes = [IsAuthenticated]
    lookup_field = 'user_id'

    def get_owner_object(self):
        user = self.request.user
        return Owner.objects.get(user_id=user)
