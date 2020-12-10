from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from django.utils.timezone import make_aware

from rest_framework import status
from rest_framework.test import APIClient

from core.models import Patient, Address, Run, MasterRun, Vehicle
from ..serializers import MasterRunSerializer

import datetime

MASTER_RUN_API = reverse('heroad:master_run-list')


def sample_address(user, name='Patient home', address1='1 rue de la fontaine', city='Bordeaux', zip_code=33000):
    return Address.objects.create(user=user, name=name, address1=address1, city=city, zip_code=zip_code)


def sample_patient(user, address, firstname='testfirst', lastname='testlast', phone_number='0678987678'):
    return Patient.objects.create(user=user, address=address, firstname=firstname, lastname=lastname,
                                  phone_number=phone_number)


def sample_run(user, pick_up_location, deposit_location, master_run, patient, date=make_aware(datetime.datetime.now()),
               departure_time=make_aware(datetime.datetime.now()), arriving_time=make_aware(datetime.datetime.now())):
    return Run.objects.create(user=user, pick_up_location=pick_up_location, deposit_location=deposit_location,
                              master_run=master_run, departure_time=departure_time, arriving_time=arriving_time,
                              date=date, patient=patient)


def sample_master_run(user, vehicle, date=make_aware(datetime.datetime.now()), am=True):
    return MasterRun.objects.create(user=user, vehicle=vehicle, date=date, am=am)


def sample_vehicle(user, type='Ambulance', license_plate='AA-123-AA'):
    return Vehicle.objects.create(user=user, type=type, license_plate=license_plate)


def sample_user(email='test@gmail.com', password='testpass'):
    """Create a sample user"""
    return get_user_model().objects.create_user(email, password)


def detail_url(master_run_id):
    """Return master run detail url"""
    return reverse("heroad:master_run-detail", args=[master_run_id])


class PublicMasterRunApiTest(TestCase):
    """Test the publicly available master run API"""
    def setUp(self):
        self.client = APIClient()

    def test_login_requires(self):
        """Test that login is required to access the endpoint"""
        res = self.client.get(MASTER_RUN_API)

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateMasterRunApiTests(TestCase):
    """Test the master run API"""
    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            'test@gmail.com',
            'pass123'
        )
        self.client.force_authenticate(self.user)

    def test_retrieve_master_run_list(self):
        """Test retrieving master run list"""
        MasterRun.objects.create(
            user=self.user,
            date=make_aware(datetime.datetime.now()),
            am=True,
            vehicle=sample_vehicle(user=self.user)
        )
        MasterRun.objects.create(
            user=self.user,
            date=make_aware(datetime.datetime.now()),
            am=True,
            vehicle=sample_vehicle(user=self.user)
        )

        res = self.client.get(MASTER_RUN_API)
        master_runs = MasterRun.objects.all()
        serializer = MasterRunSerializer(master_runs, many=True)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_create_master_run(self):
        """Test creating a master run"""
        payload = {
            'user': self.user,
            'date': make_aware(datetime.datetime.now()),
            'am': True,
            'vehicle': sample_vehicle(user=self.user).id
        }

        res = self.client.post(MASTER_RUN_API, payload)

        exists = MasterRun.objects.filter(
            user=self.user,
            date=payload['date'],
            am=payload['am'],
            vehicle=payload['vehicle']
        ).exists()

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        self.assertTrue(exists)

    def test_partial_update_master_run(self):
        """Test updating a master run with patch"""
        master_run = sample_master_run(user=self.user, vehicle=sample_vehicle(user=self.user))

        payload = {
            'am': False,
            'pm': True
        }

        url = detail_url(master_run.id)
        res = self.client.patch(url, payload)
        master_run.refresh_from_db()

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(master_run.am, payload['am'])
        self.assertEqual(master_run.pm, payload['pm'])

    def test_full_update_master_run(self):
        """Test updating master run with put"""
        master_run = sample_master_run(user=self.user, vehicle=sample_vehicle(user=self.user))

        new_vehicle = sample_vehicle(user=self.user)
        payload = {
            'date': make_aware(datetime.datetime.now()),
            'vehicle': new_vehicle.id,
            'am': False,
            'pm': True
        }

        url = detail_url(master_run.id)
        res = self.client.put(url, payload)
        master_run.refresh_from_db()

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(master_run.am, payload['am'])
        self.assertEqual(master_run.pm, payload['pm'])
        self.assertEqual(master_run.vehicle, new_vehicle)

    def test_delete_master_run(self):
        """Test deleting a master run"""
        master_run = sample_master_run(user=self.user, vehicle=sample_vehicle(user=self.user))

        url = detail_url(master_run.id)
        res = self.client.delete(url)

        self.assertEqual(res.status_code, status.HTTP_204_NO_CONTENT)

    def test_create_master_run_with_drivers(self):
        """Test creating master run with drivers"""
        driver1 = sample_user('driver1@gmail.com', 'pass222')
        driver2 = sample_user('driver2@gmail.com', 'pass222')

        payload = {
            'user': self.user,
            'date': make_aware(datetime.datetime.now()),
            'am': True,
            'vehicle': sample_vehicle(user=self.user).id,
            'users': [driver1.id, driver2.id]
        }

        res = self.client.post(MASTER_RUN_API, payload)
        url = detail_url(res.data['id'])
        master_run = self.client.get(url)

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        self.assertEqual(len(master_run.data['users']), 2)
        self.assertIn(driver1.id, master_run.data['users'])
        self.assertIn(driver2.id, master_run.data['users'])

    def test_create_master_run_with_runs(self):
        """Test creating master runs with runs"""

        run1 = sample_run(user=self.user, deposit_location=sample_address(user=self.user),
                         pick_up_location=sample_address(user=self.user, address1='Mamie michon'),
                         master_run=sample_master_run(user=self.user, vehicle=sample_vehicle(user=self.user)),
                         patient=sample_patient(user=self.user, address=sample_address(user=self.user)))

        run2 = sample_run(user=self.user, deposit_location=sample_address(user=self.user),
                         pick_up_location=sample_address(user=self.user, address1='Mamie Fleury'),
                         master_run=sample_master_run(user=self.user, vehicle=sample_vehicle(user=self.user)),
                         patient=sample_patient(user=self.user, address=sample_address(user=self.user)))

        payload = {
            'user': self.user,
            'date': make_aware(datetime.datetime.now()),
            'am': True,
            'vehicle': sample_vehicle(user=self.user).id,
            'runs': [run1.id, run2.id]
        }

        res = self.client.post(MASTER_RUN_API, payload)

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        master_run = MasterRun.objects.get(id=res.data['id'])
        runs = master_run.runs.all()
        self.assertEqual(len(runs), 2)
        self.assertIn(run1, runs)
        self.assertIn(run2, runs)
