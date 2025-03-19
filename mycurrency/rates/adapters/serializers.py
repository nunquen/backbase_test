from rest_framework import serializers
from ..models import CurrencyExchangeRate, Currency


class CurrencyExchangeRateSerializer(serializers.ModelSerializer):
    source_currency = serializers.SerializerMethodField()
    exchanged_currency = serializers.SerializerMethodField()
    valuation_date = serializers.SerializerMethodField()
    rate_value = serializers.SerializerMethodField()

    class Meta:
        model = CurrencyExchangeRate
        # fields = '__all__'
        fields = ['source_currency', 'exchanged_currency', 'valuation_date', 'rate_value']

    def get_source_currency(self, obj):
        # Returns the currency code for source_currency
        return obj.source_currency.code

    def get_exchanged_currency(self, obj):
        # Returns the currency code for exchanged_currency
        return obj.exchanged_currency.code

    def get_valuation_date(self, obj):
        return obj.valuation_date if type(obj.valuation_date) == str else obj.valuation_date.strftime("%Y-%m-%d")

    def get_rate_value(self, obj):
        return float(obj.rate_value)


class CurrencySerializer(serializers.ModelSerializer):
    class Meta:
        model = Currency
        fields = "__all__"
