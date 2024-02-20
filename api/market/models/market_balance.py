from django.db import models

from ..models.market_session import MarketSession


class MarketBalance(models.Model):
    # Foreign (OnetoOne) keys (PK):
    user = models.OneToOneField("users.User",
                                on_delete=models.CASCADE,
                                primary_key=True)
    # User market balance:
    balance = models.FloatField(default=0.0, null=False)
    # User sum of deposit to the market:
    total_deposit = models.FloatField(default=0.0, null=False)
    # User sum of withdraw from the market:
    total_withdraw = models.FloatField(default=0.0, null=False)
    # User sum of payments in market:
    total_payment = models.FloatField(default=0.0, null=False)
    # User sum of revenues in market:
    total_revenue = models.FloatField(default=0.0, null=False)
    # Field last update date:
    updated_at = models.DateTimeField(auto_now_add=True, blank=True,
                                      null=False)

    def __str__(self):
        return f'{self.user}'

    class Meta:
        db_table = "market_balance"


class MarketSessionBalance(models.Model):
    # Session balance ID:
    bal_id = models.AutoField(primary_key=True)
    # User ID:
    user = models.ForeignKey(
        to="users.User",
        on_delete=models.CASCADE,
    )
    # Market session identifier:
    market_session = models.ForeignKey(
        to=MarketSession,
        on_delete=models.CASCADE,
    )
    # Resource ID (each user will have 1 bid per resource):
    resource = models.ForeignKey(
        to="users.UserResources",
        on_delete=models.CASCADE,
    )
    # Market session balance (transfer-payment+revenue-withdraw):
    session_balance = models.FloatField(
        default=0.0,
        null=False
    )
    # How much user deposit in market session:
    session_deposit = models.FloatField(
        default=0.0,
        null=False
    )
    # How much user payed in market session:
    session_payment = models.FloatField(
        default=0.0,
        null=False
    )
    # How much user received in market session:
    session_revenue = models.FloatField(
        default=0.0,
        null=False
    )
    # Register date:
    registered_at = models.DateTimeField(
        auto_now_add=True,
        blank=True,
        null=False
    )

    def __str__(self):
        return f'#{self.pk}: ' \
               f'{self.user}, ' \
               f'{self.resource}, ' \
               f'{self.market_session}'

    class Meta:
        # each user should only have 1 balance for each market session
        unique_together = ("market_session", "user", "resource")
        db_table = "market_session_balance"


class BalanceTransferOut(models.Model):
    # Transaction ID (table PK id)
    withdraw_transfer_id = models.AutoField(
        primary_key=True
    )
    # Foreign (OnetoOne) keys:
    user = models.ForeignKey(
        to="users.User",
        on_delete=models.CASCADE,
    )
    # Amount to transfer:
    amount = models.IntegerField(
        default=0,
        null=False
    )
    # Tokens transferred to address:
    user_wallet_address = models.TextField(
        unique=False,
        null=False
    )
    # IOTA tangle message ID (searchable in IOTA explorer):
    tangle_msg_id = models.TextField(
        unique=False,
        null=False
    )
    # Is bid confirmed in Tangle (solid and correct amount):
    is_solid = models.BooleanField(
        null=False,
        default=False
    )
    # Register date:
    registered_at = models.DateTimeField(
        auto_now_add=True,
        blank=True,
        null=False
    )

    def __str__(self):
        return f'#{self.pk}: {self.user}'

    class Meta:
        # Each transfer will have its own Tangle message ID
        db_table = "balance_transfer_out"
