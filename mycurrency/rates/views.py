from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import serializers, status, viewsets
from django.conf import settings

import logging

from .adapters.serializers import CurrencyExchangeRateSerializer, CurrencySerializer
from .lib.utils import validate_date
from .models import Currency
from .service.rater import get_exchange_rates, get_exchange_convertion
from decimal import Decimal

logger = logging.getLogger(__name__)


class CurrencyConversionQuerySerializer(serializers.Serializer):
    source_currency = serializers.CharField(required=True, max_length=3)
    exchanged_currency = serializers.CharField(required=True, max_length=3)
    amount = serializers.DecimalField(
        required=True,
        max_digits=12,
        decimal_places=2,
        min_value=Decimal("0.01")
    )


class CurrencyConverterView(APIView):
    """
    API View to retrieve real time currency convertion for an specific amount.
    """

    def get(self, request):
        data = request.query_params.copy()
        if "amount" in data:
            try:
                data["amount"] = float(data["amount"])
            except Exception:
                data["amount"] = ""

        serializer = CurrencyConversionQuerySerializer(data=data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        validated_data = serializer.validated_data
        source_currency = validated_data['source_currency']
        exchanged_currency = validated_data['exchanged_currency']
        amount = validated_data['amount']

        logger.info("Currency Convertion requested for {}, from {} to {}".format(
            source_currency,
            exchanged_currency,
            amount
        ))

        # - retrieve all currencies and check if source_currency exists
        valid_currencies = set(Currency.objects.values_list("code", flat=True))
        if source_currency not in valid_currencies:
            return Response(
                {"error": f"Invalid source_currency: {source_currency}"},
                status=status.HTTP_400_BAD_REQUEST
            )

        if exchanged_currency not in valid_currencies:
            return Response(
                {"error": f"Invalid exchanged_currency: {exchanged_currency}"},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            convertion_rate = get_exchange_convertion(
                source_currency=source_currency,
                exchanged_currency=exchanged_currency,
                amount=amount
            )
            return Response(convertion_rate, status=status.HTTP_200_OK)

        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)


class CurrencyRateView(APIView):
    """
    API View to retrieve currency rates for a particular time range.
    """

    def get(self, request):
        source_currency = request.GET.get("source_currency")
        date_from = request.GET.get("date_from")
        date_to = request.GET.get("date_to")
        logger.info("Currency Rates requested for {}, from {} to {}".format(
            source_currency,
            date_from,
            date_to
        ))

        # - retrieve all currencies and check if source_currency exists
        valid_currencies = set(Currency.objects.values_list("code", flat=True))
        if source_currency not in valid_currencies:
            return Response(
                {"error": f"Invalid source_currency: {source_currency}"},
                status=status.HTTP_400_BAD_REQUEST
            )
        # - check dates format to be "%Y-%m-%d"
        date_from_parsed, error_response = validate_date(date_str=date_from, field_name="date_from")
        if error_response:
            return error_response

        date_to_parsed, error_response = validate_date(date_str=date_to, field_name="date_to")
        if error_response:
            return error_response

        if date_from_parsed > date_to_parsed:
            return Response(
                {"error": "Invalid date range"},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            rate_values = get_exchange_rates(
                source_currency=source_currency,
                date_from=date_from_parsed,
                date_to=date_to_parsed
            )

            # serializer = CurrencyExchangeRateSerializer(rate_values, many=True)
            return Response(rate_values, status=status.HTTP_200_OK)

        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)


class CurrencyViewSet(viewsets.ModelViewSet):
    """CRUD API for Currency model"""
    queryset = Currency.objects.all()
    serializer_class = CurrencySerializer


class VersionView(APIView):
    def get(self, request):
        return Response(
            {"version": settings.PROJECT_VERSION},
            status=status.HTTP_200_OK
        )
