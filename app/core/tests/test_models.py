from unittest.mock import patch

from django.test import TestCase
from django.contrib.auth import get_user_model
from django.utils import timezone

from .. import models

import datetime


def sample_user(email='test@gmail.com', password='testpass'):
    """Create a sample user"""
    return get_user_model().objects.create_user(email, password)


def sample_location(user, address1='Victoire', city='Bordeaux', zip_code=33000):
    """Create sample location"""
    return models.Address.objects.create(user=user, address1=address1, city=city, zip_code=zip_code)


def sample_vehicle(user, type='VSL', license_plate='AA-123-AA'):
    """Create sample vehicle"""
    return models.Vehicle.objects.create(user=user, type=type, license_plate=license_plate)


def sample_master_run(user, vehicle, am=True, date=datetime.datetime.now(tz=timezone.utc)):
    """Create sample master run"""
    return models.MasterRun.objects.create(user=user, vehicle=vehicle, am=am, date=date)


def sample_patient(user, address, firstname='John', lastname='Doe', phone_number='0678645763'):
    """Create sample patient"""
    return models.Patient.objects.create(user=user, address=address, firstname=firstname, lastname=lastname,
                                         phone_number=phone_number)


def sample_address(user):
    """Create sample address"""
    return models.Address.objects.create(user=user, address1='Victoire', city='Bordeaux', zip_code=33000)


class ModelTests(TestCase):

    def test_create_user_with_email_successful(self):
        """Test creating a new user with an email is successful"""
        email = 'test@gmail.com'
        password = 'Testpass123'
        user = get_user_model().objects.create_user(
            email=email,
            password=password
        )

        self.assertEqual(user.email, email)
        self.assertTrue(user.check_password(password))

    def test_new_user_email_normalized(self):
        """Test the email for a new user is normalized"""
        email = 'test@GMAIL.COM'
        user = get_user_model().objects.create_user(email, 'test123')

        self.assertEqual(user.email, email.lower())

    def test_new_user_invalid_email(self):
        """Test creating user with no email raises error"""
        with self.assertRaises(ValueError):
            get_user_model().objects.create_user(None, 'test123')

    def test_create_new_superuser(self):
        """Test creating a new superuser"""
        user = get_user_model().objects.create_superuser(
            'test@gmail.com',
            'test123',
        )

        self.assertTrue(user.is_superuser)
        self.assertTrue(user.is_staff)
