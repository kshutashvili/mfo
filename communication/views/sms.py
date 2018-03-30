# Download the Python helper library from twilio.com/docs/python/install
from random import randint

from twilio.rest import Client
from authy.api import AuthyApiClient

from django.urls import reverse
from django.http.response import HttpResponseRedirect
from django.http import Http404
from django.template.loader import get_template, render_to_string
from django.shortcuts import render_to_response, redirect, render
from django.utils.translation import ugettext_lazy as _
from django.contrib.sites.shortcuts import get_current_site
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_text
from django.core.mail import EmailMessage, EmailMultiAlternatives
from django.contrib.auth.models import User

# Your Account Sid and Auth Token from twilio.com/user/account
from efin.settings import TWILIO_ACCOUNT_SID as account_sid
from efin.settings import TWILIO_AUTH_TOKEN as auth_token
from efin.settings import AUTHY_API_KEY as auth_token
from efin.settings import ADMIN_EMAIL

from users.models import Profile
from token_confirm.models import Token
from token_confirm.token import account_activation_token


api = AuthyApiClient(auth_token)

def sms(request, phone):
    request.session['phone'] = phone
    res = api.phones.verification_start(phone, '+380', via='sms')
    return HttpResponseRedirect(reverse('verify'))


def verify(request):
    if request.method == 'POST':
        phone = request.session.get('phone','')
        profile = Profile.objects.filter(phone=phone).first()
        if not profile:
            profile = Profile.objects.filter(user=request.user).first()
        if not profile:
            raise Http404()
        else:
            code = request.POST.get('code','')
            verification = api.phones.verification_check(phone, '+380', code)
            if verification.ok():
                profile.user.is_active = True
                profile = Profile.objects.filter(user=request.user).first()
                profile.phone = phone
                request.user.username = phone
                profile.save()
                request.user.save()
                return HttpResponseRedirect(reverse('profile'))
            else:
                return render(request, 'enter-sms.html', {'status_message':_('Неправильный код')})
    elif request.method == 'GET':
        return render(request, 'enter-sms.html', {})


def random_code(n):
    range_start = 10**(n-1)
    range_end = (10**n)-1
    return randint(range_start, range_end)


def change_email(request):
    subject = 'Express Finance: смена почты'
    to_email = request.session.get('email')
    site = get_current_site(request)
    token = account_activation_token.make_token(request.user)
    token_db = Token.objects.filter(token=token).first()
    if not token_db:
        token_db = Token()
        token_db.token = token
        token_db.save()

    uid = str(urlsafe_base64_encode(force_bytes(request.user.pk))).split("'")[1]
    data ={'site':site,
           'uid':uid,
           'token':token}

    template = get_template('email/change.html')
    message = template.render(data)
    msg = EmailMultiAlternatives(subject, message, ADMIN_EMAIL, [to_email])
    msg.attach_alternative(message, "text/html")
    msg.mixed_subtype = 'related'
    try:
        msg.send()
    except:
        print('Errooooooooooooooooooooooooooooooooooooooooor')
    return render(request, 'email/sended.html', {})


def email_confirm(request, uidb64, token):
    try:
        uid = force_text(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
    except(TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None
    if user is not None and account_activation_token.check_token(user, token):
        token_db = Token.objects.filter(token=token).first()
        if token_db:
            request.user.email = request.session.get('email')
            request.user.save()
            token_db.delete()
            return render(request, 'email/changed.html', {})
        else:
            return render(request, 'email/link_invalid.html', {})
    else:
        return render(request, 'email/link_invalid.html', {})