from .utils.api_client import APIClient
from .permissions import HasUserAPIKey, IsAPIKeyOwner
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

class UnifiedWeatherView(APIView):
    permission_classes = [HasUserAPIKey, IsAPIKeyOwner]

    def get(self, request, format=None):
        city = request.GET.get('city', 'London')
        country = request.GET.get('country', 'UK')

        client = APIClient()
        results = client.make_request(
            'openweather',
            '/weather',
            params={'q': f"{city},{country}", 'units': 'metric'},
            user=request.user if request.user.is_authenticated else None
        )

        return Response(results)


class UnifiedNewsView(APIView):
    permission_classes = [HasUserAPIKey, IsAPIKeyOwner]

    def get(self, request, format=None):
        category = request.GET.get('category', 'general')

        client = APIClient()
        results = client.make_request(
            'newsapi',
            '/v2/top-headlines',
            params={'category': category, 'pageSize': 10},
            user=request.user if request.user.is_authenticated else None
        )

        return Response(results)


class GitHubUserInfoView(APIView):
    permission_classes = [HasUserAPIKey, IsAPIKeyOwner]

    def get(self, request, format=None):
        username = request.GET.get('username')

        if not username:
            return Response({'error': 'Username parameter required'}, status=400)

        client = APIClient()
        results = client.make_request(
            'github',
            f'/users/{username}',
            user=request.user if request.user.is_authenticated else None
        )

        return Response(results)
