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
# UserResourcesView
###############################
GetUserResourcesResponse = \
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
                        "id": 1,
                        "name": "park-1",
                        "type": "measurements",
                        "to_forecast": True,
                        "registered_at": "2022-10-20T11:34:57.739206Z",
                        "user": 1
                    }
                ]
            },
        }
    )


UserResourcesResponse = {
    "GET": GetUserResourcesResponse,
}


###############################
# UserWalletAddressView
###############################
GetUserWalletAddressResponse = \
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
                        "user": 1,
                        "wallet_address": "xxxxx",
                        "registered_at": "2022-10-20T11:37:36.354205Z"
                    }
                ]
            },
        }
    )


UserWalletAddressResponse = {
    "GET": GetUserWalletAddressResponse,
}
