# flake8: noqa

from django.urls import reverse
from rest_framework import status
from django.test import TransactionTestCase
from rest_framework.test import APIClient

from ....models import MarketSession, MarketSessionTransactions
from users.models.user_resources import UserResources
from ...common import (
    create_and_login_superuser,
    create_market_session_data,
    create_user,
    login_user,
    drop_dict_field
)
from ..response_templates import missing_field_response


class TestMarketSessionTransactionsViewView(TransactionTestCase):
    """
        Tests for MarketSessionTransactionsView class.

    """
    reset_sequences = True  # reset DB AutoIncremental PK's on each test

    def setUp(self):
        self.client = APIClient()
        self.base_url = reverse("market:market-transactions")
        self.super_user = create_and_login_superuser(self.client)
        self.session_data = create_market_session_data()

        # Models:
        self.market_session = MarketSession.objects.create(**self.session_data)

    def test_list_session_transactions_no_auth(self):
        self.client.credentials(HTTP_AUTHORIZATION="")
        response = self.client.get(self.base_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_list_session_transactions_normal_user(self):
        # Create user and a resource:
        user = create_user()
        login_user(client=self.client, user=user)
        resource = UserResources.objects.create(**{
            "user_id": user.id,
            "name": "resource-1",
            "type": "measurements",
            "to_forecast": True
        })
        # Create transactions:
        transaction = MarketSessionTransactions.objects.create(
            **{
                "amount": 2000000,
                "market_session_id": self.market_session.id,
                "resource_id": resource.id,
                "user_id": user.id,
                "transaction_type": "transfer_in"
            }
        )

        response = self.client.get(self.base_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        response_data = response.json()["data"]
        expected_response = [
            {
                'market_session': 1,
                'user': str(user.id),
                'resource': str(resource.id),
                'amount': 2000000.0,
                'transaction_type': transaction.transaction_type,
                'registered_at': transaction.registered_at.strftime("%Y-%m-%dT%H:%M:%S.%fZ"),
                "resource_name": resource.name
            }
        ]
        self.assertEqual(len(response_data), 1)
        self.assertEqual(response_data, expected_response)

    def test_normal_user_access_other_user_transactions(self):
        # --------------- Configure User 1
        user1 = create_user()
        login_user(client=self.client, user=user1)
        resource11 = UserResources.objects.create(**{
            "user_id": user1.id,
            "name": "resource-1",
            "type": "measurements",
            "to_forecast": True
        })
        # Create transactions:
        MarketSessionTransactions.objects.create(
            **{
                "amount": 2000000,
                "market_session_id": self.market_session.id,
                "resource_id": resource11.id,
                "user_id": user1.id,
                "transaction_type": "transfer_in"
            }
        )
        # --------------- Configure User 2
        user2 = create_user(use_custom_data=True, **{
            'email': 'normal2@user.com',
            'password': 'normal2_foo',
            'first_name': 'Normal2',
            'last_name': 'Peanut2'})
        login_user(client=self.client, user=user2)
        resource21 = UserResources.objects.create(**{
            "user_id": user2.id,
            "name": "resource-1",
            "type": "measurements",
            "to_forecast": True
        })
        # Create transactions:
        transaction21 = MarketSessionTransactions.objects.create(
            **{
                "amount": 2000000,
                "market_session_id": self.market_session.id,
                "resource_id": resource21.id,
                "user_id": user2.id,
                "transaction_type": "transfer_in"
            }
        )

        # Attempt to get all resources:
        response = self.client.get(self.base_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        response_data = response.json()["data"]
        expected_response = [
            {
                'market_session': 1,
                'user': str(user2.id),
                'resource': str(resource21.id),
                'amount': 2000000.0,
                'transaction_type': transaction21.transaction_type,
                'registered_at': transaction21.registered_at.strftime("%Y-%m-%dT%H:%M:%S.%fZ"),
                "resource_name": resource21.name
            }
        ]
        self.assertEqual(len(response_data), 1)
        self.assertEqual(response_data, expected_response)

    def test_super_user_access_other_user_transactions(self):
        # --------------- Configure User 1
        user1 = create_user()
        login_user(client=self.client, user=user1)
        resource11 = UserResources.objects.create(**{
            "user_id": user1.id,
            "name": "resource-1",
            "type": "measurements",
            "to_forecast": True
        })
        # Create transactions:
        MarketSessionTransactions.objects.create(
            **{
                "amount": 2000000,
                "market_session_id": self.market_session.id,
                "resource_id": resource11.id,
                "user_id": user1.id,
                "transaction_type": "transfer_in"
            }
        )
        # --------------- Configure User 2
        user2 = create_user(use_custom_data=True, **{
            'email': 'normal2@user.com',
            'password': 'normal2_foo',
            'first_name': 'Normal2',
            'last_name': 'Peanut2'})
        login_user(client=self.client, user=user2)
        resource21 = UserResources.objects.create(**{
            "user_id": user2.id,
            "name": "resource-1",
            "type": "measurements",
            "to_forecast": True
        })
        # Create transactions:
        MarketSessionTransactions.objects.create(
            **{
                "amount": 2000000,
                "market_session_id": self.market_session.id,
                "resource_id": resource21.id,
                "user_id": user2.id,
                "transaction_type": "transfer_in"
            }
        )

        # Attempt to get all resources:
        login_user(self.client, user=self.super_user)
        response = self.client.get(self.base_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        response_data = response.json()["data"]
        self.assertEqual(len(response_data), 2)
