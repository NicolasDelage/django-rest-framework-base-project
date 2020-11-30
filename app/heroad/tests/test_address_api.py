from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from rest_framework import status
from rest_framework.test import APIClient

from core.models import Address
from ..serializers import AddressSerializer

ADDRESS_URL = reverse('heroad:address-list')


def detail_url(address_id):
    """Return address detail url"""
    return reverse('heroad:address-detail', args=[address_id])


def sample_address(user, name='home', address1='place des quinconces', zip_code=33000, city='Bordeaux'):
    return Address.objects.create(user=user, name=name, address1=address1, zip_code=zip_code, city=city)


class PublicAddressApiTests(TestCase):
    """Test the publicly available ingredients API"""

    def setUp(self):
        self.client = APIClient()

    def test_login_requires(self):
        """Test that login is required to access the endpoint"""
        res = self.client.get(ADDRESS_URL)

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateAddressApiTests(TestCase):
    """Test the private address API"""

    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            'test@gmail.com',
            'pass123'
        )

        self.client.force_authenticate(self.user)

    def test_retrieve_address_list(self):
        """Test retrieving a list of address"""
        Address.objects.create(
            user=self.user,
            name='Work',
            address1='14 rue des Quinconces',
            city='Bordeaux',
            zip_code=33000
        )
        Address.objects.create(
            user=self.user,
            name='Home',
            address1='33 rue des sols',
            city='Bordeaux',
            zip_code=33000
        )

        res = self.client.get(ADDRESS_URL)

        address = Address.objects.all().order_by('-name')
        serializer = AddressSerializer(address, many=True)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_create_address(self):
        """Test creating a new address"""
        payload = {
            'user': self.user,
            'name': 'Work',
            'address1': '14 rue des Quinconces',
            'city': 'Bordeaux',
            'zip_code': 33000
        }

        self.client.post(ADDRESS_URL, payload)

        exists = Address.objects.filter(
            user=self.user,
            name=payload['name']
        ).exists()

        self.assertTrue(exists)

    def test_partial_update_address(self):
        """Test updating an address with patch"""
        address = sample_address(self.user)

        payload = {'name': 'Work'}
        url = detail_url(address.id)
        self.client.patch(url, payload)

        address.refresh_from_db()
        self.assertEqual(address.name, payload['name'])

    def test_full_update_address(self):
        """Test updating an address with put"""
        address = sample_address(self.user)

        payload = {
            'name': 'kiné',
            'address1': '33 rue du loup',
            'city': 'Marmande',
            'zip_code': 47200
        }
        url = detail_url(address.id)
        self.client.put(url, payload)

        address.refresh_from_db()
        self.assertEqual(address.name, payload['name'])
        self.assertEqual(address.address1, payload['address1'])
        self.assertEqual(address.city, payload['city'])
        self.assertEqual(address.zip_code, payload['zip_code'])

    def test_delete_address(self):
        """Test deleting an address"""
        address = sample_address(self.user)

        url = detail_url(address.id)
        res = self.client.delete(url)

        self.assertEqual(res.status_code, status.HTTP_204_NO_CONTENT)
