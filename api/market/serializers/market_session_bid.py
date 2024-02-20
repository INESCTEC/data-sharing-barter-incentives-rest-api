from django.conf import settings
from django.db.models import Q
from django.db.utils import IntegrityError
from rest_framework import serializers

from users.models import (
    UserResources,
    UserWalletAddress,
)
from .market_balance import MarketSessionBalanceCreateSerializer
from .. import exceptions as market_exceptions
from ..models.market_session import (
    MarketSession,
    MarketSessionTransactions,
)
from ..models.market_session_bid import (
    MarketSessionBid,
    MarketSessionBidPayment,
)
from ..models.market_wallet import MarketWalletAddress


class MarketSessionBidRetrieveSerializer(serializers.ModelSerializer):
    tangle_msg_id = serializers.SerializerMethodField()

    class Meta:
        model = MarketSessionBid
        fields = '__all__'

    @staticmethod
    def get_tangle_msg_id(obj):
        # Attempt to access the related payment object and its tangle_msg_id attribute
        # If the related payment does not exist, return None or a default value
        return obj.payment.tangle_msg_id if hasattr(obj, 'payment') and obj.payment else None


class MarketSessionBidCreateSerializer(serializers.Serializer):
    market_session = serializers.IntegerField(
        required=True,
        allow_null=False,
    )
    resource = serializers.IntegerField(
        required=True,
        allow_null=False,
    )
    max_payment = serializers.IntegerField(
        required=True,
        allow_null=False,
        min_value=settings.MINIMUM_PAYMENT_AMOUNT
    )
    bid_price = serializers.IntegerField(
        required=True,
        allow_null=False,
    )
    gain_func = serializers.ChoiceField(
        choices=MarketSessionBid.GainFunc,
        required=True,
        allow_null=False,
        allow_blank=False
    )

    def update(self, instance, validated_data):
        pass

    def validate(self, attrs):
        """
        Check if market session is open
        :param attrs:
        :return:
        """
        request = self.context.get('request')
        user = request.user
        resource_id = attrs["resource"]
        market_session_id = attrs["market_session"]

        try:
            # Check if user has registered wallet address:
            UserWalletAddress.objects.get(user_id=user.id)
        except UserWalletAddress.DoesNotExist:
            raise market_exceptions.UserWalletAddressNotFound(user=user)

        try:
            # Check if this resource belongs to user:
            resource_data = UserResources.objects.get(
                id=resource_id,
                user_id=user.id
            )
        except UserResources.DoesNotExist:
            raise market_exceptions.UserResourceNotRegistered(
                user=user,
                resource_id=resource_id,
            )

        if resource_data.type != UserResources.ResourceType.MEASUREMENT:
            # It is only possible to place bids for measurements resources
            raise market_exceptions.InvalidResourceBid()

        if not resource_data.to_forecast:
            raise market_exceptions.NoForecastResourceBid()

        try:
            # Get market session data:
            market_session = MarketSession.objects.get(id=market_session_id)
            attrs["session_number"] = market_session.session_number
            attrs["session_date"] = market_session.session_date
        except MarketSession.DoesNotExist:
            raise market_exceptions.NoMarketSession(
                market_session_id=market_session_id
            )

        # Session status must be OPEN to accept bids:
        if market_session.status != MarketSession.MarketStatus.OPEN:
            raise market_exceptions.SessionNotOpenForBids(
                market_session_id=market_session_id
            )

        # Check if a bid for this user_id/market_session_id/resource_id
        # already exists:
        if MarketSessionBid.objects.filter(
                user_id=user.id,
                market_session_id=market_session_id,
                resource_id=resource_id,
        ):
            raise market_exceptions.BidAlreadyExists(
                market_session_id=market_session_id,
                resource_id=resource_id
            )

        return attrs

    def create(self, validated_data):
        # user info:
        user = self.context.get('request').user
        # session info:
        user_id = user.id
        market_session_id = validated_data["market_session"]
        resource_id = validated_data["resource"]
        bid_price = validated_data["bid_price"]
        max_payment = validated_data["max_payment"]
        gain_func = validated_data["gain_func"]

        # Register bid:
        bid = MarketSessionBid.objects.create(
            user_id=user_id,
            market_session_id=market_session_id,
            resource_id=resource_id,
            bid_price=bid_price,
            max_payment=max_payment,
            gain_func=gain_func,
        )
        # Get Bid Identifier:
        market_bid_id = bid.id

        # Get Market Wallet Address:
        market_wallet = MarketWalletAddress.objects.get()

        return {
            "id": market_bid_id,
            "user": user_id,
            "market_session": market_session_id,
            "resource": resource_id,
            "bid_price": bid_price,
            "gain_func": gain_func,
            "max_payment": max_payment,
            "market_wallet_address": market_wallet.wallet_address
        }


