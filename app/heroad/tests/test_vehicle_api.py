from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from rest_framework import status
from rest_framework.test import APIClient

from core.models import Vehicle
from ..serializers import VehicleSerializer

VEHICLE_URL = reverse('heroad:vehicle-list')


def detail_url(vehicle_id):
    """Return vehicle detail url"""
    return reverse('heroad:vehicle-detail', args=[vehicle_id])


def sample_vehicle(user, type='Ambulance', license_plate='AA-123-AA'):
    return Vehicle.objects.create(user=user, type=type, license_plate=license_plate)


class PublicVehicleApiTests(TestCase):
    """Test the publicly avaiblable ingredient API"""

    def setUp(self):
        self.client = APIClient()

    def test_login_requires(self):
        """Test that login is required to access the enpoint"""
        res = self.client.get(VEHICLE_URL)

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateVehicleApiTests(TestCase):
    """Test the Vehicle private API"""

    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            'test@gmail.com',
            'pass123'
        )

        self.client.force_authenticate(self.user)

    def test_retrieve_vehicle_list(self):
        """Test retrieving a list of vehicle"""
        Vehicle.objects.create(
            user=self.user,
            type='Ambulance',
            license_plate='AA-123-AA'
        )
        Vehicle.objects.create(
            user=self.user,
            type='VSL',
            license_plate='BB-123-BB'
        )

        res = self.client.get(VEHICLE_URL)

        vehicles = Vehicle.objects.all()
        serializer = VehicleSerializer(vehicles, many=True)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_create_vehicle(self):
        """Test creating a vehicle"""
        payload = {
            'user': self.user,
            'type': 'Ambulance',
            'license_plate': 'AA-123-AA'
        }

        self.client.post(VEHICLE_URL, payload)

        exists = Vehicle.objects.filter(
            user=self.user,
            type=payload['type'],
            license_plate=payload['license_plate']
        )

        self.assertTrue(exists)

    def test_partial_update_vehicle(self):
        """Test update vehicle with patch"""
        vehicle = sample_vehicle(user=self.user)

        payload = {
            'type': 'VSL'
        }
        url = detail_url(vehicle.id)
        self.client.patch(url, payload)

        vehicle.refresh_from_db()
        self.assertEqual(vehicle.type, payload['type'])

    def test_full_update_vehicle(self):
        """Test update vehicle with put"""
        vehicle = sample_vehicle(self.user)

        payload = {
            'type': 'VSL',
            'license_plate': 'BB-123-BB'
        }
        url = detail_url(vehicle.id)

        self.client.put(url, payload)

        vehicle.refresh_from_db()

        self.assertEqual(vehicle.type, payload['type'])
        self.assertEqual(vehicle.license_plate, payload['license_plate'])

    def test_delete_vehicle(self):
        """Test deleting a vehicle"""
        vehicle = sample_vehicle(user=self.user)

        url = detail_url(vehicle.id)
        res = self.client.delete(url)

        self.assertEqual(res.status_code, status.HTTP_204_NO_CONTENT)

    def test_create_vehicle_with_bad_type(self):
        """Test creating a vehicle with a bad type"""

        payload = {
            'user': self.user,
            'type': 'Bad',
            'license_plate': 'AA-123-AA'
        }

        res = self.client.post(VEHICLE_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
