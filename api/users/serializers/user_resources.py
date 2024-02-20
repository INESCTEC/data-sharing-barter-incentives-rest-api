import datetime as dt

from rest_framework import exceptions, serializers

from ..util.validators import ResourceNameValidator
from ..models.user_resources import UserResources


class UserResourcesSerializer(serializers.ModelSerializer):

    class Meta:
        model = UserResources
        fields = '__all__'
        extra_kwargs = {
            'name': {'required': True, 'validators': [ResourceNameValidator]},
            'type': {'required': True},
            'to_forecast': {'required': True},
        }

    def validate(self, attrs):
        resource_type = attrs["type"]
        to_forecast = attrs["to_forecast"]
        if to_forecast and resource_type == "forecasts":
            msg = "You can only request forecasts for resources with " \
                  "'measurements' resource type."
            raise exceptions.ValidationError(
                {'resource_type': [msg], 'to_forecast': [msg]}
            )
        return attrs

    def update(self, instance, validated_data):
        utc_now_ = dt.datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%S.%fZ")
        validated_data["registered_at"] = utc_now_
        return super().update(instance, validated_data)
