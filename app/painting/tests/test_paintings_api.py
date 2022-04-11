from django.contrib.auth import get_user_model
from django.urls import reverse
from django.test import TestCase

from rest_framework import status
from rest_framework.test import APIClient

from core.models import Painting, Category, Supply

from painting.serializers import PaintingSerializer, PaintingDetailSerializer


PAINTINGS_URL = reverse('painting:painting-list')
# need another URL whiche the id for the painting that is to be retrieved
# url for all the paintings: /api/painting/paintings
# url for the detailed painting : /api/painting/paintings/id (id is an int)

def detail_painting_url(painting_id):
    """ return the detailed painting id"""
    return reverse('painting:painting-detail', args=[painting_id])

def sample_painting(user, **default_dic):
    """Create and return a sample painting"""
    defaults = {
        'title': 'Sample painting',
        'painting_create_date': '2014-6-11'
    }
    defaults.update(default_dic)

    return Painting.objects.create(user=user, **defaults)

def sample_category(user, name='Sample category'):
    """Create and return a sample category object"""
    return Category.objects.create(user=user, name=name)

def sample_supply(user, name='Sample supply'):
    """Create and return a sample supply object"""
    return Supply.objects.create(user=user, name=name)
#PaintingDetailSerializer


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

    def test_retrieve_paintings_list(self):  # a preview as will return the
        # ids of the paintings
        """Test retrieving painting is correct"""
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

    def test_painting_detail_view(self):
        """test viewing a painting detail is correct"""
        painting = sample_painting(user=self.user)
        painting.category.add(sample_category(user=self.user))
        painting.supply.add(sample_supply(user=self.user))

        url = detail_painting_url(painting.id)  # gets the id of the sample painting
        res = self.client.get(url)

        serializer = PaintingDetailSerializer(painting) # only one painting
        # detail will be returned thus we dont need (many = true) here.
        self.assertEqual(res.data, serializer.data)
