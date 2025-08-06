from drf_yasg.utils import swagger_auto_schema
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from ..schemas.responses import *
from ..serializers.market_payment_processor import PaymentProcessorSerializer


class MarketPaymentProcessorView(APIView):
    permission_classes = (IsAuthenticated,)

    @swagger_auto_schema(
        operation_id="get_market_payment_processor",
        operation_description="Method for agents to get current market payment "
                              "processor information.",
        responses={
            200: PaymentProcessorSerializer,
            400: 'Bad request',
            401: NotAuthenticatedResponse,
            403: ForbiddenAccessResponse,
            500: "Internal Server Error",
        })
    def get(self, request):
        payment_processor = request.payment_processor
        data = {
            "name": payment_processor.PAYMENT_METHOD.name,
            "base_unit": payment_processor.BASE_UNIT,
            "transaction_unit": payment_processor.TRANSACTION_UNIT,
        }
        serializer = PaymentProcessorSerializer(data=data)
        serializer.is_valid(raise_exception=True)
        return Response(data=serializer.data, status=status.HTTP_200_OK)
