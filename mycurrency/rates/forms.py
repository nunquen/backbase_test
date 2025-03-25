from django import forms
from .models import Currency


class CurrencyConverterForm(forms.Form):
    source_currency = forms.ModelChoiceField(
        queryset=Currency.objects.all(), label="Source Currency"
    )
    exchanged_currency = forms.ModelMultipleChoiceField(
        queryset=Currency.objects.all(),
        label="Exchanged Currencies",
        widget=forms.CheckboxSelectMultiple,
    )
    amount = forms.DecimalField(label="Amount", min_value=0.01)
