from drf_yasg.utils import swagger_auto_schema
from rest_framework import status, exceptions
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, IsAdminUser

from api.utils.permissions import method_permission_classes
from api.renderers.CustomRenderer import CustomRenderer

from ..schemas.query import *
from ..schemas.responses import *
from ..util.validators import validate_query_params

from ..models.market_session import (
    MarketSession,
    MarketSessionFee,
    MarketSessionPriceWeight,
    MarketSessionTransactions,
)

from ..serializers.market_session import (
    MarketSessionSerializer,
    MarketSessionFeeSerializer,
    MarketSessionPriceWeightRetrieveSerializer,
    MarketSessionPriceWeightCreateSerializer,
    MarketSessionTransactionsSerializer,
)


class MarketSessionView(APIView):
    permission_classes = (IsAuthenticated,)
    renderer_classes = [CustomRenderer]
    serializer_class = MarketSessionSerializer

    @staticmethod
    def queryset(request):
        session_status = request.query_params.get('status', None)
        market_session_id = request.query_params.get('market_session', None)
        latest_only = request.query_params.get('latest_only', None)
        validate_query_params(
            market_session_id=market_session_id,
            market_session_status=session_status,
            latest_only=latest_only
        )

        # initial query:
        sessions = MarketSession.objects.all()

        if market_session_id is not None:
            sessions = sessions.filter(id=market_session_id)

        if session_status is not None:
            sessions = sessions.filter(status=session_status)

        # Default latest_only query param to False if not declared
        latest_only = 'false' if latest_only is None else latest_only.lower()
        latest_only = False if latest_only == "false" else True
        if latest_only:
            last_sess = sessions.order_by('id').last()
            sessions = [] if last_sess is None else [last_sess]
        return sessions

    @swagger_auto_schema(
        operation_id="get_market_session",
        operation_description="List market sessions",
        manual_parameters=market_session_query_params(),
        responses={
            200: MarketSessionResponse["GET"],
            400: 'Bad request',
            401: NotAuthenticatedResponse,
            403: ForbiddenAccessResponse,
            500: "Internal Server Error",
        })
    def get(self, request):
        sessions = self.queryset(request)
        serializer = self.serializer_class(sessions, many=True)
        return Response(serializer.data)

    @swagger_auto_schema(
        operation_id="post_market_session",
        operation_description="[AdminOnly] Method to register market session",
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
        serializer.save()
        return Response(data=serializer.data)


class MarketSessionUpdateView(APIView):
    permission_classes = (IsAuthenticated,)
    renderer_classes = [CustomRenderer]
    serializer_class = MarketSessionSerializer

    @swagger_auto_schema(
        operation_id="patch_market_session",
        operation_description="[AdminOnly] Method to update market "
                              "session details",
        responses={
            400: 'Bad request',
            401: NotAuthenticatedResponse,
            403: ForbiddenAccessResponse,
            500: "Internal Server Error",
        })
    @method_permission_classes((IsAdminUser,))
    def patch(self, request, session_id=None):

        if session_id is None:
            raise exceptions.ValidationError("Missing 'session_id' url "
                                             "parameter.")

        try:
            market_session = MarketSession.objects.get(id=session_id)
            serializer = self.serializer_class(
                market_session,
                data=request.data,
                partial=True,
                context={'request': request, "session_id": session_id})
            serializer.is_valid(raise_exception=True)
            serializer.update(market_session, serializer.validated_data)
            return Response(data=serializer.data)
        except MarketSession.DoesNotExist:
            return Response(data="That market session ID does not exist.",
                            status=status.HTTP_400_BAD_REQUEST)
        except KeyError as e:
            return Response(data={e.args[0]: ["This field is required"]},
                            status=status.HTTP_400_BAD_REQUEST)


class MarketPriceWeightView(APIView):
    permission_classes = (IsAdminUser,)
    renderer_classes = [CustomRenderer]

    @staticmethod
    def queryset(request):
        market_session_id = request.query_params.get('market_session', None)
        validate_query_params(market_session_id=market_session_id)
        if market_session_id:
            query = MarketSessionPriceWeight.objects.filter(
                market_session_id=market_session_id
            )
        else:
            query = MarketSessionPriceWeight.objects.all()
        return query

    def get(self, request):
        query = self.queryset(request)
        serializer = MarketSessionPriceWeightRetrieveSerializer(query,
                                                                many=True)
        return Response(data=serializer.data)

    def post(self, request):
        serializer = MarketSessionPriceWeightCreateSerializer(
            data=request.data
        )
        serializer.is_valid(raise_exception=True)
        response = serializer.save()
        return Response(data=response)


class MarketSessionTransactionsView(APIView):
    renderer_classes = (CustomRenderer,)
    permission_classes = (IsAuthenticated,)
    serializer_class = MarketSessionTransactionsSerializer

    @staticmethod
    def queryset(request):
        user = request.user
        market_session_id = request.query_params.get('market_session', None)
        validate_query_params(market_session_id=market_session_id)

        if user.is_superuser:
            user_id = request.query_params.get('user', None)
            if user_id:
                query = MarketSessionTransactions.objects.filter(
                    user_id=user_id
                )
            else:
                query = MarketSessionTransactions.objects.all()
        else:
            query = MarketSessionTransactions.objects.filter(
                user_id=user.id
            )

        if market_session_id:
            query = query.filter(market_session_id=market_session_id)

        return query

    # @swagger_auto_schema(
    #     operation_id="get_market_session_transactions",
    #     operation_description="List market session transactions",
    #     manual_parameters=market_session_transactions_query_params(),
    #     responses={
    #         200: MarketSessionTransactionsResponse["GET"],
    #         400: 'Bad request',
    #         401: NotAuthenticatedResponse,
    #         403: ForbiddenAccessResponse,
    #         500: "Internal Server Error",
    #     })
    def get(self, request):
        address = self.queryset(request)
        serializer = self.serializer_class(address, many=True)
        return Response(data=serializer.data)


class MarketSessionFeeView(APIView):
    renderer_classes = (CustomRenderer,)
    permission_classes = (IsAdminUser,)
    serializer_class = MarketSessionFeeSerializer

    @staticmethod
    def queryset(request):
        market_session_id = request.query_params.get('market_session', None)
        validate_query_params(market_session_id=market_session_id)
        if market_session_id:
            query = MarketSessionFee.objects.filter(
                market_session_id=market_session_id
            )
        else:
            query = MarketSessionFee.objects.all()
        return query

    # @swagger_auto_schema(
    #     operation_id="get_market_session_fee",
    #     operation_description="[AdminOnly] List market session fees",
    #     responses={
    #         400: 'Bad request',
    #         401: NotAuthenticatedResponse,
    #         403: ForbiddenAccessResponse,
    #         500: "Internal Server Error",
    #     })
    def get(self, request):
        fee = self.queryset(request)
        serializer = self.serializer_class(fee, many=True)
        return Response(data=serializer.data)

    # @swagger_auto_schema(
    #     operation_id="post_market_session_fee",
    #     operation_description="[AdminOnly] Method to register "
    #                           "market session fee",
    #     request_body=MarketSessionFeeSerializer,
    #     responses={
    #         201: 'Market fee registered with success.',
    #         400: 'Bad request',
    #         401: NotAuthenticatedResponse,
    #         403: ForbiddenAccessResponse,
    #         500: "Internal Server Error",
    #     })
    def post(self, request):
        serializer = self.serializer_class(
            data=request.data,
            context={'request': request}
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(data="Market fee registered with success.")
