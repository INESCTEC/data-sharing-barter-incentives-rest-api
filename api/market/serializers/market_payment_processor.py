from rest_framework import serializers


class PaymentProcessorSerializer(serializers.Serializer):
    name = serializers.CharField()
    base_unit = serializers.CharField()
    transaction_unit = serializers.CharField()
