from rest_framework import generics, permissions, status
from django.contrib.auth.models import User
from .serializers import RegisterSerializer
from rest_framework_simplejwt.views import TokenObtainPairView

from rest_framework.views import APIView
from rest_framework.response import Response
from .models import UserAPIKey

class CreateUserAPIKey(APIView):
    """Endpoint untuk membuat API key untuk user"""
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        user = request.user

        # Buat API key baru
        api_key, key = UserAPIKey.objects.create_key(
            name=f"{user.username}_key",
            user=user
        )

        return Response({
            'user': user.username,
            'api_key_id': api_key.id,
            'api_key': key,
            'message': 'Save this API key securely!'
        })

class RegisterView(generics.CreateAPIView):
    queryset = User.objects.all()
    permission_classes = [permissions.AllowAny]
    serializer_class = RegisterSerializer
