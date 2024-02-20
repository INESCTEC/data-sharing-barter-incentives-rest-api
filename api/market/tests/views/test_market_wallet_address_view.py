# flake8: noqa

from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from ...models import MarketWalletAddress
from ..common import create_and_login_superuser, create_user, login_user
from .response_templates import (
    conflict_error_response,
    validation_error_response
)


class TestMarketWalletAddressView(APITestCase):
    """
        Tests for MarketWalletAddress class.

    """
    wallet_address = "atoi1qpx2srs3nw08yuwtyrhsksku5yfkld2fmmmj643nwq4cqyu5xtgfjhh46sp"

    def setUp(self):
        self.base_url = reverse("market:market-wallet-address")
        self.super_user = create_and_login_superuser(self.client)

    def test_register_address_no_auth(self):
        data = {"wallet_address": self.wallet_address}
        self.client.credentials(HTTP_AUTHORIZATION="")
        response = self.client.post(self.base_url, data=data)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_list_address_no_auth(self):
        self.client.credentials(HTTP_AUTHORIZATION="")
        response = self.client.get(self.base_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_register_address(self):
        login_user(self.client, user=self.super_user)
        data = {"wallet_address": self.wallet_address}
        response = self.client.post(self.base_url, data=data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        response_data = response.json()["data"]
        self.assertEqual(response_data["wallet_address"], data["wallet_address"])
        # Check if exists in DB:
        resource_data = MarketWalletAddress.objects.get(
            wallet_address=response_data["wallet_address"]
        )
        self.assertTrue(resource_data)

    def test_register_duplicated_address(self):
        login_user(self.client, user=self.super_user)
        data = {"wallet_address": self.wallet_address}
        response = self.client.post(self.base_url, data=data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        response = self.client.post(self.base_url, data=data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        expected_response = validation_error_response(
            data={'wallet_address': ['market wallet address with this wallet '
                                     'address already exists.']}
        )
        self.assertEqual(response.json(), expected_response)

    def test_register_second_address(self):
        login_user(self.client, user=self.super_user)
        data = {"wallet_address": self.wallet_address}
        response = self.client.post(self.base_url, data=data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = {"wallet_address": "atoi1qpx2srs3nw08yuwtyrhsksku5yfkld2fmmmj643nwq4cqyu5xtgfjhhaaaa"}
        response = self.client.post(self.base_url, data=data)
        self.assertEqual(response.status_code, status.HTTP_409_CONFLICT)
        expected_response = conflict_error_response(
            message='A market address was already registered. '
                    'Use PUT method to update it.'
        )
        self.assertEqual(response.json(), expected_response)

    def test_list_address_normal_user(self):
        user = create_user()
        login_user(client=self.client, user=user)
        data = {"wallet_address": self.wallet_address}
        response = self.client.post(self.base_url, data=data)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        expected_response = {'code': 403,
                             'data': None,
                             'status': 'error',
                             'message': 'You do not have permission to perform this action.'}
        self.assertEqual(response.json(), expected_response)

    def test_list_address(self):
        login_user(self.client, user=self.super_user)
        data = {"wallet_address": self.wallet_address}
        response = self.client.post(self.base_url, data=data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        response = self.client.get(self.base_url)
        response_data = response.json()["data"]
        self.assertEqual(response_data["wallet_address"], data["wallet_address"])

    def test_update_address(self):
        login_user(self.client, user=self.super_user)
        data = {"wallet_address": self.wallet_address}
        response = self.client.post(self.base_url, data=data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # Change wallet address
        new_wallet_address = "rms1qz2yvydysm3fnjcs2ek4wascxkectuhgkk36f0rr23yjh69zyheuvux4ngj"
        data = {"wallet_address": new_wallet_address}
        response = self.client.put(self.base_url, data=data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # Verify if wallet address changed:
        response = self.client.get(self.base_url)
        response_data = response.json()["data"]
        self.assertEqual(response_data["wallet_address"], new_wallet_address)

