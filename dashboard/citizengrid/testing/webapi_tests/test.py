"""
Tests the endpoints
"""

from django.test import TestCase
from django.core.urlresolvers import reverse
from rest_framework import status
from rest_framework.authtoken.models import Token
from django.contrib.auth.models import User
import json

from rest_framework.test import APITestCase, APIClient


class GroupTests(APITestCase):

    def setUp(self):
        self.user = User.objects.create_user('foo', 'foo@bar.de', 'bar')
        #self.client = APIClient(enforce_csrf_checks=False)
        self.client.login(username='foo', password='bar')

    def test_can_list_groups(self):
        """
        Ensure that the endpoint is capable of listing all the  groups
        """
        APIClient(enforce_csrf_checks=True)
        url = reverse('MyGroupList')
        response = self.client.get(url, {},format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_can_create_group(self):
        """
        Tests that an authenticated request to create_group creates a valid group
        :return: HTTP_201_CREATED
        """
        APIClient(enforce_csrf_checks=True)
        url = reverse('MyGroupList')
        data = {'name': 'demo','description':'This is demo description'}
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(json.loads(response.content)['data'], data)

