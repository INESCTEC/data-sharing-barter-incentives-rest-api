import datetime as dt
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
        request = self.context.get('request')
        payment_processor = request.payment_processor
        wallet_address = attrs["wallet_address"]
        if not payment_processor.validate_account_address(address=wallet_address):
            raise serializers.ValidationError(
                {'wallet_address': [f'Invalid wallet address for the selected '
                                    f'payment method: '
                                    f'{payment_processor.PAYMENT_METHOD.name}']}
            )
        return attrs

    def update(self, instance, validated_data):
        utc_now_ = dt.datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%S.%fZ")
        validated_data["registered_at"] = utc_now_
        return super().update(instance, validated_data)
