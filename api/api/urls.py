"""api URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.conf import settings
from django.urls import path, include, re_path
from rest_framework_simplejwt import views as jwt_views
from rest_framework import permissions

from authentication.views.login import MyTokenObtainPairView

from drf_yasg.views import get_schema_view
from drf_yasg import openapi

schema_view = get_schema_view(
    openapi.Info(
        title="Predico - Restful-API",
        default_version='v1',
        description="""
#### Description:
Restful API for the INESC TEC Data Sharing / Barter Incentives Service.

This API is crafted to enable secure data exchange and incentivized collaboration among multiple agents and a central server, where the execution of Data Sharing/Barter Incentives algorithms takes place. It robustly supports internal mechanisms for Data Sharing/Barter Incentives, addressing a diverse range of use cases.

A prominent use case, characterized by a higher Technology Readiness Level (TRL), is the collaborative forecasting scenario.
In this context, various agents can trade historical (or future) time-series data—such as power generation or weather measurements data—and acquire time-series forecasts improved by the collective pool of data available on the platform. Notably, agents can access these forecasts without directly tapping into internal datasets. The economic value of data shared by one agent is inherently tied to its utility for other participants that also buy collaborative forecasts from this service.

## Main functions:
- **User management**:
    * Register new user
    * User verification / authentication
    * User password reset
    * Manage User Resources (i.e., bidding units in user portfolio) (create/update/delete)
    * Manage User IOTA wallet address reference (create/update/delete)

- **Market management**:
    * Manage Market Sessions
    * Manage Market Balance (Session & Total Balance)
    * Manage Market Bid Placement & Validation
    * Manage Market IOTA wallet address reference (create/update/delete)

- **Data management**:
    * Raw Data Ingestion (users measurements or features data)
    * Access to forecasts (produced by the Data Sharing / Barter Incentives Service collaborative forecasting engine)

## Developers // Contacts:
- andre.f.garcia@inesctec.pt
- carla.s.goncalves@inesctec.pt
- jose.r.andrade@inesctec.pt
- ricardo.j.bessa@inesctec.pt
""",
        license=openapi.License(name="MIT License"),
    ),
    public=True,
    permission_classes=[permissions.AllowAny, ],
    url=settings.SWAGGER_BASE_URL
)

urlpatterns = [
    # Auto-Docs
    re_path(r'^swagger(?P<format>\.json|\.yaml)$', schema_view.without_ui(cache_timeout=0), name='schema-json'),
    re_path(r'^swagger/$', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    re_path(r'^redoc/$', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),
    # Admin URLs
    path('admin/', admin.site.urls),
    # API urls:
    re_path('api/token/refresh', jwt_views.TokenRefreshView.as_view(), name='token_refresh'),
    re_path('api/token', MyTokenObtainPairView.as_view(), name='token_obtain_pair'),
    re_path('api/market/', include('market.urls'), name="market"),
    re_path('api/user/', include('users.urls'), name="users"),
    re_path('api/data/', include('data.urls'), name="data")
]
