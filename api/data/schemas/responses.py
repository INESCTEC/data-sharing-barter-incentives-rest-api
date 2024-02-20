from drf_yasg import openapi
from .util import create_schema


# Response for when a valid token is needed and not given in the request
NotAuthenticatedResponse = \
    openapi.Response(
        description="Unauthorized",
        schema=openapi.Schema(
            title="Not Authenticated schema",
            type=openapi.TYPE_OBJECT,
            properties={
                "code": create_schema(
                    type=openapi.TYPE_INTEGER,
                    enum=[401],
                    description="Response status code."
                ),
                "data": create_schema(
                    type=openapi.TYPE_OBJECT,
                    description="Null field in case of error response."
                ),
                "status": create_schema(
                    type=openapi.TYPE_STRING,
                    enum=["error"],
                    description="Response status info."
                ),
                "message": create_schema(
                    type=openapi.TYPE_STRING,
                    enum=["Authentication credentials were not provided."],
                    description="Error message."
                ),
            },
        ),
        examples={
            "application/json": {
                "code": 401,
                "data": None,
                "status": "error",
                "message": "Given token not valid for any token type"
            },
        }
    )

ForbiddenAccessResponse = \
    openapi.Response(
        description="Forbidden",
        schema=openapi.Schema(
            title="Forbidden access schema",
            type=openapi.TYPE_OBJECT,
            properties={
                "code": create_schema(
                    type=openapi.TYPE_INTEGER,
                    enum=[403],
                    description="Response status code."
                ),
                "data": create_schema(
                    type=openapi.TYPE_OBJECT,
                    description="Null field in case of error response."
                ),
                "status": create_schema(
                    type=openapi.TYPE_STRING,
                    enum=["error"],
                    description="Response status info."
                ),
                "message": create_schema(
                    type=openapi.TYPE_STRING,
                    enum=["You do not have permission to perform this action."],
                    description="Error message."
                ),
            },
        ),
        examples={
            "application/json": {
                "code": 403,
                "data": None,
                "status": "error",
                "message": "You do not have permission to perform this action."
            },
        }
    )


###############################
# RawDataView
###############################
GetRawDataResponse = \
    openapi.Response(
        description="Success",
        schema=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                "code": create_schema(
                    type=openapi.TYPE_INTEGER,
                    enum=[200],
                    description="Response status code."
                ),
                "data": create_schema(
                    type=openapi.TYPE_OBJECT,
                    description="Response data."
                ),
            },
        ),
        examples={
            "application/json": {
                "code": 200,
                "data": [
                    {
                        "datetime": "2022-10-01T00:34:58Z",
                        "value": 7802,
                        "units": "kw",
                        "resource": 1,
                        "resource_type": "measurements",
                        "time_interval": "60",
                        "aggregation_type": "avg",
                        "registered_at": "2022-10-20T11:34:58.131623Z"
                    },
                    {
                        "datetime": "2022-10-01T01:34:58Z",
                        "value": 7164,
                        "units": "kw",
                        "resource": 1,
                        "resource_type": "measurements",
                        "time_interval": "60",
                        "aggregation_type": "avg",
                        "registered_at": "2022-10-20T11:34:58.131623Z"
                    },
                ]
            },
        }
    )


RawDataResponse = {
    "GET": GetRawDataResponse,
}


###############################
# MarketForecastsView
###############################
GetMarketForecastsResponse = \
    openapi.Response(
        description="Success",
        schema=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                "code": create_schema(
                    type=openapi.TYPE_INTEGER,
                    enum=[200],
                    description="Response status code."
                ),
                "data": create_schema(
                    type=openapi.TYPE_OBJECT,
                    description="Response data."
                ),
            },
        ),
        examples={
            "application/json": {
                "code": 200,
                "data": [
                    {
                        "market_session": 1,
                        "datetime": "2022-10-01T10:00:00Z",
                        "request": "2022-10-01T00:34:58Z",
                        "value": 0.9661258461978153,
                        "units": "kw",
                        "resource": 1,
                        "registered_at": "2022-10-01T11:34:58.131623Z",
                        "resource_name": "park-1"
                    }
                ]
            },
        }
    )


MarketForecastsResponse = {
    "GET": GetMarketForecastsResponse,
}
