from django.db import models


class MarketWalletAddress(models.Model):
    # Market wallet address:
    wallet_address = models.TextField(
        default=None,
        null=False,
        unique=True
    )
    # Register date:
    registered_at = models.DateTimeField(auto_now_add=True,
                                         blank=True,
                                         null=False)

    class Meta:
        # each user should only have 1 balance for each market session
        db_table = "market_wallet_address"
