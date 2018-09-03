from django import forms
from django.utils.translation import ugettext_lazy as _

from .models import Payment, PaymentPrivat


class PayForm(forms.Form):
    contract_num = forms.CharField(
        label=_("№ договора"),
        max_length=128,
        widget=forms.HiddenInput()
    )
    pay_amount = forms.DecimalField(
        label=_("Сумма платежа"),
        widget=forms.HiddenInput()
    )
    tpp_id = forms.IntegerField(
        label=_("tpp ID"),
        widget=forms.HiddenInput()
    )


class PaymentForm(forms.ModelForm):
    class Meta:
        model = Payment
        fields = (
            'account_id',
            'wallet_id',
            'service_id',
            'customer_ip_address',
            'amount',
            'description',
            'status',
            'tpp_id'
        )


class PaymentPrivatForm(forms.ModelForm):
    class Meta:
        model = PaymentPrivat
        fields = (
            'amount',
            'contract_num',
            'tpp_id'
        )
