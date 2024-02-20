# flake8: noqa

from django.urls import reverse
from rest_framework import status
from django.test import TransactionTestCase
from rest_framework.test import APIClient

from ....models import MarketSession, MarketWalletAddress
from ...common import (
    create_and_login_superuser,
    create_user,
    login_user,
    create_market_wallet_address,
    create_market_session_data,
    drop_dict_field
)
from ..response_templates import missing_field_response
from ..response_templates import conflict_error_response


class TestMarketSessionView(TransactionTestCase):
    """
        Tests for MarketSession class.

    """
    reset_sequences = True  # reset DB AutoIncremental PK's on each test

    def setUp(self):
        self.client = APIClient()
        self.base_url = reverse("market:market-session")
        self.super_user = create_and_login_superuser(self.client)
        self.wallet_address = create_market_wallet_address()
        self.session_data = create_market_session_data()

    def test_create_session_no_auth(self):
        self.client.credentials(HTTP_AUTHORIZATION="")
        response = self.client.post(self.base_url,
                                    data=self.session_data,
                                    format="json")
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_list_session_no_auth(self):
        self.client.credentials(HTTP_AUTHORIZATION="")
        response = self.client.get(self.base_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_create_session_normal_user(self):
        user = create_user()
        login_user(client=self.client, user=user)

        response = self.client.post(self.base_url,
                                    data=self.session_data,
                                    format="json")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_create_session_super_user(self):
        login_user(client=self.client, user=self.super_user)

        response = self.client.post(self.base_url,
                                    data=self.session_data,
                                    format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_create_session_no_session_number(self):
        login_user(client=self.client, user=self.super_user)
        field_to_remove = "session_number"
        data = drop_dict_field(self.session_data, field_to_remove)

        response = self.client.post(self.base_url,
                                    data=data,
                                    format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        expected_response = missing_field_response(field_name=field_to_remove)
        self.assertEqual(response.json(), expected_response)

    def test_create_session_no_market_price(self):
        login_user(client=self.client, user=self.super_user)
        field_to_remove = "market_price"
        data = drop_dict_field(self.session_data, field_to_remove)

        response = self.client.post(self.base_url,
                                    data=data,
                                    format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        expected_response = missing_field_response(field_name=field_to_remove)
        self.assertEqual(response.json(), expected_response)

    def test_create_session_no_bmin(self):
        field_to_remove = "b_min"
        data = drop_dict_field(self.session_data, field_to_remove)
        login_user(client=self.client, user=self.super_user)

        response = self.client.post(self.base_url,
                                    data=data,
                                    format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        expected_response = missing_field_response(field_name=field_to_remove)
        self.assertEqual(response.json(), expected_response)

    def test_create_session_no_bmax(self):
        field_to_remove = "b_max"
        data = drop_dict_field(self.session_data, field_to_remove)
        login_user(client=self.client, user=self.super_user)

        response = self.client.post(self.base_url,
                                    data=data,
                                    format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        expected_response = missing_field_response(field_name=field_to_remove)
        self.assertEqual(response.json(), expected_response)

    def test_create_session_no_n_price_steps(self):
        login_user(client=self.client, user=self.super_user)
        field_to_remove = "n_price_steps"
        data = drop_dict_field(self.session_data, field_to_remove)

        response = self.client.post(self.base_url,
                                    data=data,
                                    format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        expected_response = missing_field_response(field_name=field_to_remove)
        self.assertEqual(response.json(), expected_response)

    def test_create_session_no_delta(self):
        login_user(client=self.client, user=self.super_user)
        field_to_remove = "delta"
        data = drop_dict_field(self.session_data, field_to_remove)

        response = self.client.post(self.base_url,
                                    data=data,
                                    format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        expected_response = missing_field_response(field_name=field_to_remove)
        self.assertEqual(response.json(), expected_response)

    def test_create_session(self):
        login_user(client=self.client, user=self.super_user)

        response = self.client.post(self.base_url,
                                    data=self.session_data,
                                    format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        response_data = response.json()["data"]
        self.assertEqual(response_data["session_number"], self.session_data["session_number"])
        self.assertEqual(response_data["market_price"], self.session_data["market_price"])
        self.assertEqual(response_data["b_min"], self.session_data["b_min"])
        self.assertEqual(response_data["b_max"], self.session_data["b_max"])
        self.assertEqual(response_data["n_price_steps"], self.session_data["n_price_steps"])
        self.assertEqual(response_data["delta"], self.session_data["delta"])

    def test_create_session_no_wallet_address(self):
        login_user(client=self.client, user=self.super_user)
        # Delete current market wallet address
        MarketWalletAddress.objects.filter(
            wallet_address=self.wallet_address.wallet_address
        ).delete()

        # Try to create session without market wallet address
        response = self.client.post(self.base_url, data=self.session_data, format="json")
        self.assertEqual(response.status_code, status.HTTP_409_CONFLICT)

        expected_response = conflict_error_response(
            message='Market wallet address not found. '
                    'Register an address first.'
        )
        self.assertEqual(response.json(), expected_response)

    def test_list_session_without_creation(self):
        login_user(client=self.client, user=self.super_user)
        response = self.client.get(self.base_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        response_data = response.json()["data"]
        self.assertEqual(len(response_data), 0)

    def test_list_session(self):
        MarketSession.objects.create(**self.session_data)
        login_user(client=self.client, user=self.super_user)

        response = self.client.get(self.base_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        response_data = response.json()["data"]
        self.assertEqual(len(response_data), 1)

    def test_list_session_open_status(self):
        MarketSession.objects.create(status="open", **self.session_data)
        login_user(client=self.client, user=self.super_user)

        response = self.client.get(self.base_url,
                                   params={"status": "open"})
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        response_data = response.json()["data"]
        self.assertEqual(len(response_data), 1)
        self.assertEqual(response_data[0]["status"], "open")

    def test_list_session_closed_status(self):
        MarketSession.objects.create(status="closed", **self.session_data)
        login_user(client=self.client, user=self.super_user)

        response = self.client.get(self.base_url,
                                   params={"status": "closed"})
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        response_data = response.json()["data"]
        self.assertEqual(len(response_data), 1)
        self.assertEqual(response_data[0]["status"], "closed")

    def test_list_session_running_status(self):
        MarketSession.objects.create(status="running", **self.session_data)
        login_user(client=self.client, user=self.super_user)

        response = self.client.get(self.base_url,
                                   params={"status": "running"})
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        response_data = response.json()["data"]
        self.assertEqual(len(response_data), 1)
        self.assertEqual(response_data[0]["status"], "running")

    def test_list_session_finished_status(self):
        MarketSession.objects.create(status="finished", **self.session_data)
        login_user(client=self.client, user=self.super_user)

        response = self.client.get(self.base_url,
                                   params={"status": "finished"})
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        response_data = response.json()["data"]
        self.assertEqual(len(response_data), 1)
        self.assertEqual(response_data[0]["status"], "finished")

    def test_create_session_with_already_open_session(self):
        MarketSession.objects.create(**self.session_data)
        login_user(client=self.client, user=self.super_user)

        # Try to create new session - should fail as sessions can only
        # be created if there are no unfinished session
        data = create_market_session_data(session_number=2)
        response = self.client.post(self.base_url,
                                    data=data,
                                    format="json")
        self.assertEqual(response.status_code, status.HTTP_409_CONFLICT)

        expected_response = conflict_error_response(
            message='Unable to create new session. '
                    'There are still unfinished sessions.'
        )
        self.assertEqual(response.json(), expected_response)

    def test_update_session_status(self):
        MarketSession.objects.create(**self.session_data)
        login_user(client=self.client, user=self.super_user)
        valid_status = MarketSession.MarketStatus.values

        response = self.client.get(self.base_url, params={"status": "open"})
        session_id = response.json()["data"][0]["id"]

        data = self.session_data.copy()
        for status_choice in valid_status:
            data["status"] = status_choice
            response = self.client.patch(self.base_url + f"/{session_id}",
                                         data=data)
            response_data = response.json()["data"]
            self.assertEqual(response.status_code, status.HTTP_200_OK)
            self.assertEqual(response_data["id"], session_id)
            self.assertEqual(response_data["status"], status_choice)

    def test_list_latest_session(self):
        sess1 = create_market_session_data(session_number=1)
        sess2 = create_market_session_data(session_number=2)
        sess3 = create_market_session_data(session_number=3)
        MarketSession.objects.create(**sess1)
        MarketSession.objects.create(**sess2)
        MarketSession.objects.create(**sess3)
        user = create_user()
        login_user(client=self.client, user=user)

        response = self.client.get(self.base_url, {"latest_only": True})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        response_data = response.json()["data"]

        self.assertEqual(len(response_data), 1)
        self.assertEqual(response_data[0]["id"], 3)

    def test_list_latest_session_bad_query_params(self):
        user = create_user()
        login_user(client=self.client, user=user)
        response = self.client.get(self.base_url, {"latest_only": True})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        response = self.client.get(self.base_url, {"latest_only": False})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        response = self.client.get(self.base_url, {"latest_only": "asdsd"})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        response_data = response.json()["data"]
        expected_response = ["Query param 'latest_only' must be a boolean "
                             "(true/false)"]
        self.assertEqual(response_data, expected_response)

    def test_update_session_invalid_status(self):
        login_user(client=self.client, user=self.super_user)
        response = self.client.post(self.base_url,
                                    data=self.session_data,
                                    format="json")
        session_id = response.json()["data"]["id"]
        data = self.session_data.copy()
        data["status"] = "invalid_status"
        response = self.client.patch(self.base_url + f"/{session_id}",
                                     data=data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_multiple_sessions(self):
        login_user(client=self.client, user=self.super_user)
        for session_number in range(0, 5):
            # Create session ('open' status by default)
            data = create_market_session_data(session_number=session_number)
            response = self.client.post(self.base_url,
                                        data=data,
                                        format="json")
            self.assertEqual(response.status_code, status.HTTP_200_OK)
            # Change session status to 'finished'
            session_id = response.json()["data"]["id"]
            data["status"] = "finished"
            response = self.client.patch(self.base_url + f"/{session_id}",
                                         data=data)
            self.assertEqual(response.status_code, status.HTTP_200_OK)

            db_entries = MarketSession.objects.all()
            self.assertEqual(len(db_entries), session_number + 1)
