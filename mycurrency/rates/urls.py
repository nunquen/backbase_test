from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import CurrencyRateView, CurrencyViewSet, VersionView

router = DefaultRouter()
router.register(r'currency', CurrencyViewSet, basename="currency")

urlpatterns = [
    path('currency-rates/', CurrencyRateView.as_view(), name='currency-rates'),
    path("", include(router.urls)),
    path("version/", VersionView.as_view(), name="version"),
]
