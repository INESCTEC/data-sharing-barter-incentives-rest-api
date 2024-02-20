import datetime as dt
import iota_sdk
from rest_framework import serializers
from ..models.user_wallet import UserWalletAddress


class UserWalletAddressSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserWalletAddress
        fields = '__all__'
        # note: gotta disables unique constraint validation for 'user' to be
        # able to perform updates. See bellow 'validators': []
        # todo: find a workaround for this
        extra_kwargs = {
            'wallet_address': {'required': True},
            'user': {'validators': [], 'required': True},
        }

    def validate(self, attrs):
        wallet_address = attrs["wallet_address"]
        if not iota_sdk.utils.Utils().is_address_valid(wallet_address):
            raise serializers.ValidationError(
                {'wallet_address': ["Invalid wallet address."]}
            )
        return attrs

    def update(self, instance, validated_data):
        utc_now_ = dt.datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%S.%fZ")
        validated_data["registered_at"] = utc_now_
        return super().update(instance, validated_data)