class MarketSessionBidUpdateSerializer(serializers.Serializer):
    tangle_msg_id = serializers.CharField(
        required=True,
        allow_blank=False,
        allow_null=False
    )

    def validate(self, attrs):
        """
        Check if market session is open
        :param attrs:
        :return:
        """
        request = self.context.get('request')
        bid_id = self.context.get('bid_id')
        tangle_msg_id = attrs.get('tangle_msg_id')
        user = request.user

        # Check if user has a registered wallet address with a single query
        if not UserWalletAddress.objects.filter(user=user).exists():
            raise market_exceptions.UserWalletAddressNotFound(user=user)

        # Attempt to fetch the bid and its associated market session with a single query
        try:
            bid = MarketSessionBid.objects.select_related('payment').get(id=bid_id, user=user)

            # Ensure the market session is open
            if bid.market_session.status != MarketSession.MarketStatus.OPEN:
                raise market_exceptions.SessionNotOpenForBids(market_session_id=bid.market_session.id)

        except MarketSessionBid.DoesNotExist:
            raise market_exceptions.UserBidNotRegistered(user=user, bid_id=bid_id)

        # Check for existing tangle_msg_id or bid update in a single query
        if MarketSessionBidPayment.objects.filter(Q(market_bid_id=bid_id) |
                                                  Q(tangle_msg_id=tangle_msg_id)).exists():
            raise market_exceptions.BidAlreadyWithTangleIdException(bid_id=bid_id)

        attrs["bid_id"] = bid_id
        return attrs

    def update(self, instance, validated_data):
        tangle_msg_id = validated_data["tangle_msg_id"]
        bid_id = validated_data["bid_id"]
        try:
            # Register bid payment:
            bid_payment = MarketSessionBidPayment.objects.create(
                tangle_msg_id=tangle_msg_id,
                market_bid_id=bid_id,
                is_solid=False,
            )
        except IntegrityError:
            # each tangle msg id can only be associated with 1 bid:
            raise market_exceptions.DuplicatedTangleMessageId(
                tangle_msg_id=tangle_msg_id
            )

        instance.has_tangle_msg_id = True
        instance.save()

        return {
            "bid_id": int(bid_payment.market_bid_id),
            "tangle_msg_id": bid_payment.tangle_msg_id,
        }


class MarketValidateSessionBidSerializer(serializers.Serializer):
    tangle_msg_id = serializers.CharField()

    def update(self, instance, validated_data):
        pass

    def validate(self, attrs):
        try:
            # Check if tangle message id is already assigned to a bid:
            transaction_data = MarketSessionBidPayment.objects.get(
                tangle_msg_id=attrs['tangle_msg_id']
            )
        except MarketSessionBidPayment.DoesNotExist:
            raise market_exceptions.BidPaymentNotFound(
                tangle_msg_id=attrs['tangle_msg_id']
            )

        try:
            # -- Query bid info associated with request tangle message id:
            bid_data = MarketSessionBid.objects.get(
                id=transaction_data.market_bid_id
            )
            # -- Check if bid was already confirmed (in IOTA Tangle):
            if bid_data.confirmed:
                raise market_exceptions.TransactionAlreadyValid(
                    tangle_msg_id=attrs['tangle_msg_id']
                )
        except MarketSessionBid.DoesNotExist:
            raise market_exceptions.NoBidsDataFound(
                tangle_msg_id=attrs['tangle_msg_id']
            )

        # Save objects to later update:
        attrs['transaction_data'] = transaction_data
        attrs['bid_data'] = bid_data
        return attrs

    def create(self, validated_data):
        # -- Get params:
        wallet_address = MarketWalletAddress.objects.first().wallet_address
        tangle_msg_id = validated_data['tangle_msg_id']
        transaction_data = validated_data['transaction_data']
        bid_data = validated_data['bid_data']
        transaction_type = MarketSessionTransactions.TransactionType.TRANSFER_IN

        # Once transaction is valid, one should update the session balance:
        bid_data.confirmed = True
        transaction_data.is_solid = True

        # Update market session and market balance:
        balance_serializer = MarketSessionBalanceCreateSerializer(data={
            "amount": bid_data.max_payment,
            "market_session": bid_data.market_session_id,
            "resource": bid_data.resource_id,
            "user": bid_data.user_id,
            "transaction_type": transaction_type
        })
        balance_serializer.is_valid(raise_exception=True)

        # Save changes:
        balance_serializer.save()
        transaction_data.save()
        bid_data.save()

        return {
            "market_bid": bid_data.id,
            "market_session": bid_data.market_session_id,
            "tangle_msg_id": tangle_msg_id,
            "user_wallet_address": wallet_address,
            "confirmed": bid_data.confirmed,
        }
