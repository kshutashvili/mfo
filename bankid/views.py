import hashlib
import json

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

from content.helpers import clear_contact_phone
from users.models import User
from users.helpers import make_user_password
from .models import ScanDocument, BankIDLog
from .utils import (
    decrypt_data, local_save
)


class BankidView(View):
    def get(self, *args, **kwargs):
        """
            The first request (GET) to a bankid
            will return a response that contains
            'code' value which  will be used in
            a second request from this view.
            After getting a response, browser redirects
            to this view second time.

            Example of first request URL:
            https://bankid.org.ua/DataAccessService/das/authorize?
                response_type=code&
                client_id=b0f1d8f4-9775-49b4-b82f-807fbacc385a&
                redirect_uri=https://expressfinance.com.ua/bankid/auth


            The second request (GET/POST) to bankid
            will return a response that
            contains 'access_token' and 'refresh_token' values
            which will be used for requesting data.
            After getting a response, browser redirects
            to the 'bankid:getdata' URL

            Example of second request URL:
            https://bankid.org.ua/DataAccessService/oauth/token
            params:
            {
             'redirect_uri': 'https://expressfinance.com.ua/bankid/auth',
             'client_id': 'b0f1d8f4-9775-49b4-b82f-807fbacc385a',
             'client_secret': '8e6c439b90ae96ea5e2d7cbc882846eb1c86cb4040...',
             'code': 'opWX7B45588',
             'grant_type': 'authorization_code'
            }
        """
        BankIDLog.objects.create(
            type='BankIDView',
            subtype="GET",
            message=self.request.GET
        )

        if 'code' not in self.request.GET:
            # First request

            # different domains for Dev and Prod
            if settings.DEBUG:
                domain = "bankid.privatbank.ua"     # dev domain
            else:
                domain = "bankid.org.ua"            # prod domain

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

            BankIDLog.objects.create(
                type='BankIDView',
                subtype="URL",
                message=url
            )

            return HttpResponseRedirect(url)

        code = self.request.GET.get('code', None)

        BankIDLog.objects.create(
            type='BankIDView',
            subtype="Code",
            message=code
        )

        if code:
            # Second request
            if settings.DEBUG:
                domain = "bankid.privatbank.ua"     # dev domain
            else:
                domain = "bankid.org.ua"            # prod domain

            path = "DataAccessService/oauth/token"
            for_sha = "{0}{1}{2}".format(
                settings.BANKID_CLIENT_ID,          # client_id
                settings.BANKID_SECRET,             # secret
                code
            )

            BankIDLog.objects.create(
                type='BankIDView',
                subtype="for SHA",
                message=for_sha
            )
            url = "https://{domain}/{path}".format(
                domain=domain,
                path=path
            )
            BankIDLog.objects.create(
                type='BankIDView',
                subtype="URL",
                message=url
            )
            params = {
                "grant_type": "authorization_code",
                "client_id": settings.BANKID_CLIENT_ID,
                "client_secret": hashlib.sha512(for_sha.encode()).hexdigest(),
                "code": code,
                "redirect_uri": "{0}://{1}/bankid/auth".format(
                    'https' if self.request.is_secure() else 'http',  # schema
                    self.request.META['HTTP_HOST']  # domain
                )
            }

            BankIDLog.objects.create(
                type='Request',
                subtype="PARAMS",
                message=params
            )
            try:
                r = requests.get(
                    url=url,
                    params=params
                )
            except Exception as e:
                BankIDLog.objects.create(
                    type='Request',
                    subtype="Request Error",
                    message=e
                )
            try:
                json_resp = r.json()
            except Exception as e:
                BankIDLog.objects.create(
                    type='BankIDGetData',
                    subtype="json_resp Error",
                    message=e
                )

            BankIDLog.objects.create(
                type='BankIDGetData',
                subtype="response text",
                message=r.text
            )

            if 'error' in json_resp:
                # invalid data
                return HttpResponseRedirect('/')

            # set tokens into session
            self.request.session['access_token'] = json_resp['access_token']
            self.request.session['refresh_token'] = json_resp['refresh_token']

            return HttpResponseRedirect(reverse('bankid:getdata'))
        else:
            # GET request with code=None
            return HttpResponseBadRequest()


def bankid_refreshtokens(request):
    print("GET refreshtokens", request.GET)
    refresh_token = request.GET.get('refresh_token', None)
    if not refresh_token:
        return HttpResponseRedirect('/')

    if settings.DEBUG:
        domain = "bankid.privatbank.ua"     # dev domain
    else:
        domain = "bankid.org.ua"            # prod domain
    path = "DataAccessService/oauth/token"
    for_sha = "{0}{1}{2}".format(
        settings.BANKID_CLIENT_ID,
        settings.BANKID_SECRET,
        refresh_token
    )
    query = "grant_type={type}&client_id={id}&client_secret={secret}&refresh_token={refresh_token}".format(
        type='refresh_token',
        id=settings.BANKID_CLIENT_ID,
        secret=hashlib.sha512(for_sha.encode()).hexdigest(),
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
    """
        Function gets encoded data from BankID,
        decode it and save into models
    """
    access_token = request.session.get('access_token', None)  # pop
    refresh_token = request.session.get('refresh_token', None)  # pop
    BankIDLog.objects.create(
        type='BankIDGetData',
        subtype="access_token",
        message=access_token
    )
    BankIDLog.objects.create(
        type='BankIDGetData',
        subtype="refresh_token",
        message=refresh_token
    )

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

    # Describe which data will be requested
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

    BankIDLog.objects.create(
        type='BankIDGetData',
        subtype="request headers",
        message=headers
    )
    BankIDLog.objects.create(
        type='BankIDGetData',
        subtype="request data",
        message=json.dumps(data)
    )
    BankIDLog.objects.create(
        type='BankIDGetData',
        subtype="request URL",
        message=url
    )

    r = requests.post(
        url=url,
        headers=headers,
        data=json.dumps(data)
    )

    BankIDLog.objects.create(
        type='BankIDGetData',
        subtype="response",
        message=r.json()
    )

    response_json = r.json()
    if 'customer' in response_json.keys():
        decrypted = decrypt_data(response_json)
    else:
        BankIDLog.objects.create(
            type='BankIDGetData',
            subtype="error",
            message="response not contain 'customer' key"
        )
        return HttpResponseRedirect(reverse_lazy('main'))

    BankIDLog.objects.create(
        type='BankIDGetData',
        subtype="decrypted",
        message=decrypted
    )

    # Check if user with this mobile_phone exists
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
    # Set user password, send SMS with it
    password = make_user_password(user)
    # Authenticate user
    auth_user = authenticate(mobile_phone=user.mobile_phone, password=password)

    # Save decrypted data to models:
    # Customer, Document, Address, ScanDocument
    # and copy this data to Questionnaire model
    local_save(decrypted, user, headers)

    if auth_user is not None:
        login(request, auth_user)
        return HttpResponseRedirect(reverse_lazy('questionnaire'))

    return HttpResponseRedirect(reverse_lazy('main'))


@user_passes_test(lambda u: u.is_superuser)
def document_view(request, scan_id):
    """
    Preview document's scan;
    only for superusers
    """
    scan = ScanDocument.objects.get(id=scan_id)
    response = HttpResponse()
    response.content = scan.file.read()
    response["Content-Type"] = "application/pdf"
    response["Content-Disposition"] = "inline; filename={0}".format(
        scan.file.name
    )
    return response
