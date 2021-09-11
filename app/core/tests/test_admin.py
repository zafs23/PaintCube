from django.test import TestCase, Client
from django.contrib.auth import get_user_model
from django.urls import reverse


class AdminSiteTests(TestCase):  # inherited from test cases
    # we need a set up function here, that will run before every test case

    def setUp(self):
        # helps the client helpfer function to log user by Django
        # Authentication thus we don manually have to log user before testing
        self.client = Client()
        self.admin_user = get_user_model().objects.create_superuser(
            email='admin@sajiazafreen.com',
            password='password123'
        )
        self.client.force_login(self.admin_user)  # admin is login to client
        self.user = get_user_model().objects.create_user(  # regular user
            # we have this spare user for testing listing
            email='test@sajiazafreen.com',
            password='password123',
            name='Test user full name'
        )

    def test_users_listed(self):
        """Test that users are listed on usr page"""
        url = reverse('admin:core_user_changelist')
        # generate the URL for our list user page and if the URL changes this
        # reverse function will update the URLs automatically
        res = self.client.get(url)  # here test client will perform HTTP GET
        # on the URL we found here

        self.assertContains(res, self.user.name)
        self.assertContains(res, self.user.email)
        # this checks our response here contains certain item
        # also checks the HTTP response if it was HTTP200 and also looks into
        # actual content of the res-manually checking res will output an object

    def test_user_change_page(self):
        """Test that the user edit page works"""
        url = reverse('admin:core_user_change', args=[self.user.id])
        # /admin/core/user/id - the reverse will make this urls
        res = self.client.get(url)

        self.assertEqual(res.status_code, 200)# status code for response from
        # the client is HTTP 200

    def test_create_user_page(self):
        """Test that create user page works"""
        url = reverse('admin:core_user_add')
        res = self.client.get(url)

        self.assertEqual(res.status_code, 200)
