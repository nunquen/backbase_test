from django.contrib import admin
from .models import Provider, Currency, CurrencyExchangeRate


# Register the model
admin.site.register(Currency)
admin.site.register(CurrencyExchangeRate)
admin.site.register(Provider)
