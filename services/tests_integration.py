
from unittest.mock import patch
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from django.contrib.auth.models import User
from user.models import UserAPIKey
from services.models import ThirdPartyService

class BaseServiceIntegrationTest(APITestCase):
    def setUp(self):
        # Buat user dan API key untuk otentikasi
        self.user = User.objects.create_user(username='testuser', password='testpass123')
        self.api_key, self.key_plain = UserAPIKey.objects.create_key(name="test-key", user=self.user)
        self.client.credentials(HTTP_AUTHORIZATION=f'Api-Key {self.key_plain}')
        self.client.force_authenticate(user=self.user)

        # Buat mock untuk ThirdPartyService
        ThirdPartyService.objects.create(
            name="openweather",
            api_endpoint="http://mock.weather.api",
            is_active=True
        ).set_api_key("weather_key")
        
        ThirdPartyService.objects.create(
            name="newsapi",
            api_endpoint="http://mock.news.api",
            is_active=True
        ).set_api_key("news_key")

        ThirdPartyService.objects.create(
            name="github",
            api_endpoint="http://mock.github.api",
            is_active=True
        ).set_api_key("github_key")

        ThirdPartyService.objects.create(
            name="coingecko",
            api_endpoint="http://mock.coingecko.api",
            is_active=True
        ).set_api_key("coingecko_key")

        ThirdPartyService.objects.create(
            name="exchangeRate",
            api_endpoint="http://mock.exchange.api",
            is_active=True
        ).set_api_key("exchange_key")


@patch('services.views.APIClient.make_request')
class WeatherViewTests(BaseServiceIntegrationTest):
    def test_get_weather_success(self, mock_make_request):
        """Uji endpoint cuaca berhasil."""
        mock_make_request.return_value = {'temperature': 25, 'city': 'London'}
        
        url = reverse('unified-weather') + '?city=London&country=UK'
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, {'temperature': 25, 'city': 'London'})
        mock_make_request.assert_called_once_with(
            'openweather',
            '/weather',
            params={'q': 'London,UK', 'units': 'metric'},
            user=self.user
        )

    def test_weather_view_no_api_key(self, mock_make_request):
        """Uji akses endpoint cuaca tanpa API key."""
        self.client.credentials() # Hapus header otentikasi
        url = reverse('unified-weather')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)


@patch('services.views.APIClient.make_request')
class NewsViewTests(BaseServiceIntegrationTest):
    def test_get_news_success(self, mock_make_request):
        mock_make_request.return_value = {'articles': [{ 'title': 'Test Article'}]}
        url = reverse('unified-news') + '?category=technology'
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        mock_make_request.assert_called_with(
            'newsapi',
            '/v2/top-headlines',
            params={'category': 'technology', 'pageSize': 10},
            user=self.user
        )

@patch('services.views.APIClient.make_request')
class GitHubViewTests(BaseServiceIntegrationTest):
    def test_get_github_user_success(self, mock_make_request):
        mock_make_request.return_value = {'login': 'testuser', 'public_repos': 5}
        url = reverse('github-user') + '?username=testuser'
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        mock_make_request.assert_called_with(
            'github',
            '/users/testuser',
            user=self.user
        )

    def test_get_github_user_no_username(self, mock_make_request):
        url = reverse('github-user')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

@patch('services.views.APIClient.make_request')
class CoinGeckoViewsTests(BaseServiceIntegrationTest):
    def test_simple_price_success(self, mock_make_request):
        mock_make_request.return_value = {'bitcoin': {'usd': 50000}}
        url = reverse('simple-price') + '?ids=bitcoin&vs_currencies=usd'
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        mock_make_request.assert_called_with(
            'coingecko',
            '/simple/price',
            params={'ids': 'bitcoin', 'vs_currencies': 'usd'},
            user=self.user
        )

    def test_coin_detail_missing_param(self, mock_make_request):
        url = reverse('coin-info')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_coin_detail_success(self, mock_make_request):
        mock_make_request.return_value = {'id': 'bitcoin', 'name': 'Bitcoin'}
        url = reverse('coin-info') + '?id=bitcoin'
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        mock_make_request.assert_called_with(
            'coingecko',
            '/coins/bitcoin',
            user=self.user
        )

@patch('services.views.APIClient.make_request')
class ExchangeRateViewsTests(BaseServiceIntegrationTest):
    def test_exchange_rate_success(self, mock_make_request):
        mock_make_request.return_value = {'rates': {'USD': 1.0, 'EUR': 0.9}}
        url = reverse('exchanges-rate') + '?currency=USD'
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        mock_make_request.assert_called_with(
            'exchangeRate',
            '/latest/USD',
            user=self.user
        )

    def test_convert_currency_success(self, mock_make_request):
        mock_make_request.return_value = {'result': 118.5}
        url = reverse('pair') + '?from=USD&to=JPY&amount=1'
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        mock_make_request.assert_called_with(
            'exchangeRate',
            '/pair/USD/JPY/1',
            user=self.user
        )
