import uuid

from django.db import models
from .user import User


class UserResources(models.Model):
    class ResourceType(models.TextChoices):
        FORECAST = 'forecasts'
        MEASUREMENT = 'measurements'

    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False
    )
    user = models.ForeignKey(
        to=User,
        on_delete=models.CASCADE,
    )
    name = models.CharField(
        max_length=64,
        null=False,
    )
    type = models.CharField(
        max_length=12,
        choices=ResourceType.choices,
        null=False,
        blank=False
    )
    to_forecast = models.BooleanField(
        null=False,
        default=False
    )
    # Register date:
    registered_at = models.DateTimeField(auto_now_add=True, blank=True)

    def __str__(self):
        return f'#{self.pk}: {self.user}, {self.name}'

    class Meta:
        unique_together = ("user", "name", "type")
        db_table = 'user_resources'
