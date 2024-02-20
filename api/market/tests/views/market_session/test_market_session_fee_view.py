# flake8: noqa

from django.urls import reverse
from rest_framework import status
from django.test import TransactionTestCase
from rest_framework.test import APIClient

from ....models import MarketSession, MarketSessionFee
from ...common import (
    create_and_login_superuser,
    create_user,
    login_user,
    create_market_wallet_address,
    create_market_session_data,
    create_market_session_fee_data,
    drop_dict_field
)
from ..response_templates import missing_field_response
from ..response_templates import validation_error_response


class TestMarketSessionFeeView(TransactionTestCase):
    """
        Tests for MarketSessionFee class.

    """
    reset_sequences = True  # reset DB AutoIncremental PK's on each test

    def setUp(self):
        self.client = APIClient()
        self.base_url = reverse("market:market-session-fee")
        self.super_user = create_and_login_superuser(self.client)
        self.wallet_address = create_market_wallet_address()
        self.session_data = create_market_session_data()
        self.session_fee_data = create_market_session_fee_data()

    def test_create_session_fee_no_auth(self):
        self.client.credentials(HTTP_AUTHORIZATION="")
        response = self.client.post(self.base_url,
                                    data=self.session_data,
                                    format="json")
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_list_session_fee_no_auth(self):
        self.client.credentials(HTTP_AUTHORIZATION="")
        response = self.client.get(self.base_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_create_session_fee_normal_user(self):
        user = create_user()
        login_user(client=self.client, user=user)
        MarketSession.objects.create(**self.session_data)

        response = self.client.post(self.base_url,
                                    data=self.session_fee_data,
                                    format="json")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_create_session_fee_super_user(self):
        login_user(client=self.client, user=self.super_user)
        MarketSession.objects.create(**self.session_data)

        response = self.client.post(self.base_url,
                                    data=self.session_fee_data,
                                    format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_create_session_fee_no_market_session_id(self):
        login_user(client=self.client, user=self.super_user)
        field_to_remove = "market_session"
        data = drop_dict_field(self.session_fee_data, field_to_remove)

        response = self.client.post(self.base_url,
                                    data=data,
                                    format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        expected_response = missing_field_response(field_name=field_to_remove)
        self.assertEqual(response.json(), expected_response)

    def test_create_session_fee_no_session_available(self):
        login_user(client=self.client, user=self.super_user)

        response = self.client.post(self.base_url,
                                    data=self.session_fee_data,
                                    format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        response_data = response.json()
        expected_response = validation_error_response(
            data={
                "market_session": ['This market session does not exist yet.']
            }
        )
        self.assertEqual(response_data, expected_response)

    def test_list_session_fee(self):
        login_user(client=self.client, user=self.super_user)
        MarketSession.objects.create(**self.session_data)
        MarketSessionFee.objects.create(
            market_session_id=self.session_fee_data["market_session"],
            amount=self.session_fee_data["amount"],
        )

        response = self.client.get(self.base_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        response_data = response.json()["data"]
        self.assertEqual(len(response_data), 1)
        self.assertEqual(response_data[0], self.session_fee_data)

