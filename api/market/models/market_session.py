from django.db import models


class MarketSession(models.Model):

    class MarketStatus(models.TextChoices):
        STAGED = 'staged'      # Session prepared to be open (no bids)
        OPEN = 'open'          # Session open (accepts bids)
        CLOSED = 'closed'      # Session closed (no bids)
        RUNNING = 'running'    # Session being executed (no bids)
        FINISHED = 'finished'  # Session finished (no bids)

    id = models.AutoField(
        primary_key=True
    )
    session_number = models.IntegerField(
        null=False,
        blank=False
    )
    session_date = models.DateField(
        auto_now_add=True,
        blank=False,
        null=False,
    )
    # Datetime at which session was staged
    staged_ts = models.DateTimeField(
        auto_now_add=True,
        blank=True,
        null=True,
    )
    # Datetime at which session was opened (bid placement time)
    open_ts = models.DateTimeField(
        blank=True,
        null=True,
    )
    # Datetime at which session was closed (gate closure time)
    close_ts = models.DateTimeField(
        blank=True,
        null=True
    )
    # Datetime at which session launched (market run start)
    launch_ts = models.DateTimeField(
        blank=True,
        null=True
    )
    # Datetime at which session finished (market run ended)
    finish_ts = models.DateTimeField(
        blank=True,
        null=True
    )
    # Session status (updated during market processes)
    status = models.CharField(
        max_length=10,
        choices=MarketStatus.choices,
        default=MarketStatus.STAGED,
        null=False,
    )
    # Market price (IOTA)
    market_price = models.FloatField(
        null=False,
        blank=False,
    )
    # Minimum bid price (IOTA)
    b_min = models.IntegerField(
        null=False,
        blank=False,
    )
    # Maximum bid price (IOTA)
    b_max = models.IntegerField(
        null=False,
        blank=False,
    )
    # Number of price price intervals to be considered
    n_price_steps = models.IntegerField(
        null=False,
        blank=False,
    )
    # Market price delta
    delta = models.FloatField(
        null=False,
        blank=False,
    )

    class Meta:
        unique_together = ("session_number", "session_date")
        db_table = "market_session"

    def __str__(self):
        return f'#{self.pk}: {self.status}'


class MarketSessionPriceWeight(models.Model):

    market_session = models.ForeignKey(
        to=MarketSession,
        on_delete=models.CASCADE,
    )
    weights_p = models.FloatField(
        null=False,
        blank=False
    )

    class Meta:
        db_table = "market_session_weights_p"


class MarketSessionTransactions(models.Model):
    class TransactionType(models.TextChoices):
        PAYMENT = 'payment'
        REVENUE = 'revenue'
        TRANSFER_IN = 'transfer_in'
        TRANSFER_OUT = 'transfer_out'

    # Transaction ID (table PK id)
    tid = models.AutoField(primary_key=True)
    # Market session identifier:
    market_session = models.ForeignKey(
        to=MarketSession,
        on_delete=models.CASCADE,
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
    # Amount to transact:
    amount = models.FloatField(
        default=0.0,
        null=False,
        blank=False,
    )
    # Type of transaction ('transfer_in', 'payment', 'revenue', 'transfer_out')
    transaction_type = models.TextField(
        choices=TransactionType.choices,
        null=False
    )
    # Register date:
    registered_at = models.DateTimeField(
        auto_now_add=True,
        blank=True,
        null=False
    )

    class Meta:
        # each user will have once transaction of each type for each session
        unique_together = ("market_session", "user", "resource", "transaction_type")
        db_table = "market_session_transactions"


class MarketSessionFee(models.Model):
    # Market session identifier:
    market_session = models.OneToOneField(
        to=MarketSession,
        on_delete=models.CASCADE,
        primary_key=True,
    )
    # Market session fee
    amount = models.FloatField(
        default=0.0,
        null=False
    )
    # Register date:
    registered_at = models.DateTimeField(
        auto_now_add=True,
        blank=True,
        null=False
    )

    class Meta:
        # there is only 1 fee per session
        db_table = "market_session_fee"
