import hashlib
from pprint import pprint
import json

import requests

from django.db.models import F

from .models import KeyFor4billAPI


def get_client_ip(request):
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip


def get_full_url(request, url_type):
    types = {
        "fail_url": "/pay/{0}/fail",
        "success_url": "/pay/{0}/success",
        "callback_url": "/pay/{0}/callback",
    }

    return "{0}://{1}{2}".format(
        request.META.get("wsgi.url_scheme"),
        request.META.get("HTTP_HOST"),
        types[url_type]
    )


class Provider4billAPI:

    def __init__(self, api_key, point, debug=False):
        self.API_KEY = api_key
        self.POINT = point
        self.DEBUG = debug
        self.LOCALE = "en"
        self.ENDPOINT = "https://api.4bill.io"

    def get_hash(self, point, api_key, key):
        """
            creating MD5 hash of string:
            point + api_key + key

            Example:
            point = 1
            api_key = ero3423hddff
            key = 1
            str_for_hash MUST be 1ero3423hddff1

            1ero3423hddff1 converts to: b448ac496663df24e6dda0e847bdf1fa
        """
        str_for_hashing = "{0}{1}{2}".format(point, api_key, key)
        return hashlib.md5(str_for_hashing.encode()).hexdigest()

    def get_key(self):
        # https://docs.4bill.io/#/docs/documentation-2
        key_object = KeyFor4billAPI.get_solo()
        return key_object.key

    def set_key(self):
        key_object = KeyFor4billAPI.get_solo()
        key_object.key += 1
        key_object.save()

    def transaction_create(self, request, payment_object):
        # incremented key value for request
        request_key = self.get_key()

        request_data = {
            "auth": {
                "debug": self.DEBUG,
                "point": self.POINT,
                "key": request_key,
                "hash": self.get_hash(self.POINT, self.API_KEY, request_key)
            },
            "locale": self.LOCALE,
            "external_customer_id": payment_object.user.id,  # user == request.user
            "external_order_id": payment_object.id,          # payment's ID from Payment model
            "account_id": payment_object.account_id,
            "wallet_id": payment_object.wallet_id,
            "service_id": payment_object.service_id,
            "customer_ip_address": payment_object.customer_ip_address,
            "amount": payment_object.amount,
            "amount_currency": payment_object.amount_currency,
            "point": {
                "success_url": get_full_url(request, "success_url").format(payment_object.id),
                "fail_url": get_full_url(request, "fail_url").format(payment_object.id),
                "callback_url": get_full_url(request, "callback_url").format(payment_object.id)
            }
        }

        # creating full API endpoint
        endpoint = "{0}/transaction/create".format(self.ENDPOINT)

        r = requests.post(
            endpoint,
            data=json.dumps(request_data),
            headers={"Content-Type": "application/json"}
        )

        self.set_key()

        return r.json()

    def transaction_find(self, payment_object):
        # incremented key value for request
        request_key = self.get_key()

        request_data = {
            "auth": {
                "debug": self.DEBUG,
                "point": self.POINT,
                "key": request_key,
                "hash": self.get_hash(self.POINT, self.API_KEY, request_key)
            },
            "locale": self.LOCALE,
            "id": payment_object.provider_transaction_id
        }

        # creating full API endpoint
        endpoint = "{0}/transaction/find".format(self.ENDPOINT)

        r = requests.post(
            endpoint,
            data=json.dumps(request_data),
            headers={"Content-Type": "application/json"}
        )

        self.set_key()

        return r.json()
