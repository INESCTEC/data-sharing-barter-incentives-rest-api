# flake8: noqa

from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from ..common import create_and_login_superuser, create_user, login_user


class TestUserListView(APITestCase):
    """
    Tests for UserListView class. This method should only be available
    to superusers.

    """

    def setUp(self):
        self.base_url = reverse("user:list")
        self.super_user = create_and_login_superuser(self.client)
        self.normal_user = create_user()

    def test_list_users_no_auth(self):
        self.client.credentials(HTTP_AUTHORIZATION="")
        response = self.client.get(self.base_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_normaluser_list_users(self):
        login_user(self.client, self.normal_user)
        response = self.client.get(self.base_url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        expected_response = {'code': 403,
                             'data': None,
                             'status': 'error',
                             'message': 'You do not have permission to '
                                        'perform this action.'}
        self.assertEqual(response.json(), expected_response)

    def test_superuser_list_users(self):
        login_user(self.client, self.super_user)
        response = self.client.get(self.base_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        response_data = response.json()["data"]
        self.assertEqual(len(response_data), 2)
