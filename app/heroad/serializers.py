from rest_framework import serializers

from core.models import Address, Vehicle, Patient, Run, MasterRun, User


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


class RunSerializer(serializers.ModelSerializer):
    """Serializer for run objects"""

    pick_up_location = serializers.PrimaryKeyRelatedField(queryset=Address.objects.all())
    deposit_location = serializers.PrimaryKeyRelatedField(queryset=Address.objects.all())

    master_run = serializers.PrimaryKeyRelatedField(queryset=MasterRun.objects.all())
    patient = serializers.PrimaryKeyRelatedField(queryset=Patient.objects.all())

    class Meta:
        model = Run
        fields = ('id', 'date', 'departure_time', 'arriving_time', 'pick_up_location', 'deposit_location',
                  'is_return_path', 'comments', 'master_run', 'patient', )
        read_only_fields = ('id', )


class MasterRunSerializer(serializers.ModelSerializer):
    """Serializer for master run object"""

    patients = serializers.PrimaryKeyRelatedField(queryset=Patient.objects.all(), many=True)
    vehicle = serializers.PrimaryKeyRelatedField(queryset=Vehicle.objects.all())
    runs = serializers.PrimaryKeyRelatedField(queryset=Run.objects.all(), many=True)

    class Meta:
        model = MasterRun
        fields = ('id', 'comments', 'date', 'patients', 'am', 'pm', 'vehicle', 'runs', 'drivers', )
        read_only_fields = ('id', )
