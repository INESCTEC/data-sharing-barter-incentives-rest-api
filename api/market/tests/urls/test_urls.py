from django.test import TestCase
from django.urls import reverse, resolve

from ...views.market_session import (
    MarketSessionView,
    MarketSessionFeeView,
    MarketPriceWeightView,
    MarketSessionTransactionsView
)
from ...views.market_session_bid import (
    MarketSessionBidView,
    MarketValidateSessionBidView
)
from ...views.market_balance import (
    MarketBalanceView,
    MarketSessionBalanceView,
    BalanceTransferOutView
)
from ...views.market_wallet import MarketWalletAddressView


class TestUrls(TestCase):

    def test_list_url_is_resolved(self):

        url = reverse('market:market-wallet-address')
        self.assertEqual(resolve(url).func.view_class, MarketWalletAddressView)

        url = reverse('market:market-session')
        self.assertEqual(resolve(url).func.view_class, MarketSessionView)

        url = reverse('market:market-session-bid')
        self.assertEqual(resolve(url).func.view_class, MarketSessionBidView)

        url = reverse('market:market-validate-session-bid')
        self.assertEqual(resolve(url).func.view_class, MarketValidateSessionBidView)

        url = reverse('market:market-session-price-weight')
        self.assertEqual(resolve(url).func.view_class, MarketPriceWeightView)

        url = reverse('market:market-transactions')
        self.assertEqual(resolve(url).func.view_class, MarketSessionTransactionsView)

        url = reverse('market:market-session-balance')
        self.assertEqual(resolve(url).func.view_class, MarketSessionBalanceView)

        url = reverse('market:market-session-balance')
        self.assertEqual(resolve(url).func.view_class, MarketSessionBalanceView)

        url = reverse('market:market-session-fee')
        self.assertEqual(resolve(url).func.view_class, MarketSessionFeeView)

        url = reverse('market:market-balance')
        self.assertEqual(resolve(url).func.view_class, MarketBalanceView)

        url = reverse('market:transfer-out-request')
        self.assertEqual(resolve(url).func.view_class, BalanceTransferOutView)
