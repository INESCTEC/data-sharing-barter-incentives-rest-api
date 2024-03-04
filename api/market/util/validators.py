import uuid

from rest_framework import exceptions
from ..models import MarketSession


def validate_query_params(
        market_session_id=None,
        resource_id=None,
        market_session_status=None,
        confirmed=None,
        latest_only=None,
        balance__lte=None,
        balance__gte=None,
        balance_by_resource=None,
):
    if market_session_id is not None:
        try:
            int(market_session_id)
        except ValueError:
            raise exceptions.ValidationError(
                "Query param 'market_session' must be an integer."
            )
    if resource_id is not None:
        try:
            uuid.UUID(resource_id)
        except ValueError:
            raise exceptions.ValidationError(
                "Query param 'resource' must be a valid uuid."
            )
    if market_session_status is not None:
        lbl = [x.lower() for x in MarketSession.MarketStatus.labels]
        if market_session_status.lower() not in lbl:
            raise exceptions.ValidationError(
                f"Query param 'session_status' must be "
                f"one of the following {lbl}"
            )
    if confirmed is not None:
        if confirmed.lower() not in ['true', 'false']:
            raise exceptions.ValidationError(
                "Query param 'confirmed' must be a boolean (true/false)"
            )

    if latest_only is not None:
        if latest_only.lower() not in ['true', 'false']:
            raise exceptions.ValidationError(
                "Query param 'latest_only' must be a boolean (true/false)"
            )

    if balance_by_resource is not None:
        if balance_by_resource.lower() not in ['true', 'false']:
            raise exceptions.ValidationError(
                "Query param 'balance_by_resource' must be a boolean "
                "(true/false)"
            )

    if balance__lte is not None:
        try:
            float(balance__lte)
        except ValueError:
            raise exceptions.ValidationError(
                "Query param 'balance__lte' must be an integer or float."
            )

    if balance__gte is not None:
        try:
            float(balance__gte)
        except ValueError:
            raise exceptions.ValidationError(
                "Query param 'balance__gte' must be an integer or float."
            )
