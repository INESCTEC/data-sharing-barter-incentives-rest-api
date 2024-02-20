import structlog
from django.conf import settings
from django.db.models import Q
from drf_yasg.utils import swagger_auto_schema
from rest_framework import exceptions
from rest_framework import status
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework.response import Response
from rest_framework.views import APIView

from api.email.utils.email_utils import send_email_as_thread
from api.renderers.CustomRenderer import CustomRenderer
from ..models.market_session_bid import MarketSessionBid
from ..schemas.query import *
from ..schemas.responses import *
from ..serializers.market_session_bid import (
    MarketSessionBidCreateSerializer,
    MarketSessionBidUpdateSerializer,
    MarketSessionBidRetrieveSerializer,
    MarketValidateSessionBidSerializer
)

# init logger:
logger = structlog.get_logger("api_logger")


class MarketSessionBidView(APIView):
    permission_classes = (IsAuthenticated,)
    renderer_classes = [CustomRenderer]

    @staticmethod
    def queryset(request):
        user = request.user
        market_session_id = request.query_params.get('market_session')
        resource_id = request.query_params.get('resource')
        confirmed_param = request.query_params.get('confirmed')
        confirmed = confirmed_param.lower() == 'true' if confirmed_param is not None else None

        # If user is not superuser, filter by user_id else give the superuser the ability to filter by user_id
        user_id = request.query_params.get('user') if user.is_superuser else user.id

        # Construct query filters using Q objects for conditional filtering
        query_filters = Q()
        if market_session_id:
            query_filters &= Q(market_session_id=market_session_id)
        if resource_id:
            query_filters &= Q(resource_id=resource_id)
        if confirmed is not None:
            query_filters &= Q(confirmed=confirmed)
        if user_id:
            query_filters &= Q(user_id=user_id)

        # Perform query using Django ORM
        bids = MarketSessionBid.objects.filter(query_filters).select_related('payment').all()

        return bids

    @swagger_auto_schema(
        operation_id="get_market_session_bid",
        operation_description="Method for agents to list bids for their "
                              "resources in data market sessions",
        manual_parameters=market_session_bid_query_params(),
        responses={
            200: MarketSessionBidResponse["GET"],
            400: 'Bad request',
            401: NotAuthenticatedResponse,
            403: ForbiddenAccessResponse,
            500: "Internal Server Error",
        })
    def get(self, request):
        """
        Get all session participants
        :param request:
        :return:
        """
        bids = self.queryset(request)
        serializer = MarketSessionBidRetrieveSerializer(bids, many=True)
        return Response(serializer.data)

    @staticmethod
    @swagger_auto_schema(
        operation_id="post_market_session_bid",
        operation_description="Method for agents to place a bid to purchase "
                              "forecasts for a given resource in their "
                              "portfolio and a specific market session",
        request_body=MarketSessionBidCreateSerializer,
        responses={
            400: 'Bad request',
            401: NotAuthenticatedResponse,
            403: ForbiddenAccessResponse,
            500: "Internal Server Error",
        })
    def post(request):
        """
        Place a bid order in the market session
        :param request:
        :return:
        """
        serializer = MarketSessionBidCreateSerializer(
            data=request.data,
            context={'request': request}
        )
        serializer.is_valid(raise_exception=True)

        if settings.ENVIRONMENT == "production":
            email = request.user.email
            send_email_as_thread(
                destination=[email],
                email_opt_key="email-bid-confirmation",
                format_args=serializer.validated_data,
                fail_silently=False
            )

        response = serializer.save()
        return Response(data=response, status=status.HTTP_200_OK)


class MarketSessionBidUpdateView(APIView):
    permission_classes = (IsAuthenticated,)
    renderer_classes = [CustomRenderer]

    @staticmethod
    @swagger_auto_schema(
        operation_id="patch_market_session_bid",
        operation_description="Method for agents to provide the IOTA "
                              "tangle message ID identifier for bids to "
                              "purchase forecasts for their resources.",
        request_body=MarketSessionBidUpdateSerializer,
        responses={
            400: 'Bad request',
            401: NotAuthenticatedResponse,
            403: ForbiddenAccessResponse,
            500: "Internal Server Error",
        })
    def patch(request, bid_id=None):
        # todo: confirm if this user cannot change bid from other users
        if bid_id is None:
            raise exceptions.ValidationError("Missing 'bid_id' url parameter.")

        try:
            market_session = MarketSessionBid.objects.get(id=bid_id)
            serializer = MarketSessionBidUpdateSerializer(
                market_session,
                data=request.data,
                partial=True,
                context={'request': request, "bid_id": bid_id})
            serializer.is_valid(raise_exception=True)

            if settings.ENVIRONMENT == "production":
                email = request.user.email
                send_email_as_thread(
                    destination=[email],
                    email_opt_key="email-bid-tangle-id-confirmation",
                    format_args=serializer.validated_data,
                    fail_silently=False
                )

            response = serializer.update(market_session, serializer.validated_data)
            return Response(data=response)

        except MarketSessionBid.DoesNotExist:
            return Response(data="That market bid ID does not exist.",
                            status=status.HTTP_400_BAD_REQUEST)


class MarketValidateSessionBidView(APIView):
    permission_classes = (IsAdminUser,)
    renderer_classes = [CustomRenderer]
    serializer_class = MarketValidateSessionBidSerializer

    @swagger_auto_schema(
        operation_id="post_market_validate_session_bid",
        operation_description="[AdminOnly] Method for market engine to "
                              "update bid status to valid",
        request_body=MarketValidateSessionBidSerializer,
        responses={
            400: 'Bad request',
            401: NotAuthenticatedResponse,
            403: ForbiddenAccessResponse,
            500: "Internal Server Error",
        })
    def post(self, request):
        """
        Get all session participants
        :param request:
        :return:
        """
        serializer = self.serializer_class(
            data=request.data,
            context={'request': request}
        )
        serializer.is_valid(raise_exception=True)
        response = serializer.save()
        return Response(data=response)
