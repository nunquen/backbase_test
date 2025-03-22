from django.conf import settings
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    CurrencyConverterView,
    CurrencyHistoryRateView,
    CurrencyRateView,
    CurrencyViewSet,
    VersionView
)

router = DefaultRouter()
router.register(r'currency', CurrencyViewSet, basename="currency")

version = f'v{settings.PROJECT_VERSION.split(".")[0]}'
urlpatterns = [
    path(
        f'{version}/currency-rates/',
        CurrencyRateView.as_view(),
        name='currency-rates'
    ),
    path(
        f'{version}/currency-converter/',
        CurrencyConverterView.as_view(),
        name='currency-converter'
    ),
    path("", include(router.urls)),
    path("version/", VersionView.as_view(), name="version"),
    path(
        f'{version}/currency-history-rates/',
        CurrencyHistoryRateView.as_view(),
        name='currency-history-rates'
    ),
]
