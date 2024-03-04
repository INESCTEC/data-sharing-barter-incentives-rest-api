# flake8: noqa

import uuid

from django.urls import reverse
from rest_framework import status
from django.test import TransactionTestCase
from rest_framework.test import APIClient

from ....models import (
    MarketSession,
    MarketSessionBid,
    MarketSessionBidPayment
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
from ..response_templates import conflict_error_response


class TestMarketSessionBidView(TransactionTestCase):
    """
    Tests for MarketSessionBidView class.

    """
    reset_sequences = True  # reset DB AutoIncremental PK's on each test

    def setUp(self):
        self.client = APIClient()
        self.base_url = reverse("market:market-session-bid")
        self.super_user = create_and_login_superuser(self.client)
        self.wallet_address = create_market_wallet_address()
        self.session_data = create_market_session_data()
        self.users = create_users_and_resources(nr_users=2, nr_resources_per_user=2)

    def test_create_bid_no_auth(self):
        self.client.credentials(HTTP_AUTHORIZATION="")
        response = self.client.post(self.base_url,
                                    data=self.session_data,
                                    format="json")
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_list_bid_no_auth(self):
        self.client.credentials(HTTP_AUTHORIZATION="")
        response = self.client.get(self.base_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_create_bid(self):
        user = self.users[0]["user"]
        resource = self.users[0]["resources"][0]
        login_user(client=self.client, user=user)
        bid_data = create_market_bid_data(resource=resource.id)
        market_session = MarketSession.objects.create(
            status="open",
            **self.session_data
        )

        response = self.client.post(self.base_url,
                                    data=bid_data,
                                    format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        response_data = response.json()["data"]
        self.assertEqual(response_data["market_session"], market_session.id)
        self.assertEqual(response_data["user"], str(user.id))
        self.assertEqual(response_data["resource"], str(resource.id))
        assert uuid.UUID(response_data["id"], version=4), "id is not a valid UUID."
        self.assertEqual(response_data["bid_price"], bid_data["bid_price"])
        self.assertEqual(response_data["gain_func"], bid_data["gain_func"])
        self.assertEqual(response_data["max_payment"], bid_data["max_payment"])

        bid_model_data = MarketSessionBid.objects.get(id=response_data["id"])
        self.assertEqual(bid_model_data.market_session_id, market_session.id)
        self.assertEqual(bid_model_data.user_id, user.id)
        self.assertEqual(bid_model_data.resource_id, resource.id)
        self.assertEqual(bid_model_data.bid_price, bid_data["bid_price"])
        self.assertEqual(bid_model_data.max_payment, bid_data["max_payment"])
        self.assertEqual(bid_model_data.gain_func, bid_data["gain_func"])
        self.assertEqual(bid_model_data.has_forecasts, False)
        self.assertEqual(bid_model_data.confirmed, False)

        bid_payment_model_data = MarketSessionBidPayment.objects.filter(market_bid_id=response_data["id"])
        assert not bid_payment_model_data

    def test_add_tangle_msg_id(self):
        user = self.users[0]["user"]
        resource = self.users[0]["resources"][0]
        login_user(client=self.client, user=user)
        bid_data = create_market_bid_data(resource=resource.id)
        MarketSession.objects.create(status="open", **self.session_data)

        # Create Bid:
        response = self.client.post(self.base_url,
                                    data=bid_data,
                                    format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        response_data = response.json()["data"]

        # Add tangle msg id to bid:
        response = self.client.patch(
            self.base_url + f"/{response_data['id']}",
            data={"tangle_msg_id": bid_data["tangle_msg_id"]},
            format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        response_data = response.json()["data"]

        bid_payment_model_data = MarketSessionBidPayment.objects.get(market_bid_id=response_data["bid_id"])
        self.assertEqual(str(bid_payment_model_data.market_bid_id), response_data["bid_id"])
        self.assertEqual(str(bid_payment_model_data.tangle_msg_id), response_data["tangle_msg_id"])
        self.assertEqual(bid_payment_model_data.is_solid, False)

    def test_add_tangle_msg_id_duplicated(self):
        user = self.users[0]["user"]
        resource_1 = self.users[0]["resources"][0]
        resource_2 = self.users[0]["resources"][1]
        login_user(client=self.client, user=user)
        bid_data_1 = create_market_bid_data(resource=resource_1.id)
        bid_data_2 = create_market_bid_data(resource=resource_2.id)
        MarketSession.objects.create(status="open", **self.session_data)

        # Create First Bid:
        response_1 = self.client.post(self.base_url,
                                      data=bid_data_1,
                                      format="json")
        self.assertEqual(response_1.status_code, status.HTTP_200_OK)
        response_1_data = response_1.json()["data"]

        # Create Second Bid (other resource):
        response_2 = self.client.post(self.base_url,
                                      data=bid_data_2,
                                      format="json")
        self.assertEqual(response_2.status_code, status.HTTP_200_OK)
        response_2_data = response_2.json()["data"]

        # Add tangle msg id to bid 1:
        response = self.client.patch(
            self.base_url + f"/{response_1_data['id']}",
            data={"tangle_msg_id": bid_data_1["tangle_msg_id"]},
            format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Add tangle msg id to bid 2 (try same tangle msg id):
        response = self.client.patch(
            self.base_url + f"/{response_2_data['id']}",
            data={"tangle_msg_id": bid_data_2["tangle_msg_id"]},
            format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_409_CONFLICT)

    def test_already_has_tangle_msg_id(self):
        user = self.users[0]["user"]
        resource = self.users[0]["resources"][0]
        login_user(client=self.client, user=user)
        bid_data = create_market_bid_data(resource=resource.id)
        MarketSession.objects.create(status="open", **self.session_data)

        # Create Bid:
        response = self.client.post(self.base_url,
                                    data=bid_data,
                                    format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        response_data = response.json()["data"]

        # Add tangle msg id to bid:
        response = self.client.patch(
            self.base_url + f"/{response_data['id']}",
            data={"tangle_msg_id": bid_data["tangle_msg_id"]},
            format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Try to add again tangle msg id to bid:
        response = self.client.patch(
            self.base_url + f"/{response_data['id']}",
            data={"tangle_msg_id": bid_data["tangle_msg_id"]},
            format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_409_CONFLICT)

    def test_create_bid_no_max_payment(self):
        MarketSession.objects.create(status="open", **self.session_data)

        user = self.users[0]["user"]
        resource = self.users[0]["resources"][0]
        login_user(client=self.client, user=user)
        bid_data = create_market_bid_data(resource=resource.id)
        field_to_remove = "max_payment"
        bid_data = drop_dict_field(bid_data, field_to_remove)

        response = self.client.post(self.base_url,
                                    data=bid_data,
                                    format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        expected_response = missing_field_response(field_name=field_to_remove)
        self.assertEqual(response.json(), expected_response)

    def test_create_bid_no_bid_price(self):
        MarketSession.objects.create(status="open", **self.session_data)

        user = self.users[0]["user"]
        resource = self.users[0]["resources"][0]
        login_user(client=self.client, user=user)
        bid_data = create_market_bid_data(resource=resource.id)
        field_to_remove = "bid_price"
        bid_data = drop_dict_field(bid_data, field_to_remove)

        response = self.client.post(self.base_url,
                                    data=bid_data,
                                    format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        expected_response = missing_field_response(field_name=field_to_remove)
        self.assertEqual(response.json(), expected_response)

    def test_create_bid_no_resource_id(self):
        MarketSession.objects.create(status="open", **self.session_data)

        user = self.users[0]["user"]
        resource = self.users[0]["resources"][0]
        login_user(client=self.client, user=user)
        bid_data = create_market_bid_data(resource=resource.id)
        field_to_remove = "resource"
        bid_data = drop_dict_field(bid_data, field_to_remove)

        response = self.client.post(self.base_url,
                                    data=bid_data,
                                    format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        expected_response = missing_field_response(field_name=field_to_remove)
        self.assertEqual(response.json(), expected_response)

    def test_create_bid_no_market_session(self):
        MarketSession.objects.create(status="open", **self.session_data)

        user = self.users[0]["user"]
        resource = self.users[0]["resources"][0]
        login_user(client=self.client, user=user)
        bid_data = create_market_bid_data(resource=resource.id)
        field_to_remove = "market_session"
        bid_data = drop_dict_field(bid_data, field_to_remove)

        response = self.client.post(self.base_url,
                                    data=bid_data,
                                    format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        expected_response = missing_field_response(field_name=field_to_remove)
        self.assertEqual(response.json(), expected_response)

    def test_create_bid_no_gain_func(self):
        MarketSession.objects.create(status="open", **self.session_data)

        user = self.users[0]["user"]
        resource = self.users[0]["resources"][0]
        login_user(client=self.client, user=user)
        bid_data = create_market_bid_data(resource=resource.id)
        field_to_remove = "gain_func"
        bid_data = drop_dict_field(bid_data, field_to_remove)

        response = self.client.post(self.base_url,
                                    data=bid_data,
                                    format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        expected_response = missing_field_response(field_name=field_to_remove)
        self.assertEqual(response.json(), expected_response)

    def test_create_bid_for_duplicated_resource(self):
        MarketSession.objects.create(status="open", **self.session_data)

        user = self.users[0]["user"]
        resource = self.users[0]["resources"][0]
        login_user(client=self.client, user=user)
        bid_data = create_market_bid_data(
            resource=resource.id,
            tangle_msg_id="c3a953db074113291020b39eeb20d116833f31f590b533e967efb247100bd674"
        )
        response = self.client.post(self.base_url,
                                    data=bid_data,
                                    format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # -- Same resource, but change tangle message ID:
        bid_data = create_market_bid_data(
            resource=resource.id,
            tangle_msg_id="caaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa"
        )
        response = self.client.post(self.base_url,
                                    data=bid_data,
                                    format="json")
        self.assertEqual(response.status_code, status.HTTP_409_CONFLICT)
        response_data = response.json()
        expected_response = conflict_error_response(
            message=f'The user already has a placed bid '
                    f'for session ID 1 and resource ID {str(resource.id)}.'
        )
        self.assertEqual(response_data, expected_response)

    def test_list_bid(self):
        user = self.users[0]["user"]
        resource = self.users[0]["resources"][0]
        login_user(client=self.client, user=user)
        bid_data = create_market_bid_data(resource=resource.id)
        MarketSession.objects.create(status="open", **self.session_data)

        # -- Create bid:
        response = self.client.post(self.base_url,
                                    data=bid_data,
                                    format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # -- Retrieve bid details:
        response = self.client.get(self.base_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        response_data = response.json()["data"]

        # Force UUID replacement for unittests purposes. Confirms if
        # valid UUID and then replaces it for final structure validation.
        assert uuid.UUID(response_data[0]["id"], version=4), f"'id' is not a valid UUID."
        response_data[0]["id"] = "valid_uuid"

        expected_response = {
            'id': 'valid_uuid',
            'max_payment': 1000000,
            'bid_price': 1000,
            'gain_func': 'mse',
            'confirmed': False,
            'has_forecasts': False,
            'user': str(user.id),
            'resource': str(resource.id),
            'market_session': 1,
            'tangle_msg_id': None
        }
        self.assertEqual(len(response_data), 1)
        response_data[0].pop("registered_at")
        self.assertEqual(response_data[0], expected_response)

    def test_normal_user_list_other_user_bids(self):
        MarketSession.objects.create(status="open", **self.session_data)

        # -- Create bid for user 1:
        user1 = self.users[0]["user"]
        resource11 = self.users[0]["resources"][0]
        login_user(client=self.client, user=user1)
        bid_data = create_market_bid_data(
            resource=resource11.id,
            tangle_msg_id="c3a953db074113291020b39eeb20d116833f31f590b533e967efb247100bd674"
        )
        # -- Create bid:
        response = self.client.post(self.base_url,
                                    data=bid_data,
                                    format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # -- Create bid for user 2:
        user2 = self.users[1]["user"]
        resource21 = self.users[1]["resources"][0]
        login_user(client=self.client, user=user2)
        bid_data = create_market_bid_data(
            resource=resource21.id,
            tangle_msg_id="caaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa"
        )
        # -- Create bid:
        response = self.client.post(self.base_url,
                                    data=bid_data,
                                    format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # -- Retrieve bid details:
        response = self.client.get(self.base_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        response_data = response.json()["data"]
        self.assertEqual(len(response_data), 1)

    def test_super_user_list_other_user_bids(self):
        MarketSession.objects.create(status="open", **self.session_data)

        # -- Create bid for user 1:
        user1 = self.users[0]["user"]
        resource11 = self.users[0]["resources"][0]
        login_user(client=self.client, user=user1)
        bid_data = create_market_bid_data(
            resource=resource11.id,
            tangle_msg_id="c3a953db074113291020b39eeb20d116833f31f590b533e967efb247100bd674"
        )
        # -- Create bid:
        response = self.client.post(self.base_url,
                                    data=bid_data,
                                    format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # -- Create bid for user 2:
        user2 = self.users[1]["user"]
        resource21 = self.users[1]["resources"][0]
        login_user(client=self.client, user=user2)
        bid_data = create_market_bid_data(
            resource=resource21.id,
            tangle_msg_id="caaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa"
        )
        # -- Create bid:
        response = self.client.post(self.base_url,
                                    data=bid_data,
                                    format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # -- Retrieve bid details:
        login_user(client=self.client, user=self.super_user)
        response = self.client.get(self.base_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        response_data = response.json()["data"]
        self.assertEqual(len(response_data), 2)

    def test_create_bid_on_staged_session(self):
        user = self.users[0]["user"]
        resource = self.users[0]["resources"][0]
        login_user(client=self.client, user=user)
        bid_data = create_market_bid_data(resource=resource.id)
        market_session = MarketSession.objects.create(
            status="staged",
            **self.session_data
        )

        response = self.client.post(self.base_url,
                                    data=bid_data,
                                    format="json")
        self.assertEqual(response.status_code, status.HTTP_409_CONFLICT)

        response_data = response.json()
        expected_response = conflict_error_response(
            message=f'Market session {market_session.id} is not open for bids.'
        )
        self.assertEqual(response_data, expected_response)

    def test_create_bid_on_closed_session(self):
        user = self.users[0]["user"]
        resource = self.users[0]["resources"][0]
        login_user(client=self.client, user=user)
        bid_data = create_market_bid_data(resource=resource.id)
        market_session = MarketSession.objects.create(
            status="closed",
            **self.session_data
        )

        response = self.client.post(self.base_url,
                                    data=bid_data,
                                    format="json")
        self.assertEqual(response.status_code, status.HTTP_409_CONFLICT)

        response_data = response.json()
        expected_response = conflict_error_response(
            message=f'Market session {market_session.id} is not open for bids.'
        )
        self.assertEqual(response_data, expected_response)

    def test_create_bid_on_running_session(self):
        user = self.users[0]["user"]
        resource = self.users[0]["resources"][0]
        login_user(client=self.client, user=user)
        bid_data = create_market_bid_data(resource=resource.id)
        market_session = MarketSession.objects.create(
            status="running",
            **self.session_data
        )

        response = self.client.post(self.base_url,
                                    data=bid_data,
                                    format="json")
        self.assertEqual(response.status_code, status.HTTP_409_CONFLICT)

        response_data = response.json()
        expected_response = conflict_error_response(
            message=f'Market session {market_session.id} is not open for bids.'
        )
        self.assertEqual(response_data, expected_response)

    def test_create_bid_on_finished_session(self):
        user = self.users[0]["user"]
        resource = self.users[0]["resources"][0]
        login_user(client=self.client, user=user)
        bid_data = create_market_bid_data(resource=resource.id)
        market_session = MarketSession.objects.create(
            status="finished",
            **self.session_data
        )

        response = self.client.post(self.base_url,
                                    data=bid_data,
                                    format="json")
        self.assertEqual(response.status_code, status.HTTP_409_CONFLICT)

        response_data = response.json()
        expected_response = conflict_error_response(
            message=f'Market session {market_session.id} is not open for bids.'
        )
        self.assertEqual(response_data, expected_response)

