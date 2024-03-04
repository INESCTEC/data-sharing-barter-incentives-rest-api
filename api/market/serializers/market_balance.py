from django.db.utils import IntegrityError
from rest_framework import serializers

from .. import exceptions as market_exceptions
from ..models.market_session import MarketSessionTransactions
from ..models.market_balance import (
    MarketBalance,
    MarketSessionBalance,
    BalanceTransferOut
)


class MarketBalanceSerializer(serializers.ModelSerializer):
    class Meta:
        model = MarketBalance
        fields = '__all__'


class BalanceTransferOutSerializer(serializers.ModelSerializer):
    class Meta:
        model = BalanceTransferOut
        fields = "__all__"

    def create(self, validated_data):
        session = self.Meta.model.objects.create(**validated_data)
        session.save()
        return {
            "user_id": session.user_id,
            "amount": session.amount,
            "user_wallet_address": session.user_wallet_address,
            "tangle_msg_id": session.tangle_msg_id,
            "withdraw_transfer_id": session.withdraw_transfer_id
        }

    def validate(self, attrs):
        """
        Check if market session is open
        :param attrs:
        :return:
        """
        return attrs

    def update(self, instance, validated_data):
        user_id = instance.user_id
        transfer_amount = instance.amount

        # Check if user already has a market balance entry:
        balance_data = MarketBalance.objects.get(user=user_id)
        # Update current balance:
        current_balance = balance_data.balance
        new_balance = current_balance - transfer_amount
        # Update withdraw field:
        current_withdraw = balance_data.total_withdraw
        new_total_withdraw = current_withdraw + transfer_amount
        # Final balance cant be lower than zero.
        if new_balance < 0:
            raise market_exceptions.BalanceLowerThanZero(
                init_balance=current_balance,
                withdraw=transfer_amount,
                new_balance=new_balance
            )
        else:
            # Update column values:
            balance_data.balance = new_balance
            balance_data.total_withdraw = new_total_withdraw
            # Save balance update:
            balance_data.save()
            return super().update(instance, validated_data)


class MarketSessionBalanceRetrieveSerializer(serializers.ModelSerializer):
    class Meta:
        model = MarketSessionBalance
        fields = ['market_session', 'user', 'resource', 'session_deposit',
                  'session_balance', 'session_payment', 'session_revenue',
                  'registered_at']


class MarketSessionBalanceCreateSerializer(serializers.Serializer):
    user = serializers.UUIDField(required=True)
    market_session = serializers.IntegerField(required=True)
    resource = serializers.UUIDField(required=True)
    transaction_type = serializers.ChoiceField(
        required=True,
        choices=MarketSessionTransactions.TransactionType
    )
    amount = serializers.FloatField(required=True)

    def update(self, instance, validated_data):
        pass

    def validate(self, attrs):
        """
        Check if market session is open
        :param attrs:
        :return:
        """
        transaction_type = attrs["transaction_type"]
        amount = attrs["amount"]

        # -- Validate amount signal (according to transaction_type):
        # 'transfer_in' / 'revenue' -> positive signal  (money in)
        # 'transfer_out' or 'payment' -> negative signal (money out)
        negative_tt = [MarketSessionTransactions.TransactionType.PAYMENT,
                       MarketSessionTransactions.TransactionType.TRANSFER_OUT]
        positive_tt = [MarketSessionTransactions.TransactionType.REVENUE,
                       MarketSessionTransactions.TransactionType.TRANSFER_IN]
        if (transaction_type in negative_tt) and (amount > 0):
            raise market_exceptions.TransactionBadOperatorSignal(
                transaction_type=transaction_type,
                amount=amount
            )
        elif (transaction_type in positive_tt) and (amount < 0):
            raise market_exceptions.TransactionBadOperatorSignal(
                transaction_type=transaction_type,
                amount=amount)

        return attrs

    def create(self, validated_data):
        user_id = validated_data["user"]
        market_session_id = validated_data['market_session']
        resource_id = validated_data["resource"]
        amount = validated_data['amount']
        transaction_type = validated_data['transaction_type']

        try:
            # Check if user already has a session balance entry:
            session_balance_data = MarketSessionBalance.objects.get(
                user_id=user_id,
                resource_id=resource_id,
                market_session_id=market_session_id
            )
        except MarketSessionBalance.DoesNotExist:
            # If not, create new entry:
            session_balance_data = MarketSessionBalance.objects.create(
                user_id=user_id,
                resource_id=resource_id,
                market_session_id=market_session_id
            )
            session_balance_data.save()

        try:
            # Check if user already has a market balance entry:
            balance_data = MarketBalance.objects.get(user_id=user_id)
        except MarketBalance.DoesNotExist:
            # If not, create new entry:
            balance_data = MarketBalance.objects.create(user_id=user_id)
            balance_data.save()

        # -- Update current session balance:
        session_balance_data.session_balance += amount

        # -- Update user's market balances:
        # Balance = topups - payment + revenue - withdrawals:
        balance_data.balance += amount

        if transaction_type == MarketSessionTransactions.TransactionType.TRANSFER_IN:
            session_balance_data.session_deposit += amount
            balance_data.total_deposit += amount

        # If its revenue, update total revenues:
        elif transaction_type == MarketSessionTransactions.TransactionType.REVENUE:
            balance_data.total_revenue += amount
            session_balance_data.session_revenue += amount

        # If its payment, update total revenues:
        elif transaction_type == MarketSessionTransactions.TransactionType.PAYMENT:
            balance_data.total_payment += amount
            session_balance_data.session_payment += amount

        if (balance_data.balance < 0) or (session_balance_data.session_balance < 0):
            raise ValueError("The user final balance cant be inferior to 0.")

        # -- Create a transaction of type - transfer:
        try:
            transaction_data = MarketSessionTransactions.objects.create(
                amount=amount,
                market_session_id=market_session_id,
                resource_id=resource_id,
                user_id=user_id,
                transaction_type=transaction_type,
            )
        except IntegrityError:
            raise market_exceptions.DuplicatedTransactionFound(
                user_id=user_id,
                resource_id=resource_id,
                market_session_id=market_session_id,
                transaction_type=transaction_type
            )

        # Save to DB:
        balance_data.save()
        session_balance_data.save()
        transaction_data.save()

        return f"Updated session balance for the user ID ({user_id}). "
