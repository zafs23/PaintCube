import tempfile
import os

from PIL import Image


from django.contrib.auth import get_user_model
from django.urls import reverse
from django.test import TestCase

from rest_framework import status
from rest_framework.test import APIClient

from core.models import Painting, Category, Supply
import datetime

from painting.serializers import PaintingSerializer, PaintingDetailSerializer


PAINTINGS_URL = reverse('painting:painting-list')
# need another URL whiche the id for the painting that is to be retrieved
# url for all the paintings: /api/painting/paintings
# url for the detailed painting : /api/painting/paintings/id (id is an int)


def image_upload_url(painting_id):
    """Return URL for painting image upload"""
    return reverse('painting:painting-upload-image', args=[painting_id])


def detail_painting_url(painting_id):
    """ return the detailed painting id"""
    return reverse('painting:painting-detail', args=[painting_id])


def sample_painting(user, **default_dic):
    """Create and return a sample painting"""
    date = datetime.date(1995, 1, 1)
    defaults = {
        'title': 'Sample painting',
        'painting_create_date': date  # format yyyy-mm-dd
    }
    defaults.update(default_dic)

    return Painting.objects.create(user=user, **defaults)


def sample_category(user, name='Sample category'):
    """Create and return a sample category object"""
    return Category.objects.create(user=user, name=name)


def sample_supply(user, name='Sample supply'):
    """Create and return a sample supply object"""
    return Supply.objects.create(user=user, name=name)
