import datetime as dt

import iota_sdk
from rest_framework import serializers

from .. import exceptions
from ..models.market_wallet import MarketWalletAddress


class MarketWalletAddressSerializer(serializers.ModelSerializer):
    class Meta:
        model = MarketWalletAddress
        fields = ['wallet_address', 'registered_at']
        extra_kwargs = {
            'wallet_address': {'required': True},
        }

    def validate(self, attrs):
        request = self.context.get('request')
        if request.method == 'POST':
            # Check if there is any address already in DB:
            current_addresses = MarketWalletAddress.objects.all()
            if len(current_addresses) > 0:
                raise exceptions.MarketAddressAlreadyExists()

        wallet_address = attrs["wallet_address"]
        if not iota_sdk.utils.Utils().is_address_valid(wallet_address):
            raise serializers.ValidationError(
                {'wallet_address': ["Invalid wallet address."]}
            )

        return attrs

    def create(self, validated_data):
        instance = super().create(validated_data)
        return {
            "wallet_address": instance.wallet_address,
            "registered_at": instance.registered_at
        }

    def update(self, instance, validated_data):
        utc_now_ = dt.datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%S.%fZ")
        validated_data["registered_at"] = utc_now_
        instance = super().update(instance, validated_data)
        return {
            "wallet_address": instance.wallet_address,
            "registered_at": instance.registered_at
        }
