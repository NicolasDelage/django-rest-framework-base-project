from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework import viewsets, mixins, status
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated

# Create your views here.

from core.models import Address, Vehicle, Patient, Run, MasterRun
from . import serializers


class AddressViewSet(viewsets.ModelViewSet, mixins.CreateModelMixin):
    """Manage address in the database"""
    authentication_classes = (TokenAuthentication, )
    permission_classes = (IsAuthenticated, )

    queryset = Address.objects.all()
    serializer_class = serializers.AddressSerializer

    def perform_create(self, serializer):
        """Create a new object"""
        serializer.save(user=self.request.user)


class VehicleViewSet(viewsets.ModelViewSet, mixins.CreateModelMixin):
    """Manage vehicle in the database"""
    authentication_classes = (TokenAuthentication, )
    permission_classes = (IsAuthenticated, )

    queryset = Vehicle.objects.all()
    serializer_class = serializers.VehicleSerializer

    def perform_create(self, serializer):
        """Create a new object"""
        serializer.save(user=self.request.user)


class PatientViewSet(viewsets.ModelViewSet, mixins.CreateModelMixin):
    """Manage patient in the database"""
    authentication_classes = (TokenAuthentication, )
    permission_classes = (IsAuthenticated, )

    queryset = Patient.objects.all()
    serializer_class = serializers.PatientSerializer

    def perform_create(self, serializer):
        """Create a new object"""
        serializer.save(user=self.request.user)


class RunViewSet(viewsets.ModelViewSet, mixins.CreateModelMixin):
    """Manage run in the database"""
    authentication_classes = (TokenAuthentication, )
    permission_classes = (IsAuthenticated, )

    queryset = Run.objects.all()
    serializer_class = serializers.RunSerializer

    def perform_create(self, serializer):
        """Create a new object"""
        serializer.save(user=self.request.user)


class MasterRunViewSet(viewsets.ModelViewSet, mixins.CreateModelMixin):
    """Manage master run in the database"""
    authentication_classes = (TokenAuthentication, )
    permission_classes = (IsAuthenticated, )

    queryset = MasterRun.objects.all()
    serializer_class = serializers.MasterRunSerializer

    def perform_create(self, serializer):
        """Create a new object"""
        serializer.save(user=self.request.user)
