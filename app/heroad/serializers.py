from rest_framework import serializers

from core.models import Address, Vehicle


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
