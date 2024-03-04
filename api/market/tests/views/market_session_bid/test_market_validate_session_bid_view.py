# flake8: noqa
import uuid

from django.urls import reverse
from rest_framework import status
from django.test import TransactionTestCase
from rest_framework.test import APIClient

from ....models import (
    MarketSession,
    MarketSessionBid,
    MarketSessionBidPayment,
    MarketBalance,
    MarketSessionBalance,
    MarketSessionTransactions
)
from ...common import (
    create_and_login_superuser,
    login_user,
    create_market_wallet_address,
    create_market_session_data,
    create_market_bid_data,
    drop_dict_field
)
from ...pipelines import create_users_and_resources
from ..response_templates import missing_field_response


class TestMarketValidateSessionBidView(TransactionTestCase):
    """
    Tests for MarketSessionBidView class.

    """
    reset_sequences = True  # reset DB AutoIncremental PK's on each test

    def setUp(self):
        self.client = APIClient()
        self.base_url = reverse("market:market-validate-session-bid")
        self.super_user = create_and_login_superuser(self.client)
        self.wallet_address = create_market_wallet_address()
        self.session_data = create_market_session_data()
        self.users = create_users_and_resources(nr_users=1,
                                                nr_resources_per_user=1)
        self.market_session = MarketSession.objects.create(
            status="open",
            **self.session_data
        )

    def test_normal_user_create_and_validate_bid(self):
        user = self.users[0]["user"]
        resource = self.users[0]["resources"][0]
        login_user(client=self.client, user=user)
        bid_data = create_market_bid_data(resource=resource.id)

        # Create bid:
        response = self.client.post(reverse("market:market-session-bid"),
                                    data=bid_data,
                                    format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Validate Bid as super user:
        validation_data = {
            "tangle_msg_id": bid_data["tangle_msg_id"]
        }
        response = self.client.post(self.base_url,
                                    data=validation_data,
                                    format="json")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_super_user_validate_bid_no_tangle_id(self):
        user = self.users[0]["user"]
        resource = self.users[0]["resources"][0]
        login_user(client=self.client, user=user)
        bid_data = create_market_bid_data(resource=resource.id)

        # Create bid:
        response = self.client.post(reverse("market:market-session-bid"),
                                    data=bid_data,
                                    format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Validate Bid as super user:
        login_user(client=self.client, user=self.super_user)
        validation_data = {
            "tangle_msg_id": bid_data["tangle_msg_id"]
        }
        response = self.client.post(self.base_url,
                                    data=validation_data,
                                    format="json")
        self.assertEqual(response.status_code, status.HTTP_409_CONFLICT)

    def test_super_user_create_and_validate_bid(self):
        user = self.users[0]["user"]
        resource = self.users[0]["resources"][0]
        login_user(client=self.client, user=user)
        bid_data = create_market_bid_data(resource=resource.id)

        # Create bid:
        response = self.client.post(reverse("market:market-session-bid"),
                                    data=bid_data,
                                    format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        response_data = response.json()["data"]

        # Add tangle msg id to bid:
        response = self.client.patch(
            reverse("market:market-session-bid") + f"/{response_data['id']}",
            data={"tangle_msg_id": bid_data["tangle_msg_id"]},
            format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Validate Bid as super user:
        login_user(client=self.client, user=self.super_user)
        validation_data = {
            "tangle_msg_id": bid_data["tangle_msg_id"]
        }
        response = self.client.post(self.base_url,
                                    data=validation_data,
                                    format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        response_data = response.json()["data"]

        _bid_id = response_data["market_bid"]
        for key in ["market_bid"]:
            # Force UUID replacement for testing purposes:
            assert uuid.UUID(response_data[key], version=4), f"{key} is not a valid UUID."
            response_data[key] = "valid_uuid"

        expected_response = {
            'market_bid': "valid_uuid",
            'market_session': 1,
            'tangle_msg_id': 'c3a953db074113291020b39eeb20d116833f31f590b533e967efb247100bd674',
            'user_wallet_address': 'atoi1qpx2srs3nw08yuwtyrhsksku5yfkld2fmmmj643nwq4cqyu5xtgfjhh46sp',
            'confirmed': True
        }
        self.assertEqual(response_data, expected_response)

        # Check if bid status was updated in table:
        bid_model_data = MarketSessionBid.objects.get(id=_bid_id)
        self.assertEqual(bid_model_data.confirmed, True)

        # Check if is_solid flag (meaning it is solid in IOTA Tangle) is True
        bid_payment_model_data = MarketSessionBidPayment.objects.get(market_bid_id=_bid_id)
        self.assertEqual(bid_payment_model_data.is_solid, True)

        # Market balance should be updated (= max_payment) as bid is validated:
        balance = MarketBalance.objects.filter(user_id=user.id)
        self.assertEqual(len(balance), 1)
        self.assertEqual(balance[0].balance, bid_data["max_payment"])

        # Market session initial balance should be = max_payment:
        session_balance = MarketSessionBalance.objects.filter(user_id=user.id)
        self.assertEqual(len(session_balance), 1)
        self.assertEqual(session_balance[0].session_balance, bid_data["max_payment"])

        # A Market 'transfer_in' transaction should be issued as bid is valid:
        session_tx = MarketSessionTransactions.objects.filter(user_id=user.id)
        self.assertEqual(len(session_tx), 1)
        self.assertEqual(session_tx[0].transaction_type, "transfer_in")
        self.assertEqual(session_tx[0].amount, bid_data["max_payment"])
