# Download the Python helper library from twilio.com/docs/python/install
from random import randint

from twilio.rest import Client
from authy.api import AuthyApiClient

from django.urls import reverse
from django.http.response import HttpResponseRedirect
from django.http import Http404
from django.shortcuts import render_to_response, redirect, render
from django.utils.translation import ugettext_lazy as _

# Your Account Sid and Auth Token from twilio.com/user/account
from efin.settings import TWILIO_ACCOUNT_SID as account_sid
from efin.settings import TWILIO_AUTH_TOKEN as auth_token
from efin.settings import AUTHY_API_KEY as auth_token

from users.models import Profile
from users.views import clear_phone


api = AuthyApiClient(auth_token)

def sms(request, phone):
    # client = Client(account_sid, auth_token)
    # code = random_code(6)
    phone = clear_phone(phone)
    request.session['phone'] = phone
    # user = Profile.objects.filter(phone=phone).first()
    # user.verify_code = str(code)
    # user.save()

    api.phones.verification_start(phone, '+380', via='sms')

#    message = client.messages.create(to=phone,
#                                     body=''.join(["Ваш код подтверждения: ", str(code)]),
#                                     from_="+18034085480")
    return HttpResponseRedirect(reverse('verify'))


def verify(request):
    if request.method == 'POST':
        phone = request.session.get('phone','')
        user = Profile.objects.filter(phone=phone).first()
        if not user:
            raise Http404()
        else:
            code = request.POST.get('code','')
            verification = api.phones.verification_check(phone, '+380', code)
            if verification.ok():
                user.user.is_active = True
                user.user.save()
                return HttpResponseRedirect(reverse('main'))
            else:
                return render(request, 'enter-sms.html', {'status_message':_('Неправильный код')})
    elif request.method == 'GET':
        return render(request, 'enter-sms.html', {})


def random_code(n):
    range_start = 10**(n-1)
    range_end = (10**n)-1
    return randint(range_start, range_end)

