from rest_framework_simplejwt.views import TokenObtainPairView

from ..serializers.login import MyTokenObtainPairSerializer

# Todo: change internal PK / FK to UUID
# Todo: Check if the access / refresh tokens can be easily decoded


class MyTokenObtainPairView(TokenObtainPairView):
    serializer_class = MyTokenObtainPairSerializer
