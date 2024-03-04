from rest_framework import serializers

from .. import exceptions as market_exceptions
from ..models.market_session import (
    MarketSession,
    MarketSessionFee,
    MarketSessionPriceWeight,
    MarketSessionTransactions,
)
from ..models.market_wallet import MarketWalletAddress


class MarketSessionPriceWeightRetrieveSerializer(serializers.ModelSerializer):
    class Meta:
        model = MarketSessionPriceWeight
        fields = "__all__"


class MarketSessionPriceWeightCreateSerializer(serializers.ModelSerializer):
    weights_p = serializers.ListSerializer(child=serializers.FloatField())

    class Meta:
        model = MarketSessionPriceWeight
        fields = "__all__"
        extra_kwargs = {
            "market_session": {
                "error_messages": {
                    "does_not_exist": "This market session does not exist yet."
                }
            }}

    def create(self, validated_data):
        try:
            weights_p_values = validated_data['weights_p']
            market_session = validated_data['market_session']
            for weights_p in weights_p_values:
                self.Meta.model(
                    weights_p=weights_p,
                    market_session_id=market_session.id
                ).save()
        except Exception as e:
            raise e
        return True


class MarketSessionSerializer(serializers.ModelSerializer):
    class Meta:
        model = MarketSession
        fields = "__all__"

    def validate(self, attrs):
        request = self.context.get('request')
        if request.method == 'POST':
            market_address = MarketWalletAddress.objects.all()
            if len(market_address) == 0:
                raise market_exceptions.NoMarketAddress()

            all_sessions = self.Meta.model.objects.all()
            for market_session in all_sessions:
                if market_session.status != MarketSession.MarketStatus.FINISHED:
                    raise market_exceptions.UnfinishedSessions()
        elif request.method == "PATCH":
            if request.data["status"] == "open":
                session_id = self.context.get('session_id')
                # Check if there are already sessions open
                # (there can only be 1 session open at each time)
                open_sessions = self.Meta.model.objects \
                    .filter(status="open") \
                    .exclude(id=session_id)
                if len(open_sessions) > 0:
                    raise market_exceptions.MoreThanOneSessionOpen(
                        session_id=session_id
                    )
        return attrs


class MarketSessionTransactionsSerializer(serializers.ModelSerializer):
    class Meta:
        model = MarketSessionTransactions
        fields = ['market_session',
                  'user',
                  "resource",
                  'amount',
                  'transaction_type',
                  'registered_at']

    def to_representation(self, instance):
        rep = super(MarketSessionTransactionsSerializer, self).to_representation(instance)
        rep['resource_name'] = instance.resource.name
        return rep


class MarketSessionFeeSerializer(serializers.ModelSerializer):
    class Meta:
        model = MarketSessionFee
        fields = ['market_session', 'amount']
        extra_kwargs = {
            'market_session': {
                'required': True,
                "error_messages": {
                    "does_not_exist": "This market session does not exist yet."
                }
            },
            'amount': {'required': True},
        }
