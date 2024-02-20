# flake8: noqa

from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from ...models import UserWalletAddress
from ..common import create_and_login_superuser, create_user, login_user


class TestUserWalletAddressView(APITestCase):
    """
        Tests for UserWalletAddressView class.

    """

    user_1 = {'email': 'normal1@user.com',
              'password': 'normal1_foo',
              'first_name': 'Normal1',
              'last_name': 'Peanut1',
              'wallet_address': 'rms1qz2yvydysm3fnjcs2ek4wascxkectuhgkk36f0rr23yjh69zyheuvux4ngj'}
    user_2 = {'email': 'normal2@user.com',
              'password': 'normal2_foo',
              'first_name': 'Normal2',
              'last_name': 'Peanut2',
              'wallet_address': 'rms1qruze7u5r6k23v6vquzqnetpdmvydgfyyltyr3qv0ydtlgmhfrgxkkugcrv'}

    def setUp(self):
        self.base_url = reverse("user:wallet-address")
        self.super_user = create_and_login_superuser(self.client)
        self.normal_user1 = create_user(use_custom_data=True, **self.user_1)
        self.normal_user2 = create_user(use_custom_data=True, **self.user_2)

    def test_register_address_no_auth(self):
        data = {"wallet_address": self.user_1["wallet_address"]}
        self.client.credentials(HTTP_AUTHORIZATION="")
        response = self.client.post(self.base_url, data=data, format="json")
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_list_address_no_auth(self):
        self.client.credentials(HTTP_AUTHORIZATION="")
        response = self.client.get(self.base_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_register_address(self):
        login_user(self.client, user=self.normal_user1)
        data = {"wallet_address": self.user_1["wallet_address"]}
        response = self.client.post(self.base_url, data=data, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        response_data = response.json()["data"]
        self.assertEqual(response_data["wallet_address"], data["wallet_address"])
        # Check if exists in DB:
        resource_data = UserWalletAddress.objects.get(
            wallet_address=response_data["wallet_address"]
        )
        self.assertTrue(resource_data)

    def test_register_duplicated_address(self):
        login_user(self.client, user=self.normal_user1)
        data = {"wallet_address": self.user_1["wallet_address"]}
        response = self.client.post(self.base_url, data=data, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        response = self.client.post(self.base_url, data=data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_register_duplicated_address_different_user(self):
        # login with user 1 & upload wallet address:
        login_user(self.client, user=self.normal_user1)
        data = {"wallet_address": self.user_1["wallet_address"]}
        response = self.client.post(self.base_url, data=data, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # login with user 2 & upload again user 1 wallet address:
        login_user(self.client, user=self.normal_user2)
        response = self.client.post(self.base_url, data=data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        expected_response = {'code': 400,
                             'data': {'wallet_address': ['user wallet address with this wallet address already exists.']},
                             'status': 'error',
                             'message': "Validation error. Please re-check "
                                        "your request parameters or body fields "
                                        "and fix the errors "
                                        "mentioned in this response "
                                        "'data' field."
                             }
        self.assertEqual(response.json(), expected_response)

    def test_list_address(self):
        login_user(self.client, user=self.normal_user1)
        data = {"wallet_address": self.user_1["wallet_address"]}
        response = self.client.post(self.base_url, data=data, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        response = self.client.get(self.base_url)
        response_data = response.json()["data"]
        self.assertEqual(response_data[0]["wallet_address"], data["wallet_address"])

    def test_update_address(self):
        login_user(self.client, user=self.normal_user1)
        data = {"wallet_address": self.user_1["wallet_address"]}
        response = self.client.post(self.base_url, data=data, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # Change wallet address
        new_wallet_address = "rms1qz45jp9h7mx90rkjh3qk8y2mzgfm9sndyc8mr6x3umy4zmjwgemh6r5g08m"
        data = {"wallet_address": new_wallet_address}
        response = self.client.put(self.base_url, data=data, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # Verify if wallet address changed:
        response = self.client.get(self.base_url)
        response_data = response.json()["data"]
        self.assertEqual(response_data[0]["wallet_address"], new_wallet_address)

    def test_superuser_list_address(self):
        # Register wallet address user 1
        login_user(self.client, user=self.normal_user1)
        data = {"wallet_address": self.user_1["wallet_address"]}
        response = self.client.post(self.base_url, data=data, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # Register wallet address user 2
        login_user(self.client, user=self.normal_user2)
        data = {"wallet_address": self.user_2["wallet_address"]}
        response = self.client.post(self.base_url, data=data, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # Login with admin user and check if it can see both wallet addresses:
        login_user(self.client, user=self.super_user)
        response = self.client.get(self.base_url)
        response_data = response.json()["data"]
        self.assertEqual(len(response_data), 2)
        valid_addresses = [self.user_1["wallet_address"],
                           self.user_2["wallet_address"]]
        for d in response_data:
            self.assertIn(d["wallet_address"], valid_addresses)
