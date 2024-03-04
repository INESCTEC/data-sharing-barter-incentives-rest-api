from drf_yasg.utils import swagger_auto_schema
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, IsAdminUser

from api.utils.permissions import method_permission_classes
from api.renderers.CustomRenderer import CustomRenderer

from ..schemas.query import *
from ..schemas.responses import *
from ..util.validators import validate_query_params
from ..serializers.market_forecasts import (
    MarketForecastsRetrieveSerializer,
    MarketForecastsCreateSerializer,
)
from ..models.market_forecasts import MarketForecasts


class MarketForecastsView(APIView):
    renderer_classes = (CustomRenderer,)
    permission_classes = (IsAuthenticated,)

    @staticmethod
    def queryset(request):
        user = request.user
        start_date = request.query_params.get('start_date', None)
        end_date = request.query_params.get('end_date', None)
        resource_id = request.query_params.get('resource', None)
        market_session_id = request.query_params.get('market_session', None)
        validate_query_params(
            start_date=start_date,
            end_date=end_date,
            resource_id=resource_id,
            market_session_id=market_session_id
        )

        if user.is_superuser:
            user_id = request.query_params.get('user', None)
            if user_id:
                query = MarketForecasts.objects.filter(user=user_id)
            else:
                query = MarketForecasts.objects.all()
        else:
            query = MarketForecasts.objects.filter(user=user.id)

        if start_date is not None:
            query = query.filter(datetime__gte=start_date)
        if end_date is not None:
            query = query.filter(datetime__lte=end_date)
        if market_session_id:
            query = query.filter(market_session_id=market_session_id)
        if resource_id:
            query = query.filter(resource_id=resource_id)

        # Order records by datetime
        query = query.order_by('datetime', 'request')

        return query

    @swagger_auto_schema(
        operation_id="get_market_forecasts",
        operation_description="Method to get market forecasts for a specific "
                              "agent resource",
        manual_parameters=raw_data_query_params(),
        responses={
            200: RawDataResponse["GET"],
            400: 'Bad request',
            401: NotAuthenticatedResponse,
            403: ForbiddenAccessResponse,
            500: "Internal Server Error",
        })
    def get(self, request):
        address = self.queryset(request)
        serializer = MarketForecastsRetrieveSerializer(address, many=True)
        return Response(data=serializer.data, status=status.HTTP_200_OK)

    @swagger_auto_schema(
        operation_id="post_market_forecasts",
        operation_description="[AdminOnly] Method to register market forecasts "
                              "for a specific agent resource",
        request_body=MarketForecastsCreateSerializer,
        responses={
            400: 'Bad request',
            401: NotAuthenticatedResponse,
            403: ForbiddenAccessResponse,
            500: "Internal Server Error",
        })
    @method_permission_classes((IsAdminUser,))
    def post(self, request):
        serializer = MarketForecastsCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        response = serializer.save()
        return Response(data=response, status=status.HTTP_200_OK)
