import re

from rest_framework import exceptions
from django.core.validators import RegexValidator

ResourceNameValidator = RegexValidator(r"^[a-z0-9_-]*$",
                                       "Resource name cannot contain any "
                                       "upper-case characters, "
                                       "spaces or any special "
                                       "characters besides '-' or '_'.")


def validate_query_params(
        resource_id=None,
        resource_name=None,
        to_forecast=None,
):
    if resource_id is not None:
        try:
            int(resource_id)
        except ValueError:
            raise exceptions.ValidationError(
                "Query param 'resource' must be an integer."
            )

    if resource_name is not None:
        matched = re.match("^[a-z0-9_-]*$", resource_name)
        is_match = bool(matched)
        if not is_match:
            raise exceptions.ValidationError(
                "Resource name cannot contain "
                "spaces or any special "
                "characters besides '-' or '_'."
            )

    if to_forecast is not None:
        if to_forecast.lower() not in ['true', 'false']:
            raise exceptions.ValidationError(
                "Query param 'to_forecast' must be a boolean (true/false)"
            )
