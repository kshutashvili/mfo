import os
import hashlib
from pprint import pprint
import json
import mimetypes
from os.path import basename

import requests

from django.conf import settings
from django.shortcuts import render
from django.http import (
    HttpResponseRedirect, JsonResponse,
    HttpResponseBadRequest, HttpResponse
)
from django.urls import reverse
from django.views.generic import View
from django.urls import reverse_lazy
from django.contrib.auth import (
    authenticate, login, logout, update_session_auth_hash
)
from django.contrib.auth.decorators import user_passes_test
from django.views.static import serve

from content.helpers import clear_contact_phone
from users.models import User
from users.helpers import make_user_password
from .models import ScanDocument
from .utils import (
    decrypt_data, load_scans, local_save, server_header
)

# Create your views here.


class BankidView(View):
    def get(self, *args, **kwargs):
        if 'code' not in self.request.GET:
            """
                first request to bankid
                response contain 'access_token'
                and 'refresh_token' values
                which will be used for requesting data

                after getting response, browser redirects
                to this view second time
            """

            # different domains for Dev and Prod
            if settings.DEBUG:
                domain = "bankid.privatbank.ua"  # dev domain
            else:
                domain = "bankid.org.ua"  # prod domain

            path = "DataAccessService/das/authorize"
            query = "response_type={type}&client_id={id}&redirect_uri={uri}".format(
                type='code',
                id=settings.BANKID_CLIENT_ID,
                uri='{0}://{1}/bankid/auth'.format(
                    'https' if self.request.is_secure() else 'http',  # schema
                    self.request.META['HTTP_HOST']  # domain
                )
            )
            url = "https://{domain}/{path}?{query}".format(
                domain=domain,
                path=path,
                query=query
            )

            return HttpResponseRedirect(url)

        code = self.request.GET.get('code', None)
        if code:
            """
                second request to bankid
                response contain 'code' value
                which will be used in next requests

                after getting response, browser redirects
                to the 'bankid:getdata' URL
            """
            if settings.DEBUG:
                domain = "bankid.privatbank.ua"  # dev domain
            else:
                domain = "biprocessing.org.ua"  # prod domain

            path = "DataAccessService/oauth/token"
            for_sha = "{0}{1}{2}".format(
                settings.BANKID_CLIENT_ID,  # client_id
                settings.BANKID_SECRET,  # secret
                code
            )
            url = "https://{domain}/{path}".format(
                domain=domain,
                path=path
            )
            params = {
                "grant_type": "authorization_code",
                "client_id": settings.BANKID_CLIENT_ID,
                "client_secret": hashlib.sha1(for_sha.encode()).hexdigest(),
                "code": code,
                "redirect_uri": "{0}://{1}/bankid/auth".format(
                    'https' if self.request.is_secure() else 'http',  # schema
                    self.request.META['HTTP_HOST']  # domain
                )
            }
            r = requests.get(
                url=url,
                params=params
            )
            json_resp = r.json()
            # pprint(json_resp)

            if 'error' in json_resp:
                # invalid data
                return HttpResponseRedirect('/')

            # print(json_resp['access_token'], json_resp['refresh_token'])
            # set tokens into session
            self.request.session['access_token'] = json_resp['access_token']
            self.request.session['refresh_token'] = json_resp['refresh_token']

            return HttpResponseRedirect(reverse('bankid:getdata'))


def bankid_refreshtokens(request):
    print("GET refreshtokens", request.GET)
    refresh_token = request.GET.get('refresh_token', None)
    if not refresh_token:
        return HttpResponseRedirect('/')

    domain = "bankid.privatbank.ua"
    path = "DataAccessService/oauth/token"
    for_sha = "{0}{1}{2}".format(
        settings.BANKID_CLIENT_ID,
        settings.BANKID_SECRET,
        refresh_token
    )
    query = "grant_type={type}&client_id={id}&client_secret={secret}&refresh_token={refresh_token}".format(
        type='refresh_token',
        id=settings.BANKID_CLIENT_ID,
        secret=hashlib.sha1(for_sha.encode()).hexdigest(),
        refresh_token=refresh_token
    )
    url = "https://{domain}/{path}?{query}".format(
        domain=domain,
        path=path,
        query=query
    )
    print(url)
    return HttpResponseRedirect(url)


