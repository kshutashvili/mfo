from twilio.rest import Client

from django.utils.crypto import get_random_string

from users.models import RequestPersonalArea, User
from content.helpers import clear_contact_phone


def make_user_password(user_obj):
    new_user_password = get_random_string(length=8)
    user_obj.set_password(new_user_password)
    user_obj.save()

    # phonxis twilio account
    account_sid = "AC37cb13a1d11a145f195479dfc148253b"
    auth_token = "8893689c10c3f0204f39c18d6dac4be3"
    twilio_phone = "+19132760090"

    # main twilio account
    # account_sid = "ACbe26b6146caf3657c7133a88dc0873e4"
    # auth_token = "e2d909069a7d4c5bd0f9e2064a3bbf43"
    # twilio_phone = "+17083406754"

    client = Client(account_sid, auth_token)
    message = client.messages.create(
        body="Ваш пароль на сайте expressfinance.com.ua: {0}".format(new_user_password),
        from_=twilio_phone,
        # to="+{0}".format(clear_contact_phone(user_obj.mobile_phone))
        to="+{0}".format("380950968326")
    )
    print("new_user_password", new_user_password)
    return new_user_password
