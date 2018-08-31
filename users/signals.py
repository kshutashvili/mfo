from twilio.rest import Client

from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils.crypto import get_random_string
from django.conf import settings

from users.models import RequestPersonalArea, User
from content.helpers import clear_contact_phone


# @receiver(post_save, sender=RequestPersonalArea)
def create_user_after_request(sender, instance, **kwargs):
    if instance.turnes_person_id:
        new_user = User.objects.create(
            first_name=instance.name,
            mobile_phone=clear_contact_phone(instance.mobile_phone_number),
            turnes_person_id=instance.turnes_person_id
        )
        new_user_password = get_random_string(length=8)
        print("new_user_password", new_user_password)
        new_user.set_password(new_user_password)
        new_user.save()

        # phonxis twilio account
        # account_sid = "AC37cb13a1d11a145f195479dfc148253b"
        # auth_token = "8893689c10c3f0204f39c18d6dac4be3"
        # twilio_phone = "+19132760090"

        # main twilio account
        account_sid = "AC37cb13a1d11a145f195479dfc148253b"
        auth_token = "8893689c10c3f0204f39c18d6dac4be3"
        twilio_phone = "+19132760090"

        client = Client(
            settings.TWILIO_ACCOUNT_SID,
            settings.TWILIO_AUTH_TOKEN
        )
        message = client.messages.create(
            body="Ваш пароль на сайте exf.in.ua: {0}".format(new_user_password),
            from_=settings.TWILIO_PHONE_NUMBER,
            # to="+{0}".format(clear_contact_phone(instance.mobile_phone_number))
            to="+380631280489"
        )

        # print(message.sid)
