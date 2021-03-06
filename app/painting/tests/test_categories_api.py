from django.contrib.auth import get_user_model
from django.urls import reverse
from django.test import TestCase

from rest_framework import status
from rest_framework.test import APIClient

from core.models import Category, Painting
import datetime

from painting.serializers import CategorySerializer


CATEGORIES_URL = reverse('painting:category-list')  # category list


class PublicCategoriesApiTests(TestCase):
    """Test thje publicly available categories API"""

    def setUp(self):
        self.client = APIClient()

    def test_login_required(self):
        """Test that login is required for retrieving category list"""
        res = self.client.get(CATEGORIES_URL)

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateCategoriesApiTests(TestCase):
    """Test the authorized user catgorize the API"""

    def setUp(self):
        self.user = get_user_model().objects.create_user(
            'test@sajiazafreen.com',
            'passtestlist100'
        )
        self.client = APIClient()
        self.client.force_authenticate(self.user)

    def test_retrieve_categories_list(self):
        """Test retrieving category list is correct"""
        Category.objects.create(user=self.user, name='Watercolor')
        Category.objects.create(user=self.user, name='Acrylic')

        res = self.client.get(CATEGORIES_URL)

        categories = Category.objects.all().order_by('-name')  # ORDER by name
        serializer = CategorySerializer(categories, many=True)  # many = true
        # needed otherwise will think only serialize one tage
        # the list is in reverse order
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_creating_categories_limited_to_user(self):
        """Test that categories listed are from authenticated users"""
        user2 = get_user_model().objects.create_user(
            'other@sajiazafreen.com',
            'testpass'
        )  # new user that was not included in the set up
        Category.objects.create(user=user2, name='Sunlight')  # painting name
        category = Category.objects.create(user=self.user, name='Acrylic')

        # make the request
        res = self.client.get(CATEGORIES_URL)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data), 1)  # checking the length of the array
        # as we have created just category it will return 1
        self.assertEqual(res.data[0]['name'], category.name)  # test correct
        # name

    def test_create_category_successful(self):
        """Test creating a new category successfully"""
        payload = {'name': 'Test category'}
        self.client.post(CATEGORIES_URL, payload)

        exists = Category.objects.filter(
            user=self.user,
            name=payload['name']
        ).exists()
        self.assertTrue(exists)  # test would fail if exists doesnt exist

    def test_create_category_invalid(self):
        """Test creating a new category with invalid payload"""
        payload = {'name': ''}  # if a blank category that will be invalid
        res = self.client.post(CATEGORIES_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_retrieve_categories_assigned_to_paintings(self):
        """Test filtering categories which are assigned to paintings"""
        category1 = Category.objects.create(
                    user=self.user, name='Sample category1')
        category2 = Category.objects.create(
                    user=self.user, name='Sample category2')
        painting = Painting.objects.create(
            title='Sample Painting',
            painting_create_date=datetime.date(2014, 6, 11),
            user=self.user
        )
        painting.categories.add(category1)

        res = self.client.get(CATEGORIES_URL, {'assigned_only': 1})

        serializer1 = CategorySerializer(category1)
        serializer2 = CategorySerializer(category2)
        self.assertIn(serializer1.data, res.data)
        self.assertNotIn(serializer2.data, res.data)

        # we have to make sure distinct item is returned for every query
        # because Django returns each item assigned seperately
    def test_retrieve_categories_assigned_unique(self):
        """Test filtering categories by assigned returns unique items"""
        category = Category.objects.create(user=self.user, name='Watercolor')
        Category.objects.create(user=self.user, name='Acrylic')
        painting1 = Painting.objects.create(
            title='Sunset',
            painting_create_date=datetime.date(2014, 6, 11),
            user=self.user
        )
        painting1.categories.add(category)
        painting2 = Painting.objects.create(
            title='Stormy night',
            painting_create_date=datetime.date(2014, 6, 11),
            user=self.user
        )
        painting2.categories.add(category)

        res = self.client.get(CATEGORIES_URL, {'assigned_only': 1})

        self.assertEqual(len(res.data), 1)
