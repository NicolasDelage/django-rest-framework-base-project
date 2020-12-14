from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework import viewsets, mixins, status
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated
from django_filters import rest_framework as filters
from django.db.models import Q

import datetime

from core.models import Address, Vehicle, Patient, Run, MasterRun
from . import serializers

# Create filters here


def master_run_filter_search(queryset, name, value):
    return queryset.filter(Q(comments__icontains=value) | Q(vehicle__license_plate__icontains=value))


def location_filter(queryset, name, value):
    return queryset.filter(Q(**{name + '__address1__icontains': value}) | Q(**{name + '__address2__icontains': value}) |
                           Q(**{name + '__city__icontains': value}) | Q(**{name + '__zip_code__icontains': value}) |
                           Q(**{name + '__name__icontains': value}))


def patient_filter(queryset, name, value):
    return queryset.filter(Q(patient__firstname__icontains=value) | Q(patient__lastname__icontains=value))


class MasterRunFilter(filters.FilterSet):
    """Filter master runs"""

    date = filters.DateFilter(field_name='date', lookup_expr='gte')
    comments = filters.CharFilter(lookup_expr='icontains')
    search = filters.CharFilter(field_name='search', method=master_run_filter_search)

    class Meta:
        model = MasterRun
        fields = ['date', 'am', 'pm', 'comments']


class RunFilter(filters.FilterSet):
    """Filter runs"""

    date = filters.DateFilter(field_name='date', lookup_expr='gte')
    departure_time = filters.CharFilter(field_name='departure_time', lookup_expr='gte')
    arriving_time = filters.CharFilter(field_name='arriving_time', lookup_expr='gte')
    pick_up_location = filters.CharFilter(field_name='pick_up_location', method=location_filter)
    deposit_location = filters.CharFilter(field_name='pick_up_location', method=location_filter)
    patient = filters.CharFilter(field_name='patient', method=patient_filter)

    class Meta:
        model = Run
        fields = ['date', 'departure_time', 'arriving_time', 'pick_up_location', 'deposit_location', 'comments',
                  'master_run', 'patient']


# Create views here


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
    filterset_class = RunFilter

    def perform_create(self, serializer):
        """Create a new object"""
        serializer.save(user=self.request.user)


class MasterRunViewSet(viewsets.ModelViewSet, mixins.CreateModelMixin):
    """Manage master run in the database"""
    authentication_classes = (TokenAuthentication, )
    permission_classes = (IsAuthenticated, )

    queryset = MasterRun.objects.all()
    serializer_class = serializers.MasterRunSerializer
    filterset_class = MasterRunFilter

    def perform_create(self, serializer):
        """Create a new object"""
        serializer.save(user=self.request.user)
