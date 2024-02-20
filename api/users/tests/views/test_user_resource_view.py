# flake8: noqa

from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from ...models import UserResources
from ..common import create_and_login_superuser, create_user, login_user
from .response_templates import conflict_error_response


class TestUserResourceView(APITestCase):
    """
        Tests for UserResourcesView class.

    """

    user_1 = {'email': 'normal1@user.com',
              'password': 'normal1_foo',
              'first_name': 'Normal1',
              'last_name': 'Peanut1'}
    user_2 = {'email': 'normal2@user.com',
              'password': 'normal2_foo',
              'first_name': 'Normal2',
              'last_name': 'Peanut2'}

    user_1_resources = [
        {"name": "u1-resource-1",
         "type": "measurements",
         "to_forecast": True},
        {"name": "u1-resource-2",
         "type": "measurements",
         "to_forecast": False},
        {"name": "u1-resource-3",
         "type": "forecasts",
         "to_forecast": False}
    ]

    user_2_resources = [
        {"name": "u2-resource-1",
         "type": "measurements",
         "to_forecast": True},
        {"name": "u2-resource-2",
         "type": "measurements",
         "to_forecast": False},
        {"name": "u2-resource-3",
         "type": "forecasts",
         "to_forecast": False}
    ]

    def setUp(self):
        self.base_url = reverse("user:resource")
        self.super_user = create_and_login_superuser(self.client)
        self.normal_user1 = create_user(use_custom_data=True, **self.user_1)
        self.normal_user2 = create_user(use_custom_data=True, **self.user_2)

    def register_resources(self, user_resources):
        for resource in user_resources:
            response = self.client.post(self.base_url, data=resource, format="json")
            self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_register_single_resource_no_auth(self):
        data = {"name": "resource-x",
                "type": "forecasts",
                "to_forecast": False}
        self.client.credentials(HTTP_AUTHORIZATION="")
        response = self.client.post(self.base_url, data=data, format="json")
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_list_resource_no_auth(self):
        self.client.credentials(HTTP_AUTHORIZATION="")
        response = self.client.get(self.base_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_register_single_resource(self):
        login_user(self.client, user=self.normal_user1)
        resource = self.user_1_resources[0]
        response = self.client.post(self.base_url, data=resource, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        response_data = response.json()["data"]
        self.assertEqual(response_data["name"], resource["name"])
        self.assertEqual(response_data["type"], resource["type"])
        self.assertEqual(response_data["to_forecast"], resource["to_forecast"])
        # Confirm if resource entry it correct in DB
        resource_id = response_data["id"]
        resource_data = UserResources.objects.filter(id=resource_id).get()
        self.assertEqual(resource_data.name, response_data["name"])
        self.assertEqual(resource_data.type, response_data["type"])
        self.assertEqual(resource_data.to_forecast, response_data["to_forecast"])

    def test_list_all_user_resources(self):
        login_user(self.client, user=self.normal_user1)
        self.register_resources(self.user_1_resources)
        response = self.client.get(self.base_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        response_data = response.json()["data"]
        self.assertEqual(len(response_data), len(self.user_1_resources))
        for resource in response_data:
            original = [x for x in self.user_1_resources if x["name"] == resource["name"]]
            # Check if this resource exists in the original resource list
            # and compare its attributes to original:
            self.assertEqual(len(original), 1)
            self.assertEqual(resource["type"], original[0]["type"])
            self.assertEqual(resource["to_forecast"], original[0]["to_forecast"])

    def test_list_user_resource_by_id(self):
        login_user(self.client, user=self.normal_user1)
        resource = self.user_1_resources[0]
        response = self.client.post(self.base_url, data=resource, format="json")
        resource_id = response.data["id"]
        params = {"resource": resource_id}
        response = self.client.get(self.base_url, params)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        response_data = response.json()["data"]
        self.assertEqual(response_data[0]["id"], resource_id)

    def test_list_other_user_resource_by_id(self):
        # login with user 1
        login_user(self.client, user=self.normal_user1)
        resource = self.user_1_resources[0]
        response = self.client.post(self.base_url, data=resource, format="json")
        resource_id = response.data["id"]
        # login with user 2
        login_user(self.client, user=self.normal_user2)
        # Try to access resource from user 1
        params = {"resource": resource_id}
        response = self.client.get(self.base_url, params)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        response_data = response.json()["data"]
        self.assertEqual(len(response_data), 0)

    def test_delete_resource(self):
        login_user(self.client, user=self.normal_user1)
        resource = self.user_1_resources[0]
        # Create resource:
        response = self.client.post(self.base_url, data=resource, format="json")
        resource_id = response.data["id"]
        # Check if resource exists:
        self.assertTrue(UserResources.objects.filter(id=resource_id))
        # Delete resource:
        response = self.client.delete(self.base_url + f"/{resource_id}")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # Check if resource exists:
        self.assertFalse(UserResources.objects.filter(id=resource_id))

    def test_delete_other_user_resource(self):
        # login with user 1
        login_user(self.client, user=self.normal_user1)
        resource = self.user_1_resources[0]
        response = self.client.post(self.base_url, data=resource, format="json")
        resource_id = response.data["id"]
        # login with user 2
        login_user(self.client, user=self.normal_user2)
        # Try to delete resource from user 1:
        response = self.client.delete(self.base_url + f"/{resource_id}")
        self.assertEqual(response.status_code, status.HTTP_409_CONFLICT)
        expected_response = conflict_error_response(
            message='Resource ID not found.'
        )
        # Check response message:
        self.assertEqual(response.json(), expected_response)
        # Check if resource still exists:
        self.assertTrue(UserResources.objects.filter(id=resource_id))

    def test_update_resource(self):
        login_user(self.client, user=self.normal_user1)
        resource = self.user_1_resources[0]
        # Create resource:
        response = self.client.post(self.base_url, data=resource, format="json")
        resource_id = response.data["id"]
        # Check if resource exists:
        self.assertTrue(UserResources.objects.filter(id=resource_id))
        # Update resource:
        resource["name"] = "new-resource-1"
        response = self.client.patch(self.base_url + f"/{resource_id}", data=resource, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        response_data = response.json()["data"]
        # Check if resource ID is the same:
        self.assertEqual(response_data["id"], resource_id)
        # Check if resource name was updated:
        resource_data = UserResources.objects.get(id=resource_id)
        self.assertTrue(resource_data.name, resource["name"])

    def test_superuser_list_resource(self):
        login_user(self.client, user=self.super_user)
        self.register_resources(self.user_1_resources)
        self.register_resources(self.user_2_resources)
        # Superuser should have access to all resources from all users:
        response = self.client.get(self.base_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        resource_data = response.json()["data"]
        self.assertEqual(len(resource_data), len(self.user_1_resources) + len(self.user_2_resources))
