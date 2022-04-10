from django.test import TestCase
# import get user model helper fucntion
# not recommended to use the get user model directly
from django.contrib.auth import get_user_model

from core import models
import datetime


# helper fucntion to test the user model
def sample_user(email='test@sajiazafreen.com', password='testpass'):
    """create a sample user"""
    return get_user_model().objects.create_user(email, password)


class ModelTests(TestCase):

    def test_create_user_with_email_successful(self):
        """Test creating a new user with an email is successful"""
        email = 'test@sajiazafreen.com'
        password = 'Testpass123'
        user = get_user_model().objects.create_user(
            email=email,
            password=password
        )

        self.assertEqual(user.email, email)
        self.assertTrue(user.check_password(password))

    def test_new_user_email_normalize(self):
        """test the email for a new user is normalized"""
        email = 'test@SAJIAZAFREEN.COM'
        user = get_user_model().objects.create_user(email, 'test123')
        # here we do not need the actual password as we already tested that

        self.assertEqual(user.email, email.lower())
        # this makes the string lower case

    def test_new_user_invalid_email(self):
        # email address was not provided or passed a non value
        """test creating user with no email raises error"""
        with self.assertRaises(ValueError):
            # if anything we run here doesn't the ValueError this test
            # will fail
            get_user_model().objects.create_user(None, 'test123')

    def test_create_new_superuser(self):
        """Test creating a new superuser"""
        user = get_user_model().objects.create_superuser(
            'test@sajiazafreen.com',
            'test123'
        )

        self.assertTrue(user.is_superuser)
        self.assertTrue(user.is_staff)

    def test_category_str(self):
        # test by creating a sample tag for a painting and test that that the
        # string created from the tag gives the correct tage name
        """Test the painting category's string representation"""
        category = models.Category.objects.create(
            user=sample_user(),
            name='Watercolor'
        )

        self.assertEqual(str(category), category.name)

    def test_supply_str(self):
        """Test the string respresentation painting suppply used """
        supply = models.Supply.objects.create(
            user=sample_user(),
            name='Paint Brush'
        )

        self.assertEqual(str(supply), supply.name)

    def test_painting_str(self):
        """Test the paintings string representation"""
        painting = models.Painting.objects.create(
            user=sample_user(),
            title='Stormy Night',
            painting_create_date=datetime.date(2014, 6, 11)
            # do not put zero in date as it is counted as octals
        )

        self.assertEqual(str(painting), painting.title)
