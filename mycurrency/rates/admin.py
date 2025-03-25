from django.contrib import admin
from .models import BatchProcess, Currency, CurrencyExchangeRate, Provider


# Register the model
admin.site.register(Currency)
admin.site.register(CurrencyExchangeRate)
admin.site.register(Provider)
admin.site.register(BatchProcess)
