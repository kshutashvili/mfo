from pprint import pprint
from django.shortcuts import render
from django.http import (HttpResponse,
                         HttpResponseRedirect,
                         HttpResponseBadRequest)
from django.conf import settings
from django.contrib.auth import get_user_model
from django.urls import reverse

from .forms import PayForm, PaymentForm
from .models import Payment
from .utils import get_client_ip, Provider4billAPI


User = get_user_model()


def create_payment(request):
    if request.method == 'POST':
        pay_form = PayForm(request.POST)
        if pay_form.is_valid():

            # creating new Payment using ModelForm
            payment_form = PaymentForm(data={
                'account_id': settings.PROVIDER_4BILL_ACCOUNT,
                'wallet_id': settings.PROVIDER_4BILL_WALLET,
                'service_id': settings.PROVIDER_4BILL_SERVICE,
                'customer_ip_address': get_client_ip(request),
                'tpp_id': pay_form.cleaned_data["tpp_id"],
                'amount': float(pay_form.cleaned_data["pay_amount"]) * 100,  # amount in kopeks
                'description': "Пользователь: {0}\n№ договора: {1}\nСумма: {2}".format(
                    request.user.id,
                    pay_form.cleaned_data["contract_num"],
                    pay_form.cleaned_data["pay_amount"]
                ),
                'status': Payment.NEW
            })

            if payment_form.is_valid():

                # setting current user as payer
                payment_obj = payment_form.save(commit=False)
                payment_obj.user = request.user
                payment_obj.save()

                api = Provider4billAPI(
                    point=settings.PROVIDER_4BILL_POINT,
                    api_key=settings.PROVIDER_4BILL_API_KEY,
                    debug=settings.DEBUG
                )
                # creating transaction on 4bill
                provider_transaction = api.transaction_create(
                    request,
                    payment_obj
                )

                # if request is successfull
                if provider_transaction["error"]["code"] == 0:
                    # save transaction ID from 4bill
                    payment_obj.provider_transaction_id = provider_transaction["response"]["id"]
                    payment_obj.save()

                    # redirect user to 4bill form for confirm pay
                    return HttpResponseRedirect(
                        provider_transaction["response"]["result"]["pay_url"]
                    )
                else:
                    # set fail status
                    payment_obj.status = Payment.FAILED
                    payment_obj.save()

                    return HttpResponseRedirect(
                        reverse("profile")
                    )
        return HttpResponseRedirect(
            reverse("profile")
        )
    return HttpResponseBadRequest()


def success_payment(request, payment_id):
    """
        updating transaction status
    """
    Payment.objects.filter(id=payment_id).update(
        status=Payment.SUCCESS,
        is_paid=True
    )
    return HttpResponseRedirect(
        reverse("profile")
    )


def fail_payment(request, payment_id):
    """
        updating transaction status
    """
    Payment.objects.filter(id=payment_id).update(status=Payment.FAILED)
    return HttpResponseRedirect(
        reverse("profile")
    )


def callback_payment(request, payment_id):
    statuses = {
        "0": Payment.NEW,
        "1": Payment.SUCCESS,
        "2": Payment.FAILED,
        "3": Payment.CANCELLED,
        "4": Payment.REVERSED,
        "5": Payment.EXPIRED,
    }

    payment = Payment.objects.filter(
        id=payment_id
    )[0]
    if not payment:
        return HttpResponse()

    api = Provider4billAPI(
        point=settings.PROVIDER_4BILL_POINT,
        api_key=settings.PROVIDER_4BILL_API_KEY,
        debug=settings.DEBUG
    )
    # find transaction and get its status
    provider_transaction = api.transaction_find(payment)

    if provider_transaction["error"]["code"] == 0:
        # if status == NEW (status == 0) nothing do
        if provider_transaction["response"]["status"] == 0:
            return HttpResponse()
        else:
            # try get status name by code
            # if its raises error (status > 5)
            # then set PENDING status
            try:
                current_pay_status = statuses[str(provider_transaction["response"]["status"])]
                payment.status = current_pay_status
                if current_pay_status == Payment.SUCCESS:
                    payment.is_paid = True
                payment.save()
            except Exception:
                payment.status = Payment.PENDING
                payment.save()
    return HttpResponse()
