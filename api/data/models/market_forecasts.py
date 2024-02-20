from django.db import models


class MarketForecasts(models.Model):

    class ForecastsUnits(models.TextChoices):
        WATT = 'w'
        KILO_WATT = 'kw'
        MEGA_WATT = 'mw'

    # User ID:
    user = models.ForeignKey(
        to="users.User",
        on_delete=models.CASCADE,
    )
    # Resource ID (each user will have 1 bid per resource):
    resource = models.ForeignKey(
        to="users.UserResources",
        on_delete=models.CASCADE,
    )
    # Market session ID:
    market_session = models.ForeignKey(
        to="market.MarketSession",
        on_delete=models.CASCADE,
    )
    # Forecast Horizon Timestamps:
    datetime = models.DateTimeField(
        blank=False,
        null=False
    )
    # Forecast Request Timestamp:
    request = models.DateTimeField(
        blank=False,
        null=False
    )
    # Time-series Value:
    value = models.FloatField(
        blank=False,
        null=False
    )
    # Time-series Unit:
    units = models.CharField(
        max_length=2,
        choices=ForecastsUnits.choices,
        null=False,
        blank=False)

    # Insert date:
    registered_at = models.DateTimeField(blank=False)

    class Meta:
        db_table = "market_forecasts"
        unique_together = ("user", "resource", "market_session", "datetime")
