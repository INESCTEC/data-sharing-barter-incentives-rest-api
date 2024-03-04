from drf_yasg.utils import swagger_auto_schema
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

from api.renderers.CustomRenderer import CustomRenderer

from ..schemas.query import *
from ..schemas.responses import *
from ..util.validators import validate_query_params
from ..serializers.raw_data import (
    RawDataRetrieveSerializer,
    RawDataCreateSerializer,
)
from ..models.raw_data import RawData


class RawDataView(APIView):
    renderer_classes = (CustomRenderer,)
    permission_classes = (IsAuthenticated,)

    @staticmethod
    def queryset(request):
        user = request.user
        start_date = request.query_params.get('start_date', None)
        end_date = request.query_params.get('end_date', None)
        resource_id = request.query_params.get('resource', None)
        validate_query_params(
            start_date=start_date,
            end_date=end_date,
            resource_id=resource_id,
        )

        if user.is_superuser:
            user_id = request.query_params.get('user', None)
            if user_id:
                query = RawData.objects.filter(user=user_id)
            else:
                query = RawData.objects.all()
        else:
            query = RawData.objects.filter(user=user.id)

        if start_date is not None:
            query = query.filter(datetime__gte=start_date)
        if end_date is not None:
            query = query.filter(datetime__lte=end_date)
        if resource_id is not None:
            query = query.filter(resource_id=resource_id)

        # Order records by datetime
        query = query.order_by('datetime')

        return query

    @swagger_auto_schema(
        operation_id="get_raw_data",
        operation_description="Method to get raw data for a specific "
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
        query = self.queryset(request)
        serializer = RawDataRetrieveSerializer(query, many=True)
        return Response(data=serializer.data, status=status.HTTP_200_OK)

    @staticmethod
    @swagger_auto_schema(
        operation_id="post_raw_data",
        operation_description="Method for agents to post raw data "
                              "for a specific resource",
        request_body=RawDataCreateSerializer,
        responses={
            400: 'Bad request',
            401: NotAuthenticatedResponse,
            403: ForbiddenAccessResponse,
            500: "Internal Server Error",
        })
    def post(request):
        request.data["user"] = request.user.id
        serializer = RawDataCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        response = serializer.save()
        return Response(data=response, status=status.HTTP_200_OK)
