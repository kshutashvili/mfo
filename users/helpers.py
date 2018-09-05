from twilio.rest import Client

from django.utils.crypto import get_random_string
from django.conf import settings

from content.helpers import clear_contact_phone


def make_user_password(user_obj):
    new_user_password = get_random_string(length=8)
    user_obj.set_password(new_user_password)
    user_obj.save()

    client = Client(
        settings.TWILIO_ACCOUNT_SID,
        settings.TWILIO_AUTH_TOKEN
    )
    message = client.messages.create(
        body="Ваш пароль на сайте expressfinance.com.ua: {0}".format(new_user_password),
        from_=settings.TWILIO_PHONE_NUMBER,
        # to="+{0}".format("380950968326")
        to="+{0}".format(clear_contact_phone(user_obj.mobile_phone))
    )
    return new_user_password


def send_password(to, password):
    client = Client(
        settings.TWILIO_ACCOUNT_SID,
        settings.TWILIO_AUTH_TOKEN
    )
    message = client.messages.create(
        body="Ваш пароль на сайте exf.in.ua: {0}".format(password),
        from_=settings.TWILIO_PHONE_NUMBER,
        # to="+380631280489"
        to="+{0}".format(to)
    )
    if message.sid:
        return message.sid
