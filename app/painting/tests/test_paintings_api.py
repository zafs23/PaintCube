from django.contrib.auth import get_user_model
from django.urls import reverse
from django.test import TestCase

from rest_framework import status
from rest_framework.test import APIClient

from core.models import Painting

from painting.serializers import PaintingSerializer


PAINTINGS_URL = reverse('painting:painting-list')


def sample_painting(user, **default_dic):
    """Create and return a sample painting"""
    defaults = {
        'title': 'Sample painting',
        'painting_create_date': '2014-6-11'
    }
    defaults.update(default_dic)

    return Painting.objects.create(user=user, **defaults)


class PublicPaintingsApiTests(TestCase):
    """Test thje publicly available paintings API"""

    def setUp(self):
        self.client = APIClient()

    def test_login_required(self):  # LOG IN IS ALWAYS REQUIREED
        """Test that login is required for retrieving painting list"""
        res = self.client.get(PAINTINGS_URL)

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivatePaintingsApiTests(TestCase):
    """Test the authorized user list the paintings in the API"""

    def setUp(self):
        self.user = get_user_model().objects.create_user(
            'test@sajiazafreen.com',
            'passtestlist100'
        )
        self.client = APIClient()
        self.client.force_authenticate(self.user)

    def test_retrieve_paintings_list(self):
        """Test retrieving supply list is correct"""
        sample_painting(user=self.user)
        sample_painting(user=self.user)

        res = self.client.get(PAINTINGS_URL)

        paintings = Painting.objects.all().order_by('-id')  # ORDER by name
        serializer = PaintingSerializer(paintings, many=True)  # many = true
        # needed otherwise will think only serialize one tage
        # the list is in reverse order
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_creating_painting_limited_to_user(self):
        """Test that paintings listed are from authenticated users"""
        user2 = get_user_model().objects.create_user(
            'other@sajiazafreen.com',
            'testpass'
        )  # new user that was not included in the set up

        sample_painting(user=user2)
        sample_painting(user=self.user)

        # make the request
        res = self.client.get(PAINTINGS_URL)

        paintings = Painting.objects.filter(user=self.user)
        serializer = PaintingSerializer(paintings, many=True)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data), 1)  # checking the length of the array
        # as we have mentioned just 1 supply it will return 1
        self.assertEqual(res.data, serializer.data)  # test correct
        # name
