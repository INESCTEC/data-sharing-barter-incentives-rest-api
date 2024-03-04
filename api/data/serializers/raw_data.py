import pandas as pd
import datetime as dt

from django.db import connection
from rest_framework import serializers

from users.models import UserResources
from users.util.validators import ResourceNameValidator

from .. import exceptions as data_exceptions
from ..models.raw_data import RawData
from ..helpers.sql import to_sql_update


class RawDataRetrieveSerializer(serializers.ModelSerializer):
    class Meta:
        model = RawData
        fields = ["datetime",
                  "value",
                  "units",
                  "resource",
                  "resource_type",
                  "time_interval",
                  "aggregation_type",
                  "registered_at"]

    def to_representation(self, instance):
        rep = super(RawDataRetrieveSerializer, self)\
            .to_representation(instance)
        rep['resource_name'] = instance.resource.name
        return rep


class RawDataCreateSerializer(serializers.Serializer):
    class RawDataFieldSerializer(serializers.Serializer):
        datetime = serializers.DateTimeField(required=True,
                                             allow_null=False)
        value = serializers.FloatField(required=True,
                                       allow_null=False)

    timeseries = RawDataFieldSerializer(many=True,
                                        required=True,
                                        allow_null=False)
    user = serializers.UUIDField(
        required=True,
        allow_null=False
    )
    resource_name = serializers.CharField(
        required=True,
        max_length=64,
        allow_null=False,
        allow_blank=False,
        validators=[ResourceNameValidator]
    )
    time_interval = serializers.ChoiceField(
        required=True,
        allow_null=False,
        allow_blank=False,
        choices=RawData.RawDataTimeInterval
    )
    aggregation_type = serializers.ChoiceField(
        required=True,
        allow_null=False,
        allow_blank=False,
        choices=RawData.RawDataAggType
    )
    units = serializers.ChoiceField(
        required=True,
        allow_null=False,
        choices=RawData.RawDataUnits
    )

    def validate(self, attrs):
        user_id = attrs["user"]
        resource_name = attrs["resource_name"]
        try:
            # Check if this resource belongs to user:
            resource_data = UserResources.objects.get(
                name=resource_name,
                user_id=user_id
            )
        except UserResources.DoesNotExist:
            raise data_exceptions.RawResourceNotAssigned(
                resource_name=resource_name
            )
        attrs["resource_data"] = resource_data
        return attrs

    def create(self, validated_data):
        """
        Create and return a new `Snippet` instance, given the validated data.
        """
        # Get timeseries info:
        data = pd.DataFrame(validated_data["timeseries"])
        # todo: process data - adjust to time resolution here or on aux step
        # Get resource info:
        resource_data = validated_data["resource_data"]
        resource_id = resource_data.id
        # resource_name = resource_data.name
        resource_type = resource_data.type
        # Include new cols in timeseries:
        data["user_id"] = validated_data["user"]
        data["resource_id"] = resource_id
        # data["resource_name"] = resource_name
        data["resource_type"] = resource_type
        data["time_interval"] = validated_data["time_interval"]
        data["aggregation_type"] = validated_data["aggregation_type"]
        data["units"] = validated_data["units"]
        data["registered_at"] = dt.datetime.utcnow()
        msg = to_sql_update(
            conn=connection,
            df=data,
            table=RawData._meta.db_table,
            constraint_columns=[
                "user_id",
                "resource_id",
                "datetime"
            ],
        )
        return {"status": "ok", "message": msg}
