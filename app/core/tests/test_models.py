from django.test import TestCase
# import get user model helper fucntion
# not recommended to use the get user model directly
from django.contrib.auth import get_user_model


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