# import the same things imported in test_categories_api
from django.contrib.auth import get_user_model
from django.urls import reverse
from django.test import TestCase

from rest_framework import status
from rest_framework.test import APIClient

from core.models import Supply, Painting
import datetime

from painting.serializers import SupplySerializer


SUPPLIES_URL = reverse('painting:supply-list')


class PublicSuppliesApiTests(TestCase):
    """Test thje publicly available supplies API"""

    def setUp(self):
        self.client = APIClient()

    def test_login_required(self):  # LOG IN IS ALWAYS REQUIREED
        """Test that login is required for retrieving supply list"""
        res = self.client.get(SUPPLIES_URL)

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


# listing ingredients
class PrivateSuppliesApiTests(TestCase):
    """Test the authorized user list the supplies for paintings in the API"""

    def setUp(self):
        self.user = get_user_model().objects.create_user(
            'test@sajiazafreen.com',
            'passtestlist100'
        )
        self.client = APIClient()
        self.client.force_authenticate(self.user)

    def test_retrieve_supplies_list(self):
        """Test retrieving supply list is correct"""
        Supply.objects.create(user=self.user, name='Pencil')
        Supply.objects.create(user=self.user, name='A4 Paper')

        res = self.client.get(SUPPLIES_URL)

        supplies = Supply.objects.all().order_by('-name')  # ORDER by name
        serializer = SupplySerializer(supplies, many=True)  # many = true
        # needed otherwise will think only serialize one tage
        # the list is in reverse order
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_creating_supplies_limited_to_user(self):
        """Test that supplies listed are from authenticated users"""
        user2 = get_user_model().objects.create_user(
            'other@sajiazafreen.com',
            'testpass'
        )  # new user that was not included in the set up
        Supply.objects.create(user=user2, name='Sunlight')  # painting name
        supply = Supply.objects.create(user=self.user, name='pencil')

        # make the request
        res = self.client.get(SUPPLIES_URL)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data), 1)  # checking the length of the array
        # as we have mentioned just 1 supply it will return 1
        self.assertEqual(res.data[0]['name'], supply.name)  # test correct
        # name

    def test_create_supply_successful(self):
        """Test creating a new supply successfully"""
        payload = {'name': 'Test supply'}
        self.client.post(SUPPLIES_URL, payload)

        exists = Supply.objects.filter(
            user=self.user,
            name=payload['name']
        ).exists()
        self.assertTrue(exists)  # test would fail if exists doesnt exist

    def test_create_supply_invalid(self):
        """Test creating a new supply with invalid payload"""
        payload = {'name': ''}  # if a blank category that will be invalid
        res = self.client.post(SUPPLIES_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_retrieve_supplies_assigned_to_paintings(self):
        """Test filtering supplies which are assigned to paintings"""
        supply1 = Supply.objects.create(user=self.user, name='Sample supply1')
        supply2 = Supply.objects.create(user=self.user, name='Sample supply2')
        painting = Painting.objects.create(
            title='Sample Painting',
            painting_create_date=datetime.date(2014, 6, 11),
            user=self.user
        )
        painting.supplies.add(supply1)

        res = self.client.get(SUPPLIES_URL, {'assigned_only': 1})

        serializer1 = SupplySerializer(supply1)
        serializer2 = SupplySerializer(supply2)
        self.assertIn(serializer1.data, res.data)
        self.assertNotIn(serializer2.data, res.data)

        # we have to make sure distinct item is returned for every query
        # because Django returns each item assigned seperately
    def test_retrieve_supplies_assigned_unique(self):
        """Test filtering supplies by assigned returns unique items"""
        supply = Supply.objects.create(user=self.user, name='A4 Paper')
        Supply.objects.create(user=self.user, name='Pen')
        painting1 = Painting.objects.create(
            title='Sunset',
            painting_create_date=datetime.date(2014, 6, 11),
            user=self.user
        )
        painting1.supplies.add(supply)
        painting2 = Painting.objects.create(
            title='Stormy night',
            painting_create_date=datetime.date(2014, 6, 11),
            user=self.user
        )
        painting2.supplies.add(supply)

        res = self.client.get(SUPPLIES_URL, {'assigned_only': 1})

        self.assertEqual(len(res.data), 1)
