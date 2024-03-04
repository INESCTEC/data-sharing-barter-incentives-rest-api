from drf_yasg.utils import swagger_auto_schema
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.db.utils import IntegrityError

from api.renderers.CustomRenderer import CustomRenderer

from ..schemas.responses import *
from .. import exceptions as user_exceptions
from ..models.user_wallet import UserWalletAddress
from ..serializers.user_wallet import UserWalletAddressSerializer


class UserWalletAddressView(APIView):
    renderer_classes = (CustomRenderer,)
    permission_classes = (IsAuthenticated,)
    serializer_class = UserWalletAddressSerializer

    @staticmethod
    def queryset(request):
        user = request.user
        if user.is_superuser:
            user_id = request.query_params.get('user', None)
            if user_id:
                query = UserWalletAddress.objects.filter(user_id=user_id)
            else:
                query = UserWalletAddress.objects.all()
        else:
            query = UserWalletAddress.objects.filter(user_id=user.id)
        return query

    @swagger_auto_schema(
        operation_id="get_user_wallet_address",
        operation_description="Method for agents to list their IOTA wallet address",
        responses={
            200: UserWalletAddressResponse["GET"],
            400: 'Bad request',
            401: NotAuthenticatedResponse,
            403: ForbiddenAccessResponse,
            500: "Internal Server Error",
        })
    def get(self, request):
        address = self.queryset(request)
        serializer = self.serializer_class(address, many=True)
        return Response(data=serializer.data)

    @swagger_auto_schema(
        operation_id="post_user_wallet_address",
        operation_description="Method for agents to register their IOTA wallet address",
        request_body=UserWalletAddressSerializer,
        responses={
            400: 'Bad request',
            401: NotAuthenticatedResponse,
            403: ForbiddenAccessResponse,
            500: "Internal Server Error",
        })
    def post(self, request):
        try:
            request.data["user"] = request.user.id
            serializer = self.serializer_class(data=request.data)
            serializer.is_valid(raise_exception=True)
            response = serializer.save()
            return Response(data={
                "wallet_address": response.wallet_address,
                "registered_at": response.registered_at
            }, status=status.HTTP_200_OK)
        except IntegrityError:
            raise user_exceptions.UserAlreadyHasAddress()

    @swagger_auto_schema(
        operation_id="put_user_wallet_address",
        operation_description="Method for agents to update their IOTA wallet address",
        request_body=UserWalletAddressSerializer,
        responses={
            400: 'Bad request',
            401: NotAuthenticatedResponse,
            403: ForbiddenAccessResponse,
            500: "Internal Server Error",
        })
    def put(self, request):
        request.data["user"] = request.user.id
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        query = self.queryset(request)
        if query.exists():
            wallet_address = query.get()
            response = serializer.update(wallet_address, serializer.validated_data)
            return Response(data={
                "wallet_address": response.wallet_address,
                "registered_at": response.registered_at
            }, status=status.HTTP_200_OK)
        else:
            raise user_exceptions.WalletAddressNotFound()