def bankid_getdata(request):
    access_token = request.session.get('access_token', None)
    refresh_token = request.session.get('refresh_token', None)

    if settings.DEBUG:
        url = "https://bankid.privatbank.ua/ResourceService/checked/data"
    else:
        url = "https://biprocessing.org.ua/ResourceService/checked/data"

    headers = {
        "Content-Type": "application/json",
        "Authorization": "Bearer {access_token}, Id {client_id}".format(
            access_token=access_token,
            client_id=settings.BANKID_CLIENT_ID
        ),
        "Accept": "application/json"
    }

    # describe which data will be requested
    data = {
        "type": "physical",
        "fields": [
            "firstName", "middleName",
            "lastName", "phone",
            "inn", "clId",
            "clIdText", "birthDay",
            "email", "sex",
            "resident", "dateModification"
        ],
        "scans": [
            {
                "type": "passport",
                "fields": [
                    "link", "dateCreate",
                    "extension", "dateModification"
                ]
            },
            {
                "type": "zpassport",
                "fields": [
                    "link", "dateCreate",
                    "extension", "dateModification"
                ]
            },
            {
                "type": "inn",
                "fields": [
                    "link", "dateCreate",
                    "extension", "dateModification"
                ]
            },
            {
                "type": "personalPhoto",
                "fields": [
                    "link", "dateCreate",
                    "extension", "dateModification"
                ]
            }
        ],
        "addresses": [
            {
                "type": "factual",
                "fields": [
                    "country", "state",
                    "area", "city",
                    "street", "houseNo",
                    "flatNo", "dateModification"
                ]
            },
            {
                "type": "birth",
                "fields": [
                    "country", "state",
                    "area", "city",
                    "street", "houseNo",
                    "flatNo", "dateModification"
                ]
            }
        ],
        "documents": [
            {
                "type": "passport",
                "fields": [
                    "series", "number",
                    "issue", "dateIssue",
                    "dateExpiration", "issueCountryIso2",
                    "dateModification"
                ]
            },
            {
                "type": "zpassport",
                "fields": [
                    "series", "number",
                    "issue", "dateIssue",
                    "dateExpiration", "issueCountryIso2",
                    "dateModification"
                ]
            }
        ]
    }

    r = requests.post(
        url=url,
        headers=headers,
        data=json.dumps(data)
    )

    decrypted = decrypt_data(r.json())

    # load_scans(decrypted['customer']['scans'], headers)

    # check if user with this mobile_phone exists
    user_exists = User.objects.filter(
        mobile_phone=clear_contact_phone(
            decrypted["customer"]["phone"]
        )
    )
    if user_exists:
        return HttpResponseRedirect(reverse_lazy('login'))

    user = User.objects.create(
        mobile_phone=clear_contact_phone(decrypted["customer"]["phone"]),
        ready_for_turnes=False
    )
    # set user password, send SMS with it
    password = make_user_password(user)
    # authenticate user
    auth_user = authenticate(mobile_phone=user.mobile_phone, password=password)

    # save decrypted data to models:
    # Customer, Document, Address, ScanDocument
    # and copy this data to Questionnaire model
    local_save(decrypted, user, headers)

    if auth_user is not None:
        login(request, auth_user)
        return HttpResponseRedirect(reverse_lazy('questionnaire'))

    # return JsonResponse(
    #     json.dumps(
    #         decrypted
    #     ),
    #     safe=False
    # )
    return HttpResponseRedirect(reverse_lazy('main'))


@user_passes_test(lambda u: u.is_superuser)
def document_view(request, scan_id):
    scan = ScanDocument.objects.get(id=scan_id)
    response = HttpResponse()
    response.content = scan.file.read()
    response["Content-Type"] = "application/pdf"
    response["Content-Disposition"] = "inline; filename={0}".format(
        scan.file.name
    )
    return response
