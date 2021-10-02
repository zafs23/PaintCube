from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse

from rest_framework.test import APIClient
from rest_framework import status


# testing an API add a helper function or constant variable to
# test the URL
CREATE_USER_URL = reverse('user:create')
TOKEN_URL = reverse('user:token')


def create_user(**params):  # two stars means this is a dynamic list of
    # arguments, and we can add many as arguments here
    return get_user_model().objects.create_user(**params)


class PublicUserApiTests(TestCase):  # unauthenticated thus public
    """test the users's api which is public"""

    def setUp(self):
        self.client = APIClient()

    def test_create_valid_user_success(self):
        """Test creating user with valid payload is successful"""
        payload = {  # these are the information we need to create a user
            'email': 'test@sajiazafreen.com',
            'password': 'testpass',
            'name': 'testname'
        }
        res = self.client.post(CREATE_USER_URL, payload)  # make the
        # this will do a HTTP post request to the client for creating users
        # then we need to test that the outcome is satisfactory

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        user = get_user_model().objects.get(**res.data)  # take a dictionary
        # response which should look similar to the payload with an ID
        # field. then test the password is correct
        self.assertTrue(user.check_password(payload['password']))
        self.assertNotIn('password', res.data)

    def test_user_exists(self):
        """test create user that already exits will fail"""
        payload = {
            'email': 'test@sajiazafreen.com',
            'password': 'testpass',
            'name': 'testname',
            }
        create_user(**payload)  # we pass the payloads to create an user and
        # then test that if we again use these payloads it will fail to do so
        # the **payload means taking more than one arguments
        res = self.client.post(CREATE_USER_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_password_too_short(self):
        """the password must be more than 8 characters"""
        payload = {
            'email': 'test@sajiazafreen.com',
            'password': 'pw',
            'name': 'testname',
            }
        res = self.client.post(CREATE_USER_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
        user_exists = get_user_model().objects.filter(
            email=payload['email']
        ).exists()
        self.assertFalse(user_exists)  # two type of condition is tested here,
        # one that the bad_request and other is after the bad_request response
        # user was not created

    def test_create_token_for_user(self):
        """Test that a token is created for the user"""
        payload = {
            'email': 'test@sajiazafreen.com',
            'password': 'testpass',
        }
        create_user(**payload)
        res = self.client.post(TOKEN_URL, payload)  # this is bad_request

        self.assertIn('token', res.data)
        self.assertEqual(res.status_code, status.HTTP_200_OK)

    def test_create_token_invalid_credentials(self):
        """test that token is not created if invalid credentials are given"""
        create_user(email='test@sajiazafreen.com', password='testpass')
        payload = {'email': 'test@sajiazafreen.com', 'password': 'wrong'}
        res = self.client.post(TOKEN_URL, payload)

        self.assertNotIn('token', res.data)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_token_no_user(self):
        """Test that  token is not created if user doesn't exist"""
        payload = {'email': 'test@sajiazafreen.com', 'password': 'testpass'}
        res = self.client.post(TOKEN_URL, payload)

        self.assertNotIn('token', res.data)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_token_missing_field(self):
        """Test that email and password are required"""
        res = self.client.post(TOKEN_URL, {'email': 'one', 'password': ''})

        self.assertNotIn('token', res.data)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
