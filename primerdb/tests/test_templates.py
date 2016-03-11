from django.test import Client, TestCase
import os
import django
from django.core.urlresolvers import reverse
os.environ['DJANGO_SETTINGS_MODULE'] = 'mysite.settings'
django.setup()


class TestUrls(TestCase):
    """Checks webpages are returning the correct HTTP status codes/ successful or unsuccessful HTTP requests"""

    def setUp(self):
        self.client = Client()

    def test_homepage(self):
        response = self.client.get(reverse('home'))
        self.assertEqual(response.status_code, 200)

    def test_uploadpage(self):
        response = self.client.get(reverse('upload'))
        self.assertEqual(response.status_code, 200)

    def test_snppage(self):
        response = self.client.get('/snps/COL4A5_2F/')  # must be in the database
        self.assertEqual(response.status_code, 200)

    def test_confirmpage(self):
        response = self.client.get(reverse('complete'))
        self.assertEqual(response.status_code, 200)

    def test_wrongpage(self):
        response = self.client.get('/bonjour/')  # checks a different status code
        self.assertEqual(response.status_code, 404)