# PaintingDetailSerializer


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
        painting.categories.add(sample_category(user=self.user))
        painting.supplies.add(sample_supply(user=self.user))

        url = detail_painting_url(painting.id)  # gets id of sample painting
        res = self.client.get(url)

        serializer = PaintingDetailSerializer(painting)  # only one painting
        #  detail will be returned thus we dont need (many = true) here.
        self.assertEqual(res.data, serializer.data)

    def test_create_basic_painting(self):
        """Test creating basic painting object"""
        date = datetime.date(2014, 6, 11)
        payload = {
            'title': 'After sunset',
            'painting_create_date': date
        }
        res = self.client.post(PAINTINGS_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        painting = Painting.objects.get(id=res.data['id'])
        for key in payload.keys():
            self.assertEqual(payload[key], getattr(painting, key))

    def test_create_recipe_with_category(self):
        """Test creating a painting with category"""
        date = datetime.date(2014, 6, 11)
        category1 = sample_category(user=self.user, name='Water Color')
        category2 = sample_category(user=self.user, name='Acrylic')
        payload = {
            'title': 'After sunset',
            'painting_create_date': date,
            'categories': [category1.id, category2.id]
        }
        res = self.client.post(PAINTINGS_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        painting = Painting.objects.get(id=res.data['id'])
        categories = painting.categories.all()
        self.assertEqual(categories.count(), 2)
        self.assertIn(category1, categories)
        self.assertIn(category2, categories)

    def test_create_recipe_with_supply(self):
        """Test creating  painting with supply"""
        date = datetime.date(2014, 6, 11)
        supply1 = sample_supply(user=self.user, name='Pen')
        supply2 = sample_supply(user=self.user, name='Paper')
        payload = {
            'title': 'After sunset',
            'painting_create_date': date,
            'supplies': [supply1.id, supply2.id]
        }
        res = self.client.post(PAINTINGS_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        painting = Painting.objects.get(id=res.data['id'])
        supplies = painting.supplies.all()
        self.assertEqual(supplies.count(), 2)
        self.assertIn(supply1, supplies)
        self.assertIn(supply2, supplies)

    def test_partial_update_painting(self):
        """Test updating a painting object with patch"""
        painting = sample_painting(user=self.user)
        painting.categories.add(sample_category(user=self.user))
        new_category = sample_category(user=self.user, name='Acrylic')

        # payload
        payload = {'title': 'Before Sunset', 'categories': [new_category.id]}
        url = detail_painting_url(painting.id)
        self.client.patch(url, payload)

        # retrieve update and check
        painting.refresh_from_db()
        self.assertEqual(painting.title, payload['title'])
        categories = painting.categories.all()
        self.assertEqual(len(categories), 1)
        self.assertIn(new_category, categories)

    def test_full_update_painting(self):
        """Test updating a painting with put"""
        date = datetime.date(2014, 6, 11)
        painting = sample_painting(user=self.user)
        painting.categories.add(sample_category(user=self.user))
        payload = {
            'title': 'Before Sunset',
            'painting_create_date': date
        }
        url = detail_painting_url(painting.id)
        self.client.put(url, payload)

        painting.refresh_from_db()
        self.assertEqual(painting.title, payload['title'])
        self.assertEqual(painting.painting_create_date,
                         payload['painting_create_date'])
        categories = painting.categories.all()
        self.assertEqual(len(categories), 0)


class PaintingImageUploadTests(TestCase):

    def setUp(self):  # before the test runs
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            'user@sajiazafreen.com',
            'testpass'
        )
        self.client.force_authenticate(self.user)
        self.painting = sample_painting(user=self.user)

    def tearDown(self):  # after the test runs, removing all the test files
        self.painting.image.delete()

    def test_upload_image_to_painting(self):
        """Test uploading an email to painting"""
        url = image_upload_url(self.painting.id)
        with tempfile.NamedTemporaryFile(suffix='.jpg') as ntf:
            # creates a names temporary file in the system at a random location
            # in forward/temp folder and suffix is the extention
            img = Image.new('RGB', (10, 10))  # 10/10 dimension
            img.save(ntf, format='JPEG')  # ntf is the reference
            ntf.seek(0)  # seeks the files, this is how python reads by
            # back to the beginning of the file
            res = self.client.post(url, {'image': ntf}, format='multipart')

        self.painting.refresh_from_db()
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertIn('image', res.data)
        self.assertTrue(os.path.exists(self.painting.image.path))

    def test_upload_image_bad_request(self):
        """Test uploading an invalid image"""
        url = image_upload_url(self.painting.id)
        res = self.client.post(url, {'image': 'notimage'}, format='multipart')

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_filter_paintings_by_categories(self):
        """Test returning paintings with specific categories"""
        painting1 = sample_painting(user=self.user, title='Sunset Before')
        painting2 = sample_painting(user=self.user, title='Sunset After')
        category1 = sample_category(user=self.user, name='Watercolor')
        category2 = sample_category(user=self.user, name='Acrylic')
        painting1.categories.add(category1)
        painting2.categories.add(category2)
        painting3 = sample_painting(user=self.user, title='After Storm')

        res = self.client.get(
            PAINTINGS_URL,
            {'categories': f'{category1.id},{category2.id}'}
        )

        serializer1 = PaintingSerializer(painting1)  # check if the categories
        # are returned using the serializer
        serializer2 = PaintingSerializer(painting2)
        serializer3 = PaintingSerializer(painting3)
        self.assertIn(serializer1.data, res.data)
        self.assertIn(serializer2.data, res.data)
        self.assertNotIn(serializer3.data, res.data)

    def test_filter_recipes_by_supplies(self):
        """Test returning paintings with specific supplies"""
        painting1 = sample_painting(user=self.user, title='Sunset Before')
        painting2 = sample_painting(user=self.user, title='Sunset after')
        supply1 = sample_supply(user=self.user, name='Pen')
        supply2 = sample_supply(user=self.user, name='Paper')
        painting1.supplies.add(supply1)
        painting2.supplies.add(supply2)
        painting3 = sample_painting(user=self.user, title='After Storm')

        res = self.client.get(
            PAINTINGS_URL,
            {'supplies': f'{supply1.id},{supply2.id}'}
        )

        serializer1 = PaintingSerializer(painting1)
        serializer2 = PaintingSerializer(painting2)
        serializer3 = PaintingSerializer(painting3)
        self.assertIn(serializer1.data, res.data)
        self.assertIn(serializer2.data, res.data)
        self.assertNotIn(serializer3.data, res.data)
