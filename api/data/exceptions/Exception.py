from rest_framework.exceptions import APIException


class RawResourceNotAssigned(APIException):

    def __init__(self, resource_name):
        super().__init__(self.default_detail.format(resource_name))
    status_code = 409
    default_detail = "Resource ID '{}' is not registered for this user. " \
                     "You must register it first."
    default_code = 'raw_resource_not_assigned'


class ForecastResourceNotAssigned(APIException):

    def __init__(self, resource_name):
        super().__init__(self.default_detail.format(resource_name))
    status_code = 409
    default_detail = "Resource ID '{}' is not registered in the platform. " \
                     "Resource owner must register it first."
    default_code = 'forecast_resource_not_assigned'
