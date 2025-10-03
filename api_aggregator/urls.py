from django.urls import path, include
from services.views import (
    UnifiedWeatherView,
    UnifiedNewsView,
    GitHubUserInfoView,
    CGSimplePriceView,
    CGCoinDetailView,
    CGSearchView,
    CGCoinMarketChartView,
    CGHistoryCoinView,
    CGSearchTrendingView,
)
from user.views import RegisterView, CreateUserAPIKey
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
    TokenVerifyView,
)

urlpatterns = [
    path('api/weather/', UnifiedWeatherView.as_view(), name='unified-weather'),
    path('api/news/', UnifiedNewsView.as_view(), name='unified-news'),
    path('api/github/user/', GitHubUserInfoView.as_view(), name='github-user'),
    path('api/simple/price/', CGSimplePriceView.as_view(), name='simple-price'),
    path('api/coins/', CGCoinDetailView.as_view(), name='coin-info'),
    path('api/coins/market_chart/', CGCoinMarketChartView.as_view(), name='coins-market-chart'),
    path('api/coins/history/', CGHistoryCoinView.as_view(), name='coins-history'),
    path('api/search/', CGSearchView.as_view(), name='search'),
    path('api/search/trending/', CGSearchTrendingView.as_view(), name='search-trending'),

    path("api/register/", RegisterView.as_view(), name="register_user"),
    path("api/token/", TokenObtainPairView.as_view(), name="token_obtain_pair"),
    path("api/token/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
    path("api/token/verify/", TokenVerifyView.as_view(), name="token_verify"),
    path("api/create-api-key/", CreateUserAPIKey.as_view(), name="create-api-key"),
]
