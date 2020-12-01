from rest_framework import serializers

from core.models import Address, Vehicle, Patient


class AddressSerializer(serializers.ModelSerializer):
    """Serializer for address objects"""

    class Meta:
        model = Address
        fields = ('id', 'name', 'address1', 'address2', 'city', 'zip_code',)
        read_only_Fields = ('id',)


class VehicleSerializer(serializers.ModelSerializer):
    """Serializer for address objects"""

    class Meta:
        model = Vehicle
        fields = ('id', 'type', 'license_plate',)
        read_only_fields = ('id',)


class PatientSerializer(serializers.ModelSerializer):
    """Serializer for patient objects"""

    address = serializers.PrimaryKeyRelatedField(queryset=Address.objects.all())

    class Meta:
        model = Patient
        fields = ('id', 'firstname', 'lastname', 'special', 'phone_number', 'description', 'address')
        read_only_fields = ('id',)
