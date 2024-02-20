from django.urls import re_path

from .views.raw_data import RawDataView
from .views.market_forecasts import MarketForecastsView

app_name = "data"

urlpatterns = [
    re_path('raw-data/?$', RawDataView.as_view(), name="raw-data"),
    re_path('market-forecasts/?$', MarketForecastsView.as_view(), name="market-forecasts"),
]
