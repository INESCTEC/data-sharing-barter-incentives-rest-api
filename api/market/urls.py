from django.urls import re_path

from .views.market_session import (
    MarketSessionView,
    MarketSessionUpdateView,
    MarketSessionFeeView,
    MarketPriceWeightView,
    MarketSessionTransactionsView
)
from .views.market_session_bid import (
    MarketSessionBidView,
    MarketSessionBidUpdateView,
    MarketValidateSessionBidView
)
from .views.market_balance import (
    MarketBalanceView,
    MarketSessionBalanceView,
    BalanceTransferOutView
)
from .views.market_wallet import MarketWalletAddressView
from rest_framework.urlpatterns import format_suffix_patterns

app_name = "market"

urlpatterns = [
    re_path('wallet-address/?$', MarketWalletAddressView.as_view(), name="market-wallet-address"),
    re_path('session/?$', MarketSessionView.as_view(), name="market-session"),
    re_path('session/(?P<session_id>[0-9]+)$', MarketSessionUpdateView.as_view(), name="market-session-update"),
    re_path('bid/?$', MarketSessionBidView.as_view(), name="market-session-bid"),
    re_path('bid/(?P<bid_id>[0-9a-f-]+)$', MarketSessionBidUpdateView.as_view(), name="market-session-bid-update"),
    re_path('validate/bid-payment?$', MarketValidateSessionBidView.as_view(), name="market-validate-session-bid"),
    re_path('price-weight/?$', MarketPriceWeightView.as_view(), name="market-session-price-weight"),
    re_path('session-transactions/?$', MarketSessionTransactionsView.as_view(), name="market-transactions"),
    re_path('session-balance/?$', MarketSessionBalanceView.as_view(), name="market-session-balance"),
    re_path('session-fee/?$', MarketSessionFeeView.as_view(), name="market-session-fee"),
    re_path('balance/?$', MarketBalanceView.as_view(), name="market-balance"),
    re_path('transfer-out/?$', BalanceTransferOutView.as_view(), name="transfer-out-request"),
]
