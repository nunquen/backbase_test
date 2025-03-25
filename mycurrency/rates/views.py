from decimal import Decimal
import logging
from asgiref.sync import sync_to_async
from adrf.views import APIView
from django.conf import settings
from django.shortcuts import render
from rest_framework.response import Response
from rest_framework import serializers, status, viewsets

from .adapters.serializers import CurrencySerializer
from .lib.utils import validate_date
from .models import Currency
from .service.rater import get_exchange_rates, get_exchange_convertion
from .service.batch_processor import batch_process
from .forms import CurrencyConverterForm


logger = logging.getLogger(__name__)


class CurrencyConversionQuerySerializer(serializers.Serializer):
    source_currency = serializers.CharField(required=True, max_length=3)
    exchanged_currency = serializers.CharField(required=True, max_length=3)
    amount = serializers.DecimalField(
        required=True, max_digits=12, decimal_places=2, min_value=Decimal("0.01")
    )


class CurrencyConverterView(APIView):
    """
    API View to retrieve real time currency convertion for an specific amount.
    """

    def get(self, request, **kwargs):
        version = kwargs.get("version")
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
        source_currency = validated_data["source_currency"]
        exchanged_currency = validated_data["exchanged_currency"]
        amount = validated_data["amount"]

        logger.info(
            "Currency Convertion {} requested for {}, from {} to {}".format(
                version, source_currency, exchanged_currency, amount
            )
        )

        # - retrieve all currencies and check if source_currency exists
        valid_currencies = set(Currency.objects.values_list("code", flat=True))
        if source_currency not in valid_currencies:
            return Response(
                {"error": f"Invalid source_currency: {source_currency}"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if exchanged_currency not in valid_currencies:
            return Response(
                {"error": f"Invalid exchanged_currency: {exchanged_currency}"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            convertion_rate = get_exchange_convertion(
                source_currency=source_currency,
                exchanged_currency=exchanged_currency,
                amount=amount,
            )
            return Response(convertion_rate, status=status.HTTP_200_OK)

        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)


class CurrencyRateView(APIView):
    """
    API View to retrieve currency rates for a particular time range.
    """

    def get(self, request, **kwargs):
        version = kwargs.get("version")
        source_currency = request.GET.get("source_currency")
        date_from = request.GET.get("date_from")
        date_to = request.GET.get("date_to")
        logger.info(
            "Currency Rates {} requested for {}, from {} to {}".format(
                version, source_currency, date_from, date_to
            )
        )

        # - retrieve all currencies and check if source_currency exists
        valid_currencies = set(Currency.objects.values_list("code", flat=True))
        if source_currency not in valid_currencies:
            return Response(
                {"error": f"Invalid source_currency: {source_currency}"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        # - check dates format to be "%Y-%m-%d"
        date_from_parsed, error_response = validate_date(
            date_str=date_from, field_name="date_from"
        )
        if error_response:
            return error_response

        date_to_parsed, error_response = validate_date(
            date_str=date_to, field_name="date_to"
        )
        if error_response:
            return error_response

        if date_from_parsed > date_to_parsed:
            return Response(
                {"error": "Invalid date range"}, status=status.HTTP_400_BAD_REQUEST
            )

        try:
            rate_values = get_exchange_rates(
                source_currency=source_currency,
                date_from=date_from_parsed,
                date_to=date_to_parsed,
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
            {"version": settings.PROJECT_VERSION}, status=status.HTTP_200_OK
        )


class CurrencyHistoryRateView(APIView):
    """
    API View to asynchronously retrieve currency rates for a particular time range.
    """

    async def post(self, request, **kwargs):
        version = kwargs.get("version")
        date_from = request.data.get("date_from")
        date_to = request.data.get("date_to")
        source_currency = request.data.get("source_currency")
        logger.info(
            "Currency Historical Rates {} requested for {}, from {} to {}".format(
                version, source_currency, date_from, date_to
            )
        )
        # - retrieve all currencies and check if source_currency exists
        valid_currencies = await sync_to_async(
            lambda: set(Currency.objects.values_list("code", flat=True)),
            thread_sensitive=True,
        )()
        if source_currency not in valid_currencies:
            return Response(
                {"error": f"Invalid source_currency: {source_currency}"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        # - check dates format to be "%Y-%m-%d"
        date_from_parsed, error_response = validate_date(
            date_str=date_from, field_name="date_from"
        )
        if error_response:
            return error_response

        date_to_parsed, error_response = validate_date(
            date_str=date_to, field_name="date_to"
        )
        if error_response:
            return error_response

        if date_from_parsed > date_to_parsed:
            return Response(
                {"error": "Invalid date range"}, status=status.HTTP_400_BAD_REQUEST
            )
        try:
            process_id = await batch_process(
                source_currency=source_currency,
                valid_currencies=valid_currencies,
                date_from=date_from_parsed,
                date_to=date_to_parsed,
            )
            response_body = {
                "process_id": str(process_id),
            }
            return Response(response_body, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)


def Converter(request, **kwargs):
    version = kwargs.get("version")
    conversion_results = []
    error = None
    if request.method == "POST":
        form = CurrencyConverterForm(request.POST)
        if form.is_valid():
            # Process the form data
            source_currency = form.cleaned_data["source_currency"]
            exchanged_currencies = form.cleaned_data["exchanged_currency"]
            amount = form.cleaned_data["amount"]

            logger.info(
                "Converter {} requested for {} to {} with amount of {}".format(
                    version,
                    source_currency.code,
                    ",".join([currency.code for currency in exchanged_currencies]),
                    amount,
                )
            )
            try:
                for exchanged_currency in exchanged_currencies:
                    convertion_rate = get_exchange_convertion(
                        source_currency=source_currency.code,
                        exchanged_currency=exchanged_currency.code,
                        amount=amount,
                    )
                    conversion_results.append(convertion_rate)
            except Exception as e:
                error = str(e)

    else:
        form = CurrencyConverterForm()

    context = {"form": form, "conversion_results": conversion_results, "error": error}
    return render(request=request, template_name="base/form.html", context=context)
