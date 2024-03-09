from django.db import models
from users.models import UserResources


class RawData(models.Model):

    class RawDataUnits(models.TextChoices):
        WATT = 'w', "Watt"
        KILO_WATT = 'kw', "Kilowatt"
        MEGA_WATT = 'mw', "Megawatt"

    class RawDataTimeInterval(models.IntegerChoices):
        T5 = 5
        T15 = 15
        T30 = 30
        T60 = 60

    # Todo: we may include other aggregation types in the future
    #  but it will require extra processing.
    class RawDataAggType(models.TextChoices):
        AVG = "avg"

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
    # Resource type:
    resource_type = models.CharField(
        max_length=12,
        choices=UserResources.ResourceType.choices,
        null=False,
        blank=False
    )
    # Time-series Timestamp:
    datetime = models.DateTimeField(
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
        choices=RawDataUnits.choices,
        null=False,
        blank=False)
    # Time-series time resolution:
    time_interval = models.IntegerField(
        choices=RawDataTimeInterval.choices,
        null=False,
        blank=False)
    # Time-series aggregation type:
    aggregation_type = models.CharField(
        max_length=3,
        choices=RawDataAggType.choices,
        null=False,
        blank=False)
    # Insert date:
    registered_at = models.DateTimeField(blank=False)

    class Meta:
        db_table = "raw_data"
        unique_together = ("user", "resource", "datetime")
