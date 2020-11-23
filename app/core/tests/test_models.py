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

    def test_tag_str(self):
        """Test the tag string representation"""
        tag = models.Tag.objects.create(
            user=sample_user(),
            name='Vegan'
        )

        self.assertEqual(str(tag), tag.name)

    def test_ingredients_str(self):
        """Test the ingredient string representation"""
        ingredient = models.Ingredient.objects.create(
            user=sample_user(),
            name='Cucumber'
        )

        self.assertEqual(str(ingredient), ingredient.name)

    def test_recipe_str(self):
        """Test the recipe string representation"""
        recipe = models.Recipe.objects.create(
            user=sample_user(),
            title='Steak and mushroom sauce',
            time_minutes=5,
            price=5.00
        )

        self.assertEqual(str(recipe), recipe.title)

    @patch('uuid.uuid4')
    def test_recipe_filename_uuid(self, mock_uuid):
        """Test that image is save in the correct location"""
        uuid = 'test-uuid'
        mock_uuid.return_value = uuid
        file_path = models.recipe_image_file_path(None, 'myimage.jpg')

        exp_path = f'uploads/recipe/{uuid}.jpg'
        self.assertEqual(file_path, exp_path)

    # Test heroad

    def test_address(self):
        """Test the address string representation"""
        address = models.Address.objects.create(
            user=sample_user(),
            name='Address test',
            address1='Roubineau',
            address2='',
            zip_code=47120,
            city='Soumensac'
        )

        address_concat = address.address1 + (' ' + address.address2 if address.address2 else '')
        string_name = '{}, {}, {}'.format(address.city, address_concat, address.zip_code)
        self.assertEqual(str(address), string_name)

    def test_run(self):
        """Test the run string representation"""
        user = sample_user()
        run = models.Run.objects.create(
            user=user,
            date=datetime.datetime.now(tz=timezone.utc),
            departure_time=datetime.datetime.now(tz=timezone.utc),
            arriving_time=datetime.datetime.now(tz=timezone.utc),
            pick_up_location=sample_location(user=user, address1='Chartrons'),
            deposit_location=sample_location(user=user),
            is_return_path=False,
            comments='This is a comment',
            master_run=sample_master_run(user, sample_vehicle(user)),
            patient=sample_patient(user, sample_address(user))
        )
        self.assertEqual(str(run), f'{run.date} {run.deposit_location}')

    def test_master_run(self):
        """Test the master run string representation"""
        user = sample_user()
        user2 = sample_user('test2@gmail.com')

        master_run = models.MasterRun.objects.create(
            user=user,
            comments='This is a comment',
            am=True,
            pm=False,
            date=datetime.datetime.now(tz=timezone.utc),
            vehicle=sample_vehicle(user=user)
        )
        master_run.users.add(user, user2)

        self.assertEqual(str(master_run), str(master_run.users))

    def test_vehicle(self):
        """Test the vehicle string representation"""

        vehicle = models.Vehicle.objects.create(
            user=sample_user(),
            type='Ambulance',
            license_plate='AA-123-AA'
        )

        self.assertEqual(str(vehicle), f'{vehicle.type} {vehicle.license_plate}')

    def test_patient(self):
        """Test the patient string representation"""

        user = sample_user()
        patient = models.Patient.objects.create(
            user=user,
            firstname='John',
            lastname='Doe',
            phone_number='0678973465',
            description='This is the patient description',
            special=False,
            address=sample_address(user)
        )

        self.assertEqual(str(patient), f'{patient.firstname} {patient.lastname}')
