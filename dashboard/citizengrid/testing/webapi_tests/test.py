"""
Tests the endpoints
"""

from django.test import TestCase
from django.core.urlresolvers import reverse
from rest_framework import status
from rest_framework.authtoken.models import Token
from django.contrib.auth.models import User
import json
from citizengrid.models import MyGroup,ApplicationBasicInfo,CloudInstancesOpenstack

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

    def test_can_delete_a_group(self):
        APIClient(enforce_csrf_checks=True)
        mg = MyGroup(name="demo",description="demo description",owner="foo", group_role ='Owner')
        mg.save()
        mg.user.add(self.user)
        url = reverse('MyGroupDetailView',kwargs={'pk':1})
        response = self.client.delete(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_cannot_delete_a_group_with_invalid_id(self):
        APIClient(enforce_csrf_checks=True)
        url = reverse('MyGroupDetailView',kwargs={'pk':41})
        response = self.client.delete(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_can_join_a_group(self):
        APIClient(enforce_csrf_checks=True)
        mg = MyGroup(name="demo",description="demo description",owner="foo", group_role ='Owner')
        mg.save()
        mg.user.add(self.user)
        us = User.objects.create_user('baz', 'baz@bax.de', 'bax')
        us.save()
        self.client.logout()
        self.client.login(username='baz', password='bax')
        data = {'group_ids':[1]}
        url = reverse('join_group')
        response = self.client.post(url, data,format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_cannot_join_a_group_with_invalid_groupid(self):
        APIClient(enforce_csrf_checks=True)

        us = User.objects.create_user('baz', 'baz@bax.de', 'bax')
        us.save()
        self.client.logout()
        self.client.login(username='baz', password='bax')
        data = {'group_ids':[20]}
        url = reverse('join_group')
        response = self.client.post(url, data,format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


    def test_can_leave_a_group(self):
        APIClient(enforce_csrf_checks=True)
        mg = MyGroup(name="demo",description="demo description",owner="foo", group_role ='Owner')
        mg.save()
        mg.user.add(self.user)
        us = User.objects.create_user('baz', 'baz@bax.de', 'bax')
        us.save()
        mg.user.add(us)
        mg.save()
        self.client.logout()
        self.client.login(username='baz', password='bax')

        url = reverse('leave_group',kwargs={'groupid':1})
        response = self.client.post(url,format='json')
        print response
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_can_leave_a_group_fails(self):
        """
            Fails when user is an owner and tries to leave it
        """
        APIClient(enforce_csrf_checks=True)
        mg = MyGroup(name="demo",description="demo description",owner="foo", group_role ='Owner')
        mg.save()
        mg.user.add(self.user)
        url = reverse('leave_group',kwargs={'groupid':1})
        self.client.post(url,format='json')
        response = self.client.post(url,format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

class CredentialsTest(APITestCase):
    """
    Test for API endpoints for managing credentials
    """
    def setUp(self):
        self.user = User.objects.create_user('foo', 'foo@bar.de', 'bar')
        #self.client = APIClient(enforce_csrf_checks=False)
        self.client.login(username='foo', password='bar')

    def test_can_list_all_credentials(self):
        pass

    def test_can_create_credentials(self):
        pass

    def test_can_show_details_of_a_credential(self):
        pass

    def test_can_delete_a_credentials(self):
        pass


class CloudInstancesTest(APITestCase):
    """
    Tests api endpoint for OpenStackCloudInstances
    """
    def setUp(self):
        self.user = User.objects.create_user('foo', 'foo@bar.de', 'bar')
        self.client.login(username='foo', password='bar')

    def test_get_openstack_cloudinstances_list(self):
        APIClient(enforce_csrf_checks=True)
        app = ApplicationBasicInfo(owner=self.user,name="demo",description="name",public=True,client_downloads=0)
        app.save()
        url = reverse('CloudInstancesList',kwargs={'appid':1})
        response = self.client.get(url,format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_get_openstack_cloudinstance_detail_by_id(self):
        pass

    def test_delete_openstack_cloudinstance(self):
        pass





