import pandas as pd
import datetime as dt

from django.db import connection
from rest_framework import serializers

from users.models import UserResources
from users.util.validators import ResourceNameValidator

from .. import exceptions as data_exceptions
from ..models.market_forecasts import MarketForecasts
from ..helpers.sql import to_sql_update


class MarketForecastsRetrieveSerializer(serializers.ModelSerializer):
    class Meta:
        model = MarketForecasts
        fields = ["market_session",
                  "datetime",
                  "request",
                  "value",
                  "units",
                  "resource",
                  "registered_at"]

    def to_representation(self, instance):
        rep = super(MarketForecastsRetrieveSerializer, self)\
            .to_representation(instance)
        rep['resource_name'] = instance.resource.name
        return rep


class MarketForecastsCreateSerializer(serializers.Serializer):
    class MarketForecastsFieldSerializer(serializers.Serializer):
        datetime = serializers.DateTimeField(required=True,
                                             allow_null=False)
        request = serializers.DateTimeField(required=True,
                                            allow_null=False)
        value = serializers.FloatField(required=True,
                                       allow_null=False)

    timeseries = MarketForecastsFieldSerializer(many=True,
                                                required=True,
                                                allow_null=False)
    user = serializers.UUIDField(
        required=True,
        allow_null=False,
    )
    resource_name = serializers.CharField(
        required=True,
        max_length=64,
        allow_null=False,
        allow_blank=False,
        validators=[ResourceNameValidator]
    )
    market_session = serializers.IntegerField(required=True,
                                              allow_null=False)
    units = serializers.ChoiceField(
        required=True,
        allow_null=False,
        choices=MarketForecasts.ForecastsUnits
    )

    def validate(self, attrs):
        user_id = attrs["user"]
        resource_name = attrs["resource_name"]
        try:
            # Check if this resource belongs to user:
            resource_data = UserResources.objects.get(
                user_id=user_id,
                name=resource_name,
            )
        except UserResources.DoesNotExist:
            raise data_exceptions.ForecastResourceNotAssigned(
                resource_name=resource_name
            )
        attrs["resource_data"] = resource_data
        return attrs

    def create(self, validated_data):
        """
        Create and return a new `Snippet` instance, given the validated data.
        """
        data = pd.DataFrame(validated_data["timeseries"])
        # Get resource info:
        resource_data = validated_data["resource_data"]
        resource_id = resource_data.id
        # resource_name = resource_data.name
        resource_user_id = resource_data.user_id
        data["user_id"] = resource_user_id
        data["resource_id"] = resource_id
        # data["resource_name"] = resource_name
        data["market_session_id"] = validated_data["market_session"]
        data["units"] = validated_data["units"]
        data["registered_at"] = dt.datetime.utcnow()
        msg = to_sql_update(
            conn=connection,
            df=data,
            table=MarketForecasts._meta.db_table,
            constraint_columns=[
                "user_id",
                "resource_id",
                "market_session_id",
                "datetime"
            ],
        )
        return {"status": "ok", "message": msg}
