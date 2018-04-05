from decimal import Decimal

from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from django.http.response import HttpResponseBadRequest, HttpResponse
from django.conf import settings
from django.db import transaction

from payment_gateways.utils import process_pb_request
from payment_gateways.models import Tcredits, Tpersons, Tcash


@csrf_exempt
@require_POST
def pb_terminal_view(request):

    is_valid, action, xml_data = process_pb_request(request)

    if not is_valid:
        return HttpResponseBadRequest("Операция не поддерживается")

    if action == "Search":
        data = xml_data['Transfer']['Data']
        contract_num = data['Unit']['@value']

        try:
            credit = Tcredits.objects.get(contract_num=contract_num)
            client_qs = Tpersons.objects.filter(id=credit.client_id)

            if client_qs:
                client = client_qs[0]
                client_fio = "{0} {1}. {2}.".format(
                    client.name3,
                    client.name[0].upper(),
                    client.name2[0].upper(),
                )
            else:
                resp = render(
                    request,
                    "payment_gateways/pb_response_search_error.xml",
                    {"error_msg": "Клиент не найден"},
                    content_type="application/xml"
                )

            resp = render(
                request,
                "payment_gateways/pb_response_search_success.xml",
                {
                    "contract_num": contract_num,
                    "service_code": settings.PB_SERVICE_CODE,
                    "vnoska": credit.vnoska,
                    "client_fio": client_fio
                },
                content_type="application/xml"
            )
        except Tcredits.DoesNotExist:
            resp = render(
                request,
                "payment_gateways/pb_response_search_error.xml",
                {"error_msg": "Договор не найден"},
                content_type="application/xml"
            )
        except Tcredits.MultipleObjectsReturned:
            resp = render(
                request,
                "payment_gateways/pb_response_search_error.xml",
                {"error_msg": "Ошибка при поиске договора"},
                content_type="application/xml"
            )

    elif action == "Pay":
        data = xml_data['Transfer']['Data']
        pb_code = data['@id']
        contract_num = data['PayerInfo']['@billIdentifier']
        note = data['PayerInfo']['Fio']
        total_sum = Decimal(data['TotalSum'])
        # create_time = data['CreateTime']

        try:
            with transaction.atomic():
                cash = Tcash.objects.create(
                    sum=total_sum,
                    note=note,
                    type='in',
                    pb_code=pb_code
                )
                resp = render(
                    request,
                    "payment_gateways/pb_response_pay_success.xml",
                    {"cash_id": cash.id},
                    content_type="application/xml"
                )
        except Exception:
            resp = render(
                request,
                "payment_gateways/pb_response_pay_error.xml",
                {"error_msg": "Ошибка при оплате"},
                content_type="application/xml"
            )
    else:
        resp = HttpResponse()

    return resp
