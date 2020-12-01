from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from rest_framework import status
from rest_framework.test import APIClient

from core.models import Patient, Address
from ..serializers import PatientSerializer

PATIENT_URL = reverse('heroad:patient-list')


def sample_address(user, name='Patient home', address1='1 rue de la fontaine', city='Bordeaux', zip_code=33000):
    return Address.objects.create(user=user, name=name, address1=address1, city=city, zip_code=zip_code)


def sample_patient(user, address, firstname='testfirst', lastname='testlast', phone_number='0678987678'):
    return Patient.objects.create(user=user, address=address, firstname=firstname, lastname=lastname,
                                  phone_number=phone_number)


def detail_url(patient_id):
    """Return patient detail url"""
    return reverse('heroad:patient-detail', args=[patient_id])


class PublicPatientApiTests(TestCase):
    """Test the publicly available patient API"""
    def setUp(self):
        self.client = APIClient()

    def test_login_requires(self):
        """Test that login is required to access the endpoint"""
        res = self.client.get(PATIENT_URL)
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivatePatientApiTests(TestCase):
    """Test the patient API"""

    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            'test@gmail.com',
            'pass123'
        )
        self.client.force_authenticate(self.user)

    def test_retrieve_patient_list(self):
        """Test retrieving patient list"""
        Patient.objects.create(
            user=self.user,
            firstname='Thierry',
            lastname='Henry',
            phone_number='0798765678',
            address=sample_address(self.user)
        )

        Patient.objects.create(
            user=self.user,
            firstname='Amandine',
            lastname='Henry',
            phone_number='0598765678',
            address=sample_address(self.user)
        )

        res = self.client.get(PATIENT_URL)

        patients = Patient.objects.all()
        serializer = PatientSerializer(patients, many=True)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_create_patient(self):
        """Test creating a patient"""
        payload = {
            'user': self.user,
            'firstname': 'Testfirst',
            'lastname': 'Testlast',
            'phone_number': '0756897687',
            'address': sample_address(self.user).id,
            'description': 'This is a description'
        }

        res = self.client.post(PATIENT_URL, payload)

        exists = Patient.objects.filter(
            user=self.user,
            firstname=res.data['firstname'],
            lastname=res.data['lastname'],
            phone_number=res.data['phone_number'],
            address=res.data['address'],
            description=res.data['description'],
        ).exists()

        self.assertTrue(exists)

    def test_create_patient_without_firstname(self):
        """Test creating a patient without firstname"""
        payload = {
            'user': self.user,
            'lastname': 'Testlast',
            'phone_number': 'Testphone',
            'address': sample_address(self.user).id,
            'description': 'This is a description'
        }

        res = self.client.post(PATIENT_URL, payload)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_patient_without_lastname(self):
        """Test creating a patient without lastname"""
        payload = {
            'user': self.user,
            'firstname': 'Testfirst',
            'phone_number': '0897898790',
            'address': sample_address(self.user).id,
            'description': 'This is a description'
        }

        res = self.client.post(PATIENT_URL, payload)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_patient_without_phone(self):
        """Test creating a patient without phone"""
        payload = {
            'user': self.user,
            'firstname': 'Testfirst',
            'lastname': 'Testlast',
            'address': sample_address(self.user).id,
            'description': 'This is a description'
        }

        res = self.client.post(PATIENT_URL, payload)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_patient_without_address(self):
        """Test creating a patient without address"""
        payload = {
            'user': self.user,
            'firstname': 'Testfirst',
            'lastname': 'Testlast',
            'phone_number': '0987987678',
            'description': 'This is a description'
        }

        res = self.client.post(PATIENT_URL, payload)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_patient_with_bad_phone(self):
        """Test creating patient with phone length superior to 9"""
        payload = {
            'user': self.user,
            'firstname': 'Testfirst',
            'lastname': 'Testlast',
            'phone_number': '0987978987890',
            'address': sample_address(self.user).id,
            'description': 'This is a description'
        }

        res = self.client.post(PATIENT_URL, payload)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_partial_patient_update(self):
        """Test updating patient with patch"""
        patient = sample_patient(user=self.user, address=sample_address(self.user))

        payload = {
            'firstname': 'New-firstname'
        }

        url = detail_url(patient.id)
        res = self.client.patch(url, payload)

        patient.refresh_from_db()

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(patient.firstname, payload['firstname'])

    def test_full_patient_update(self):
        """Test updating patient with put"""
        patient = sample_patient(user=self.user, address=sample_address(self.user))

        payload = {
            'firstname': 'New-firstname',
            'lastname': 'New-lastname',
            'phone_number': '0897876456',
            'address': sample_address(self.user).id
        }

        url = detail_url(patient.id)
        res = self.client.put(url, payload)

        patient.refresh_from_db()

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(patient.firstname, payload['firstname'])
        self.assertEqual(patient.lastname, payload['lastname'])
        self.assertEqual(patient.phone_number, payload['phone_number'])
        self.assertEqual(patient.address.id, payload['address'])

    def test_delete_patient(self):
        """Test deleting patient"""
        patient = sample_patient(user=self.user, address=sample_address(self.user))

        url = detail_url(patient.id)
        res = self.client.delete(url)

        self.assertEqual(res.status_code, status.HTTP_204_NO_CONTENT)
