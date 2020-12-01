import uuid
import os
from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, \
                                        PermissionsMixin
from django.conf import settings


def recipe_image_file_path(instance, filename):
    """Generate file path for new recipe image"""
    ext = filename.split('.')[-1]
    filename = f'{uuid.uuid4()}.{ext}'

    return os.path.join('uploads/recipe/', filename)


class UserManager(BaseUserManager):

    def create_user(self, email, password=None, **extra_fields):
        """Creates and saves a new user"""
        if not email:
            raise ValueError('Users must have an email address')
        user = self.model(email=self.normalize_email(email), **extra_fields)
        user.set_password(password)
        user.save(using=self._db)

        return user

    def create_superuser(self, email, password):
        """Creates and saves a new superuser"""
        user = self.create_user(email, password)
        user.is_staff = True
        user.is_superuser = True
        user.save(using=self.db)

        return user


class User(AbstractBaseUser, PermissionsMixin):
    """Custom user model that suppors using email instead of username"""
    email = models.EmailField(max_length=255, unique=True)
    name = models.CharField(max_length=255)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)

    objects = UserManager()

    USERNAME_FIELD = 'email'


class Tag(models.Model):
    """Tag to be used for a recipe"""
    name = models.CharField(max_length=255)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        # if we delete the user, delete the tag as well
        on_delete=models.CASCADE,
    )

    def __str__(self):
        return self.name


class Ingredient(models.Model):
    """Ingredient to be used for a recipe"""
    name = models.CharField(max_length=255)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        # if we delete the user, delete the tag as well
        on_delete=models.CASCADE,
    )

    def __str__(self):
        return self.name


class Recipe(models.Model):
    """Recipe object"""
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
    )
    title = models.CharField(max_length=255)
    time_minutes = models.IntegerField()
    price = models.DecimalField(max_digits=5, decimal_places=2)
    link = models.CharField(max_length=255, blank=True)
    """
        it's possible to remove the string arround the Ingredient object but the issue with that is we need to have 
        classes in correct order
    """
    ingredients = models.ManyToManyField('Ingredient')
    tags = models.ManyToManyField('Tag')
    # don't add brackets because we don't want to call the function.
    # Django will call the fonction in the background when uploading an image
    image = models.ImageField(null=True, upload_to=recipe_image_file_path)

    def __str__(self):
        return self.title


# heroad models
class Address(models.Model):
    """Address object"""
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
    )

    name = models.CharField(max_length=255)
    address1 = models.CharField(max_length=255)
    address2 = models.CharField(max_length=255, blank=True)
    zip_code = models.IntegerField()
    city = models.CharField(max_length=255)

    def __str__(self):
        return self.city + ', ' + self.address1 + (' ' + self.address2 if self.address2 else '') + ', ' + str(self.zip_code)


class Run(models.Model):
    """Run object"""
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
    )

    date = models.DateTimeField()
    departure_time = models.DateTimeField()
    arriving_time = models.DateTimeField()
    # Relation plusieurs à un.
    # Plusieurs runs peuvent etre liés à une adresse
    pick_up_location = models.ForeignKey(
        Address,
        related_name='pick_up_location',
        on_delete=models.CASCADE,
    )
    deposit_location = models.ForeignKey(
        Address,
        related_name='deposit_location',
        on_delete=models.CASCADE,
    )
    is_return_path = models.BooleanField(default=False)
    comments = models.CharField(max_length=255)

    master_run = models.ForeignKey(
        'MasterRun',
        on_delete=models.CASCADE
    )

    patient = models.ForeignKey(
        'Patient',
        on_delete=models.CASCADE
    )

    def __str__(self):
        return str(self.date) + ' ' + str(self.deposit_location)


class MasterRun(models.Model):
    """MasterRun object"""
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        related_name='user',
        on_delete=models.CASCADE,
    )
    comments = models.CharField(max_length=255)
    date = models.DateTimeField()
    users = models.ManyToManyField(settings.AUTH_USER_MODEL, related_name='users')
    am = models.BooleanField(default=False)
    pm = models.BooleanField(default=False)

    vehicle = models.ForeignKey(
        'Vehicle',
        on_delete=models.CASCADE
    )

    def __str__(self):
        return str(self.users)


class Vehicle(models.Model):
    """Vehicle object"""

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
    )

    TYPE_VEHICLE_CHOICES = [
        ('VSL', 'VSL'),
        ('Ambulance', 'Ambulance')
    ]
    type = models.CharField(
        choices=TYPE_VEHICLE_CHOICES,
        default='Ambulance',
        max_length=9
    )

    license_plate = models.CharField(max_length=9)

    def __str__(self):
        return f'{self.type} {self.license_plate}'


class Patient(models.Model):
    """Patient object"""

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
    )

    firstname = models.CharField(max_length=255)
    lastname = models.CharField(max_length=255)
    phone_number = models.CharField(max_length=10)
    special = models.BooleanField(default=False)
    description = models.CharField(max_length=255, blank=True)

    address = models.ForeignKey(
        'Address',
        on_delete=models.CASCADE
    )

    def __str__(self):
        return f'{self.firstname} {self.lastname}'
