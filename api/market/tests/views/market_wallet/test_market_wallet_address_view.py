# flake8: noqa

from django.urls import reverse
from rest_framework import status
from django.test import TransactionTestCase
from rest_framework.test import APIClient

from ....models import MarketWalletAddress
from ...common import (
    create_and_login_superuser,
    login_user,
    create_user
)
from ..response_templates import (
    validation_error_response,
    conflict_error_response
)


class TestMarketSessionBidView(TransactionTestCase):
    """
    Tests for MarketSessionBidView class.

    """
    reset_sequences = True  # reset DB AutoIncremental PK's on each test

    def setUp(self):
        self.client = APIClient()
        self.base_url = reverse("market:market-wallet-address")
        self.super_user = create_and_login_superuser(self.client)
        self.wallet_data = {
            "wallet_address": "atoi1qpx2srs3nw08yuwtyrhsksku5yfkld2fmmmj643nwq4cqyu5xtgfjhh46sp"
        }

    def test_create_wallet_address_no_auth(self):
        self.client.credentials(HTTP_AUTHORIZATION="")
        response = self.client.post(self.base_url,
                                    data=self.wallet_data,
                                    format="json")
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_create_wallet_address_normal_user(self):
        user = create_user()
        login_user(client=self.client, user=user)

        response = self.client.post(self.base_url,
                                    data=self.wallet_data,
                                    format="json")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_create_wallet_address_super_user(self):
        login_user(client=self.client, user=self.super_user)

        response = self.client.post(self.base_url,
                                    data=self.wallet_data,
                                    format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        response_data = response.json()["data"]
        response_data.pop("registered_at")
        expected_response = {'wallet_address': 'atoi1qpx2srs3nw08yuwtyrhsksku5yfkld2fmmmj643nwq4cqyu5xtgfjhh46sp'}
        self.assertEqual(response_data, expected_response)

        wallet_address = MarketWalletAddress.objects.get()
        self.assertEqual(wallet_address.wallet_address, self.wallet_data["wallet_address"])

    def test_update_wallet_address_super_user(self):
        # Create first address:
        MarketWalletAddress.objects.create(wallet_address=self.wallet_data["wallet_address"])
        login_user(client=self.client, user=self.super_user)

        # Try to update existing address:
        new_address = "rms1qz2yvydysm3fnjcs2ek4wascxkectuhgkk36f0rr23yjh69zyheuvux4ngj"
        response = self.client.put(self.base_url,
                                   data={"wallet_address": new_address},
                                   format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_create_second_wallet_address(self):
        # Create first address:
        MarketWalletAddress.objects.create(wallet_address=self.wallet_data["wallet_address"])
        login_user(client=self.client, user=self.super_user)

        # Create second address - should raise error as only 1 address allowed:
        data = {
            "wallet_address": "atoi1qpx2srs3nw08yuwtyrhsksku5yfkld2fmmmj643nwq4cqyu5xtgfjhh4aaa"
        }
        response = self.client.post(self.base_url,
                                    data=data,
                                    format="json")
        self.assertEqual(response.status_code, status.HTTP_409_CONFLICT)

        response_data = response.json()
        expected_response = conflict_error_response(
            message="A market address was already registered. Use PUT method to update it."
        )
        self.assertEqual(response_data, expected_response)

        # Check if address remains the same in DB:
        wallet_address = MarketWalletAddress.objects.get()
        self.assertEqual(wallet_address.wallet_address, self.wallet_data["wallet_address"])

    def test_create_duplicated_wallet_address(self):
        # Insert address in DB:
        MarketWalletAddress.objects.create(wallet_address=self.wallet_data["wallet_address"])
        login_user(client=self.client, user=self.super_user)

        # Create second address - should raise error as only 1 address allowed:
        response = self.client.post(self.base_url,
                                    data=self.wallet_data,
                                    format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        response_data = response.json()
        expected_response = validation_error_response(
            data={
                'wallet_address': ['market wallet address with this wallet address already exists.']
            }
        )
        self.assertEqual(response_data, expected_response)

    def test_list_market_address_super_user(self):
        # Insert address in DB:
        MarketWalletAddress.objects.create(wallet_address=self.wallet_data["wallet_address"])
        login_user(client=self.client, user=self.super_user)

        response = self.client.get(self.base_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        response_data = response.json()["data"]
        self.assertEqual(response_data["wallet_address"], self.wallet_data["wallet_address"])

    def test_list_market_address_normal_user(self):
        # Insert address in DB:
        MarketWalletAddress.objects.create(wallet_address=self.wallet_data["wallet_address"])

        # Create normal users & perform requests:
        user = create_user()
        login_user(client=self.client, user=user)

        response = self.client.get(self.base_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        response_data = response.json()["data"]
        self.assertEqual(response_data["wallet_address"], self.wallet_data["wallet_address"])
