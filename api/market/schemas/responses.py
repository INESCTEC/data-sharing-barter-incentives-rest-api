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
# MarketBalanceView
###############################
GetMarketBalanceResponse = \
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
                        "balance": 0,
                        "total_deposit": 10000000,
                        "total_withdraw": 6000000,
                        "total_payment": 5000000,
                        "total_revenue": 1000000,
                        "updated_at": "2022-07-25T11:08:18.289370Z"
                    }
                ]
            },
        }
    )


MarketBalanceResponse = {
    "GET": GetMarketBalanceResponse,
}


###############################
# MarketSessionBalanceView
###############################
GetMarketSessionBalanceResponse = \
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
                        "user": 1,
                        "resource": 1,
                        "session_balance": 3000000,
                        "session_deposit": 3000000,
                        "session_payment": 0,
                        "session_revenue": 0,
                        "registered_at": "2022-10-20T11:40:22.364907Z"
                    },
                ]
            },
        }
    )


MarketSessionBalanceResponse = {
    "GET": GetMarketSessionBalanceResponse,
}


###############################
# BalanceTransferOutView
###############################
GetBalanceTransferOutResponse = \
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
                "data": []
            },
        }
    )


BalanceTransferOutResponse = {
    "GET": GetBalanceTransferOutResponse,
}


###############################
# MarketSessionView
###############################
GetMarketSessionResponse = \
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
                        "session_number": 1,
                        "session_date": "2022-10-20",
                        "staged_ts": "2022-10-20T11:27:06.128045Z",
                        "open_ts": "2022-10-20T11:27:10.567510Z",
                        "close_ts": "2022-10-20T11:40:07.478614Z",
                        "launch_ts": None,
                        "finish_ts": None,
                        "status": "closed",
                        "market_price": 5500000,
                        "b_min": 500000,
                        "b_max": 10000000,
                        "n_price_steps": 20,
                        "delta": 0.05
                    }
                ]
            }
        }
    )


MarketSessionResponse = {
    "GET": GetMarketSessionResponse,
}


###############################
# MarketSessionTransactionsView
###############################
GetMarketSessionTransactionsResponse = \
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
                        "user": 2,
                        "resource": 1,
                        "amount": 3000000,
                        "transaction_type": "transfer_in",
                        "registered_at": "2022-10-20T11:40:22.374024Z"
                    }
                ]
            }
        }
    )


MarketSessionTransactionsResponse = {
    "GET": GetMarketSessionTransactionsResponse,
}


###############################
# MarketSessionBidView
###############################
GetMarketSessionBidResponse = \
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
                        "tangle_msg_id": "xxxx",
                        "max_payment": 3000000,
                        "bid_price": 5500000,
                        "gain_func": "mse",
                        "confirmed": True,
                        "registered_at": "2022-10-20T11:37:38.442420Z",
                        "has_forecasts": False,
                        "user": 1,
                        "resource": 1,
                        "market_session": 1
                    },
                ]
            }
        }
    )


MarketSessionBidResponse = {
    "GET": GetMarketSessionBidResponse,
}


###############################
# MarketWalletAddressView
###############################
GetMarketWalletAddressResponse = \
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
                "data": {
                    "wallet_address": "xxxxxxx",
                    "registered_at": "2022-10-20T11:26:40.731171Z"
                }
            }
        }
    )


MarketWalletAddressResponse = {
    "GET": GetMarketWalletAddressResponse,
}
