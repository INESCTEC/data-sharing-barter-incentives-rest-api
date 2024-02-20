from drf_yasg.utils import swagger_auto_schema
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, IsAdminUser

from api.utils.permissions import method_permission_classes
from api.renderers.CustomRenderer import CustomRenderer

from ..schemas.responses import *
from .. import exceptions as market_exceptions
from ..models.market_wallet import MarketWalletAddress
from ..serializers.market_wallet import MarketWalletAddressSerializer


class MarketWalletAddressView(APIView):
    renderer_classes = (CustomRenderer,)
    permission_classes = (IsAuthenticated,)
    serializer_class = MarketWalletAddressSerializer

    @staticmethod
    def queryset():
        try:
            query = MarketWalletAddress.objects.get()
            return query
        except MarketWalletAddress.DoesNotExist:
            raise market_exceptions.NoMarketAddress()

    @swagger_auto_schema(
        operation_id="get_market_wallet_address",
        operation_description="Method for agents to get current "
                              "market wallet address (to use as "
                              "reference for bid payments)",
        responses={
            200: MarketWalletAddressResponse["GET"],
            400: 'Bad request',
            401: NotAuthenticatedResponse,
            403: ForbiddenAccessResponse,
            500: "Internal Server Error",
        })
    def get(self, request):
        address = self.queryset()
        serializer = self.serializer_class(address)
        return Response(data=serializer.data)

    @swagger_auto_schema(
        operation_id="post_market_wallet_address",
        operation_description="[AdminOnly] Method for market engine to "
                              "register a new wallet address",
        request_body=MarketWalletAddressSerializer,
        responses={
            400: 'Bad request',
            401: NotAuthenticatedResponse,
            403: ForbiddenAccessResponse,
            500: "Internal Server Error",
        })
    @method_permission_classes((IsAdminUser,))
    def post(self, request):
        serializer = self.serializer_class(
            data=request.data,
            context={'request': request}
        )
        serializer.is_valid(raise_exception=True)
        response = serializer.save()
        return Response(data=response, status=status.HTTP_200_OK)

    @swagger_auto_schema(
        operation_id="put_market_wallet_address",
        operation_description="[AdminOnly] Method for market engine to "
                              "edit current wallet address",
        request_body=MarketWalletAddressSerializer,
        responses={
            400: 'Bad request',
            401: NotAuthenticatedResponse,
            403: ForbiddenAccessResponse,
            500: "Internal Server Error",
        })
    @method_permission_classes((IsAdminUser,))
    def put(self, request):
        serializer = self.serializer_class(
            data=request.data,
            context={'request': request}
        )
        serializer.is_valid(raise_exception=True)
        query = self.queryset()
        response = serializer.update(query, serializer.validated_data)
        return Response(data=response, status=status.HTTP_200_OK)
