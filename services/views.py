from .utils.api_client import APIClient
from rest_framework.views import APIView
from rest_framework.response import Response
from .permissions import HasAPIKey
from rest_framework.permissions import IsAuthenticated

class UnifiedWeatherView(APIView):
    permission_classes = [HasAPIKey]

    def get(self, request, format=None):
        city = request.GET.get('city', 'London')
        country = request.GET.get('country', 'UK')

        client = APIClient()
        results = client.make_request(
            'openweather',
            '/weather',
            params={'q': f"{city},{country}", 'units': 'metric'},
            user=request.user
        )

        return Response(results)


class UnifiedNewsView(APIView):
    permission_classes = [HasAPIKey]

    def get(self, request, format=None):
        category = request.GET.get('category', 'general')

        client = APIClient()
        results = client.make_request(
            'newsapi',
            '/v2/top-headlines',
            params={'category': category, 'pageSize': 10},
            user=request.user
        )

        return Response(results)


class GitHubUserInfoView(APIView):
    permission_classes = [HasAPIKey]

    def get(self, request, format=None):
        username = request.GET.get('username')

        if not username:
            return Response({'error': 'Username parameter required'}, status=400)

        client = APIClient()
        results = client.make_request(
            'github',
            f'/users/{username}',
            user=request.user
        )

        return Response(results)


class CGSimplePriceView(APIView):
    permission_classes = [HasAPIKey]

    def get(self, request, format=None):
        ids = request.GET.get('ids')
        vs_currencies = request.GET.get('vs_currencies')

        missing = False
        if not ids and not vs_currencies:
            missing = "ids and vs_currencies"
        elif not ids:
            missing = "ids"
        elif not vs_currencies:
            missing = "vs_currencies"

        if missing:
            return Response({'error': f'{missing} parameter required'}, status=400)

        client = APIClient()
        results = client.make_request(
            'coingecko',
            '/simple/price',
            params={'ids': ids, 'vs_currencies': vs_currencies},
            user=request.user
        )

        return Response(results)


class CGCoinDetailView(APIView):
    permission_classes = [HasAPIKey]

    def get(self, request, format=None):
        coinId = request.GET.get('id')

        if not coinId:
            return Response({'error': 'id parameter required'}, status=400)

        client = APIClient()
        results = client.make_request(
            'coingecko',
            f'/coins/{coinId}',
            user=request.user
        )

        return Response(results)


class CGCoinMarketChartView(APIView):
    permission_classes = [HasAPIKey]

    def get(self, request, format=None):
        vs_currency = request.GET.get('vs_currency')
        days = request.GET.get('days')
        id = request.GET.get('id')

        missing = False
        if not days and not vs_currency and not id:
            missing = "days, vs_currency and id"
        elif not days:
            missing = "days"
        elif not vs_currency:
            missing = "vs_currency"
        elif not id:
            missing = "id"

        if missing:
            return Response({'error': f'{missing} parameter required'}, status=400)

        client = APIClient()
        results = client.make_request(
            'coingecko',
            f'/coins/{id}/market_chart',
            params={"vs_currency": vs_currency, "days": days},
            user=request.user
        )

        return Response(results)


class CGHistoryCoinView(APIView):
    permission_classes = [HasAPIKey]

    def get(self, request, format=None):
        date = request.GET.get('date')

        if not date:
            return Response({'error': 'date parameter required'}, status=400)

        coinId = request.GET.get('id')

        if not coinId:
            return Response({'error': 'id parameter required'}, status=400)

        client = APIClient()
        results = client.make_request(
            'coingecko',
            f'/coins/{coinId}/history',
            params={"date": date},
            user=request.user
        )

        return Response(results)


class CGSearchView(APIView):
    permission_classes = [HasAPIKey]

    def get(self, request, format=None):
        query = request.GET.get('query')

        if not query:
            return Response({'error': 'query parameter required'}, status=400)

        client = APIClient()
        results = client.make_request(
            'coingecko',
            '/search',
            params={"query": query},
            user=request.user
        )

        return Response(results)


class CGSearchTrendingView(APIView):
    permission_classes = [HasAPIKey]

    def get(self, request, format=None):
        client = APIClient()
        results = client.make_request(
            'coingecko',
            '/search/trending',
            user=request.user
        )

        return Response(results)


class CGExchangesView(APIView):
    permission_classes = [HasAPIKey]

    def get(self, request, format=None):
        client = APIClient()
        results = client.make_request(
            'coingecko',
            '/exchanges',
            user=request.user
        )

        return Response(results)


class CGExchangesDetailView(APIView):
    permission_classes = [HasAPIKey]

    def get(self, request, format=None):
        exchangesId = request.GET.get('id')

        if not exchangesId:
            return Response({'error': 'id parameter required'}, status=400)

        client = APIClient()
        results = client.make_request(
            'coingecko',
            f'/exchanges/{exchangesId}',
            user=request.user
        )

        return Response(results)


class ExchangesRateView(APIView):
    permission_classes = [HasAPIKey]

    def get(self, request, format=None):
        client = APIClient()
        results = client.make_request(
            'exchangeRate',
            '/latest/USD',
            user=request.user
        )

        return Response(results)
