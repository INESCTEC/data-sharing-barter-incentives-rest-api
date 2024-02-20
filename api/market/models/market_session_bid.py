from django.db import models

from .market_session import MarketSession


class MarketSessionBid(models.Model):

    class GainFunc(models.TextChoices):
        MSE = 'mse'
        RMSE = 'rmse'
        MAE = 'mae'

    # Pairs w/ 'market_bid_id' key in 'market_session_bid_payment' tbl:
    id = models.AutoField(
        primary_key=True
    )
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
        to=MarketSession,
        on_delete=models.CASCADE,
    )
    # No. tokens transferred from client app to wallet:
    max_payment = models.IntegerField(
        null=False,
        blank=False
    )
    # Agent bid price per gain in market:
    bid_price = models.IntegerField(
        null=False,
        blank=False
    )
    # Bid gain function:
    gain_func = models.CharField(
        max_length=100,
        choices=GainFunc.choices,
        default=GainFunc.RMSE)

    # Is bid confirmed in Tangle (solid and correct amount):
    confirmed = models.BooleanField(
        null=True,
        blank=False,
        default=False
    )
    # Register date:
    registered_at = models.DateTimeField(
        auto_now_add=True
    )
    # Agent has forecasts for this session:
    has_forecasts = models.BooleanField(
        null=False,
        default=False
    )

    class Meta:
        # the bidder should only have one bid for one specific session
        unique_together = ("market_session", "user", "resource")
        db_table = "market_session_bid"


class MarketSessionBidPayment(models.Model):
    # Foreign Key - Pairs with 'market_bid_id' key in 'market_session_bid' tbl:
    market_bid = models.OneToOneField(MarketSessionBid,
                                      on_delete=models.CASCADE,
                                      primary_key=True,
                                      related_name='payment')
    # IOTA tangle message ID (searchable in IOTA explorer):
    tangle_msg_id = models.TextField(unique=True, null=False)
    # If transfer is solid in Tangle:
    is_solid = models.BooleanField(null=False, default=False)
    # Register date:
    registered_at = models.DateTimeField(auto_now_add=True, blank=True)

    class Meta:
        db_table = "market_session_bid_payment"
