from django.conf import settings
from django.urls import re_path, path, include
from rest_framework.routers import DefaultRouter
from .views import (
    CurrencyConverterView,
    CurrencyHistoryRateView,
    CurrencyRateView,
    CurrencyViewSet,
    VersionView,
    Converter
)

router = DefaultRouter()
router.register(r'currency', CurrencyViewSet, basename="currency")

version = f'v{settings.PROJECT_VERSION.split(".")[0]}'
urlpatterns = [
    re_path(
        r'^(?P<version>(v1|v2))/currency-rates/$',
        CurrencyRateView.as_view(),
        name='currency-rates'
    ),
    re_path(
        r'^(?P<version>(v1|v2))/currency-converter/',
        CurrencyConverterView.as_view(),
        name='currency-converter'
    ),
    path("", include(router.urls)),
    path("version/", VersionView.as_view(), name="version"),
    re_path(
        r'^(?P<version>(v2))/currency-history-rates/',
        CurrencyHistoryRateView.as_view(),
        name='currency-history-rates'
    ),
    path('converter/', Converter, name='converter'),
]
