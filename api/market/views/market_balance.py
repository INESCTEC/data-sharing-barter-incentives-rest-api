import pandas as pd

from drf_yasg.utils import swagger_auto_schema
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, IsAdminUser

from api.renderers.CustomRenderer import CustomRenderer
from api.utils.permissions import method_permission_classes

from ..schemas.query import *
from ..schemas.responses import *
from ..util.validators import validate_query_params
from ..models.market_balance import (
    MarketBalance,
    MarketSessionBalance,
    BalanceTransferOut
)
from ..serializers.market_balance import (
    MarketBalanceSerializer,
    BalanceTransferOutSerializer,
    MarketSessionBalanceCreateSerializer,
    MarketSessionBalanceRetrieveSerializer
)


class MarketBalanceView(APIView):
    renderer_classes = (CustomRenderer,)
    permission_classes = (IsAuthenticated,)
    serializer_class = MarketBalanceSerializer

    @staticmethod
    def queryset(request):
        user = request.user
        balance__gte = request.query_params.get('balance__gte', None)
        balance__lte = request.query_params.get('balance__lte', None)

        validate_query_params(
            balance__lte=balance__lte,
            balance__gte=balance__gte
        )

        if user.is_superuser:
            user_id = request.query_params.get('user', None)
            if user_id:
                query = MarketBalance.objects.filter(user_id=user_id)
            else:
                query = MarketBalance.objects.all()
        else:
            query = MarketBalance.objects.filter(user_id=user.id)

        if balance__gte:
            query = query.filter(balance__gte=balance__gte)
        elif balance__lte:
            query = query.filter(balance__lte=balance__lte)

        return query

    @swagger_auto_schema(
        operation_id="get_market_balance",
        operation_description="Method to get market balance for a given agent",
        manual_parameters=market_balance_query_params(),
        responses={
            200: MarketBalanceResponse["GET"],
            400: 'Bad request',
            401: NotAuthenticatedResponse,
            403: ForbiddenAccessResponse,
            500: "Internal Server Error",
        })
    def get(self, request):
        address = self.queryset(request)
        serializer = self.serializer_class(address, many=True)
        return Response(data=serializer.data)


class MarketSessionBalanceView(APIView):
    permission_classes = (IsAuthenticated,)
    renderer_classes = [CustomRenderer]

    @staticmethod
    def queryset(request):
        user = request.user
        market_session_id = request.query_params.get('market_session', None)
        resource_id = request.query_params.get('resource', None)
        balance_by_resource = request.query_params.get('balance_by_resource',
                                                       "true")
        validate_query_params(
            market_session_id=market_session_id,
            resource_id=resource_id,
            balance_by_resource=balance_by_resource
        )

        if user.is_superuser:
            user_id = request.query_params.get('user', None)
            if user_id:
                query = MarketSessionBalance.objects.filter(user_id=user_id)
            else:
                query = MarketSessionBalance.objects.all()
        else:
            query = MarketSessionBalance.objects.filter(user_id=user.id)

        if market_session_id:
            query = query.filter(market_session_id=market_session_id)

        # Default latest_only query param to False if not declared
        balance_by_resource = False if balance_by_resource == "false" else True
        if not balance_by_resource:
            if resource_id:
                query = query.filter(resource_id=resource_id)

        return query, not balance_by_resource

    @swagger_auto_schema(
        operation_id="get_market_session_balance",
        operation_description="Method to get market balance of a "
                              "given agent resource, in a "
                              "specific market session",
        manual_parameters=market_session_balance_query_params(),
        responses={
            200: MarketSessionBalanceResponse["GET"],
            400: 'Bad request',
            401: NotAuthenticatedResponse,
            403: ForbiddenAccessResponse,
            500: "Internal Server Error",
        })
    def get(self, request):
        session_balance, sum_balance_per_user = self.queryset(request)

        serializer = MarketSessionBalanceRetrieveSerializer(session_balance,
                                                            many=True)
        # todo: try to aggregate already in queryset using django methods
        data_ = serializer.data.copy()
        df_ = pd.DataFrame(data_)
        if (not df_.empty) and sum_balance_per_user:
            df_ = df_.groupby(["market_session", "user"]).sum()
            df_.drop("resource", axis=1, inplace=True)
            data_ = df_.reset_index().to_dict(orient="records")

        return Response(data=data_)

    @swagger_auto_schema(
        operation_id="post_market_session_balance",
        operation_description="[AdminOnly] Method to insert "
                              "balance of a "
                              "given agent resource, in a "
                              "specific market session",
        request_body=MarketSessionBalanceCreateSerializer,
        responses={
            201: "Updated session balance for the user ID (<user_id>).",
            400: 'Bad request',
            401: NotAuthenticatedResponse,
            403: ForbiddenAccessResponse,
            500: "Internal Server Error",
        })
    @method_permission_classes((IsAdminUser,))
    def post(self, request):
        serializer = MarketSessionBalanceCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        response = serializer.save()
        return Response(data=response)


class BalanceTransferOutView(APIView):
    renderer_classes = (CustomRenderer,)
    permission_classes = (IsAdminUser,)
    serializer_class = BalanceTransferOutSerializer

    @staticmethod
    def queryset(request):
        user = request.user
        if user.is_superuser:
            is_solid = request.query_params.get('is_solid', None)
            user_id = request.query_params.get('user', None)
            if user_id:
                query = BalanceTransferOut.objects.filter(user_id=user_id)
            else:
                query = BalanceTransferOut.objects.all()

            if is_solid is not None:
                query = query.filter(is_solid=is_solid)
        else:
            query = BalanceTransferOut.objects.filter(
                user_id=user.id
            )
        return query

    @swagger_auto_schema(
        operation_id="get_balance_transfer_out",
        operation_description="[AdminOnly] Method to list historical balance transfers "
                              "(i.e., from market wallet to agents wallet)",
        manual_parameters=market_balance_transfer_out_query_params(),
        responses={
            200: BalanceTransferOutResponse["GET"],
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
        operation_id="post_balance_transfer_out",
        operation_description="[AdminOnly] Method to register new balance transfer",
        request_body=BalanceTransferOutSerializer,
        responses={
            400: 'Bad request',
            401: NotAuthenticatedResponse,
            403: ForbiddenAccessResponse,
            500: "Internal Server Error",
        })
    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        response = serializer.save()
        return Response(data=response)

    @swagger_auto_schema(
        operation_id="put_balance_transfer_out",
        operation_description="[AdminOnly] Method to update balance transfer",
        request_body=BalanceTransferOutSerializer,
        responses={
            400: 'Bad request',
            401: NotAuthenticatedResponse,
            403: ForbiddenAccessResponse,
            500: "Internal Server Error",
        })
    def put(self, request):
        try:
            transfer_id = request.data['withdraw_transfer_id']
            # -- Create a transaction of type - transfer:
            transfer_out = BalanceTransferOut.objects.get(
                withdraw_transfer_id=transfer_id,
            )
            serializer = self.serializer_class(
                transfer_out,
                data=request.data,
                partial=True,
                context={'request': request}
            )
            serializer.is_valid(raise_exception=True)
            serializer.update(transfer_out, serializer.validated_data)
            return Response(data=serializer.data)
        except KeyError as e:
            return Response(data={e.args[0]: ["This field is required"]},
                            status=status.HTTP_400_BAD_REQUEST)
