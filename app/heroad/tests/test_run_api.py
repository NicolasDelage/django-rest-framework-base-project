from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from django.utils.timezone import make_aware

from rest_framework import status
from rest_framework.test import APIClient

from core.models import Patient, Address, Run, MasterRun, Vehicle
from ..serializers import RunSerializer

import datetime

RUN_URL = reverse('heroad:run-list')


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


def detail_url(run_id):
    """Return run detail url"""
    return reverse('heroad:run-detail', args=[run_id])


class PublicRunApiTests(TestCase):
    """Test the publicly available run API"""
    def setUp(self):
        self.client = APIClient()

    def test_login_requires(self):
        """Test that login is required to access the endpoint"""
        res = self.client.get(RUN_URL)
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateRunApiTests(TestCase):
    """Test the run API"""
    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            'test@gmail.com',
            'pass123'
        )

        self.client.force_authenticate(self.user)

    def test_retrieve_run_list(self):
        """Test retrieving run list"""

        Run.objects.create(
            user=self.user,
            date=make_aware(datetime.datetime.now()),
            departure_time=make_aware(datetime.datetime.now()),
            arriving_time=make_aware(datetime.datetime.now()),
            pick_up_location=sample_address(user=self.user),
            deposit_location=sample_address(user=self.user, address1='Hopital saint-pierre'),
            master_run=sample_master_run(user=self.user, vehicle=sample_vehicle(self.user)),
            patient=sample_patient(user=self.user, address=sample_address(user=self.user))
        )

        Run.objects.create(
            user=self.user,
            date=make_aware(datetime.datetime.now()),
            departure_time=make_aware(datetime.datetime.now()),
            arriving_time=make_aware(datetime.datetime.now()),
            pick_up_location=sample_address(user=self.user),
            deposit_location=sample_address(user=self.user, address1='Hopital notre dame'),
            master_run=sample_master_run(user=self.user, vehicle=sample_vehicle(self.user)),
            patient=sample_patient(user=self.user, address=sample_address(user=self.user))
        )

        res = self.client.get(RUN_URL)

        runs = Run.objects.all()
        serializer = RunSerializer(runs, many=True)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_create_run(self):
        """Test creating a run"""
        payload = {
            'user': self.user,
            'date': make_aware(datetime.datetime.now()),
            'departure_time': make_aware(datetime.datetime.now()),
            'arriving_time': make_aware(datetime.datetime.now()),
            'pick_up_location': sample_address(user=self.user).id,
            'deposit_location': sample_address(user=self.user).id,
            'master_run': sample_master_run(user=self.user, vehicle=sample_vehicle(user=self.user)).id,
            'patient': sample_patient(user=self.user, address=sample_address(user=self.user)).id
        }

        res = self.client.post(RUN_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)

    def test_partial_update_run(self):
        """Test updating run with patch"""
        run = sample_run(user=self.user, deposit_location=sample_address(user=self.user),
                         pick_up_location=sample_address(user=self.user, address1='Mamie michon'),
                         master_run=sample_master_run(user=self.user, vehicle=sample_vehicle(user=self.user)),
                         patient=sample_patient(user=self.user, address=sample_address(user=self.user)))

        new_deposit_location = sample_address(user=self.user, address1='Morgue')
        payload = {
            'deposit_location': new_deposit_location.id
        }

        url = detail_url(run.id)
        res = self.client.patch(url, payload)

        run.refresh_from_db()

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(run.deposit_location, new_deposit_location)

    def test_full_update_run(self):
        """Test updating run with put"""
        run = sample_run(user=self.user, deposit_location=sample_address(user=self.user),
                         pick_up_location=sample_address(user=self.user, address1='Mamie michon'),
                         master_run=sample_master_run(user=self.user, vehicle=sample_vehicle(user=self.user)),
                         patient=sample_patient(user=self.user, address=sample_address(user=self.user)))

        new_deposit_location = sample_address(user=self.user, address1='new deposit location')
        new_pick_up_location = sample_address(user=self.user, address1='new pick up location')
        new_patient = sample_patient(user=self.user, address=sample_address(user=self.user), firstname='Henriette')
        new_master_run = sample_master_run(user=self.user, vehicle=sample_vehicle(user=self.user,
                                                                                  license_plate='RR-333-NN'))

        payload = {
            'date': make_aware(datetime.datetime.now()),
            'departure_time': make_aware(datetime.datetime.now()),
            'arriving_time': make_aware(datetime.datetime.now()),
            'deposit_location': new_deposit_location.id,
            'pick_up_location': new_pick_up_location.id,
            'master_run': new_master_run.id,
            'patient': new_patient.id
        }

        url = detail_url(run.id)
        res = self.client.put(url, payload)
        run.refresh_from_db()

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(run.date, payload['date'])
        self.assertEqual(run.departure_time, payload['departure_time'])
        self.assertEqual(run.arriving_time, payload['arriving_time'])
        self.assertEqual(run.deposit_location, new_deposit_location)
        self.assertEqual(run.pick_up_location, new_pick_up_location)
        self.assertEqual(run.master_run, new_master_run)
        self.assertEqual(run.patient, new_patient)

    def test_delete_run(self):
        """Test deleting a run"""
        run = sample_run(user=self.user, deposit_location=sample_address(user=self.user),
                         pick_up_location=sample_address(user=self.user, address1='Mamie michon'),
                         master_run=sample_master_run(user=self.user, vehicle=sample_vehicle(user=self.user)),
                         patient=sample_patient(user=self.user, address=sample_address(user=self.user)))

        url = detail_url(run.id)
        res = self.client.delete(url)

        self.assertEqual(res.status_code, status.HTTP_204_NO_CONTENT)
