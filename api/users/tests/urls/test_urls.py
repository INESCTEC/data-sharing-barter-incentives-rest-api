from django.test import SimpleTestCase
from django.urls import reverse, resolve

from ...views.user import UserRegisterView, UserListView
from ...views.user_resources import UserResourcesView
from ...views.user_wallet import UserWalletAddressView


class TestUrls(SimpleTestCase):

    def test_list_url_is_resolved(self):

        url = reverse('user:register')
        self.assertEqual(resolve(url).func.view_class, UserRegisterView)

        url = reverse('user:resource')
        self.assertEqual(resolve(url).func.view_class, UserResourcesView)

        url = reverse('user:list')
        self.assertEqual(resolve(url).func.view_class, UserListView)

        url = reverse('user:wallet-address')
        self.assertEqual(resolve(url).func.view_class, UserWalletAddressView)
