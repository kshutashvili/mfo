from decimal import Decimal

import MySQLdb

from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from django.http.response import HttpResponseBadRequest, HttpResponse
from django.conf import settings
from django.db import transaction
from django.utils import timezone
from django.utils.formats import number_format
from django.views.generic.base import TemplateView

from payment_gateways.utils import process_pb_request, process_easypay_request
from payment_gateways.models import (Tcredits, Tpersons, Tcash,
                                     EasypayPayment, City24Payment)
from payment_gateways import constants


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
                    "vnoska": number_format(
                        value=credit.vnoska,
                        use_l10n=False),
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
                    service_code=pb_code
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


@csrf_exempt
@require_POST
def easypay_terminal_view(request):

    is_valid, action, action_data = process_easypay_request(request)

    if not is_valid:
        return HttpResponseBadRequest("Операция не поддерживается")

    if action == constants.EASYPAY_CHECK:
        template = 'payment_gateways/easypay/response_1_check_success.xml'
        contract_num = action_data['Account']
        if contract_num:
            try:
                credit = Tcredits.objects.get(
                    contract_num=int(contract_num)
                )
                client_qs = Tpersons.objects.filter(id=credit.client_id)
                if client_qs:
                    client = client_qs[0]
                    client_fio = "{0} {1}. {2}.".format(
                        client.name3,
                        client.name[0].upper(),
                        client.name2[0].upper(),
                    )
                    ctx = {
                        'status_code': 0,
                        'status_detail': 'Платеж разрешен',
                        'date_time': timezone.now().strftime(
                            settings.EASYPAY_DATE_FORMAT
                        ),
                        'signature': '',
                        'account_params': {
                            'Contract': str(contract_num),
                            'Fio': client_fio,
                            'Sum': str(credit.vnoska),
                        }
                    }
                    return render(
                        request,
                        template,
                        ctx,
                        content_type='application/xml'
                    )
            except Exception as e:
                print('Error: ', e)
        ctx = {
            'status_code': -1,
            'status_detail': 'Договор не найден',
            'date_time': timezone.now().strftime(
                settings.EASYPAY_DATE_FORMAT
            ),
            'signature': '',
            'account_params': {}
        }
        return render(
            request,
            template,
            ctx,
            content_type='application/xml'
        )

    elif action == constants.EASYPAY_PAYMENT:
        template = 'payment_gateways/easypay/response_2_payment_success.xml'
        try:
            with transaction.atomic():
                payment = EasypayPayment.objects.create(
                    service_id=action_data['ServiceId'],
                    order_id=action_data['OrderId'],
                    account=action_data['Account'],
                    amount=action_data['Amount'],
                )

            ctx = {
                'status_code': 0,
                'status_detail': 'Платеж создан',
                'date_time': timezone.now().strftime(settings.EASYPAY_DATE_FORMAT),
                'signature': '',
                'payment_id': str(payment.id)
            }
        except Exception as e:
            print(e)
            ctx = {
                'status_code': -1,
                'status_detail': 'Ошибка при создании платежа',
                'date_time': timezone.now().strftime(settings.EASYPAY_DATE_FORMAT),
                'signature': '',
                'payment_id': ''
            }
        return render(request, template, ctx, content_type='application/xml')

    elif action == constants.EASYPAY_CONFIRM:
        template = 'payment_gateways/easypay/response_3_payment_confirm_success.xml'
        ctx = {
            'status_code': 0,
            'status_detail': 'Платеж успешно проведен',
            'date_time': timezone.now().strftime(settings.EASYPAY_DATE_FORMAT),
            'signature': '',
            'order_date': ''
        }

        try:
            with transaction.atomic():
                payment = EasypayPayment.objects.select_for_update().get(
                    id=action_data['PaymentId']
                )
                payment.confirmed = True
                payment.confirmed_dt = timezone.now()
                payment.save()
                ctx['order_date'] = payment.confirmed_dt.strftime(
                    settings.EASYPAY_DATE_FORMAT
                )

                cash = Tcash.objects.create(
                    sum=payment.amount,
                    note='easypay',
                    type='in',
                    service_code=payment.order_id
                )

        except Exception as e:
            print(e)
            ctx['status_code'] = -1
            ctx['status_detail'] = 'Платеж не найден'

        return render(request, template, ctx, content_type='application/xml')

    elif action == constants.EASYPAY_CANCEL:
        template = 'payment_gateways/easypay/response_4_payment_cancel_success.xml'
        ctx = {
            'status_code': 0,
            'status_detail': 'Платеж успешно отменен',
            'date_time': timezone.now().strftime(settings.EASYPAY_DATE_FORMAT),
            'signature': '',
            'cancel_date': ''
        }

        try:
            with transaction.atomic():
                payment = EasypayPayment.objects.select_for_update().get(
                    id=action_data['PaymentId']
                )
                payment.canceled = True
                payment.cancel_dt = timezone.now()
                payment.save()
                ctx['cancel_date'] = payment.cancel_dt.strftime(
                    settings.EASYPAY_DATE_FORMAT
                )

        except Exception as e:
            print(e)
            ctx['status_code'] = -1
            ctx['status_detail'] = 'Платеж не найден'

        return render(request, template, ctx, content_type='application/xml')
    else:
        resp = HttpResponse()

    return resp


@csrf_exempt
@require_POST
def city24_terminal_view(request):

    is_valid, action, action_data = process_easypay_request(request)

    if not is_valid:
        return HttpResponseBadRequest("Операция не поддерживается")

    if action == constants.EASYPAY_CHECK:
        template = 'payment_gateways/easypay/response_1_check_success.xml'
        contract_num = action_data['Account']
        if contract_num:
            try:
                credit = Tcredits.objects.get(
                    contract_num=int(contract_num)
                )
                client_qs = Tpersons.objects.filter(id=credit.client_id)
                if client_qs:
                    client = client_qs[0]
                    client_fio = "{0} {1}. {2}.".format(
                        client.name3,
                        client.name[0].upper(),
                        client.name2[0].upper(),
                    )
                    ctx = {
                        'status_code': 0,
                        'status_detail': 'Платеж разрешен',
                        'date_time': timezone.now().strftime(
                            settings.EASYPAY_DATE_FORMAT
                        ),
                        'signature': '',
                        'account_params': {
                            'Contract': str(contract_num),
                            'Fio': client_fio,
                            'Sum': str(credit.vnoska),
                        }
                    }
                    return render(
                        request,
                        template,
                        ctx,
                        content_type='application/xml'
                    )
            except Exception as e:
                print('Error: ', e)
        ctx = {
            'status_code': -1,
            'status_detail': 'Договор не найден',
            'date_time': timezone.now().strftime(
                settings.EASYPAY_DATE_FORMAT
            ),
            'signature': '',
            'account_params': {}
        }
        return render(
            request,
            template,
            ctx,
            content_type='application/xml'
        )

    elif action == constants.EASYPAY_PAYMENT:
        template = 'payment_gateways/easypay/response_2_payment_success.xml'
        try:
            with transaction.atomic():
                payment = City24Payment.objects.create(
                    service_id=action_data['ServiceId'],
                    order_id=action_data['OrderId'],
                    account=action_data['Account'],
                    amount=action_data['Amount'],
                )

            ctx = {
                'status_code': 0,
                'status_detail': 'Платеж создан',
                'date_time': timezone.now().strftime(
                    settings.EASYPAY_DATE_FORMAT
                ),
                'signature': '',
                'payment_id': str(payment.id)
            }
        except Exception as e:
            print(e)
            ctx = {
                'status_code': -1,
                'status_detail': 'Ошибка при создании платежа',
                'date_time': timezone.now().strftime(
                    settings.EASYPAY_DATE_FORMAT
                ),
                'signature': '',
                'payment_id': ''
            }
        return render(request, template, ctx, content_type='application/xml')

    elif action == constants.EASYPAY_CONFIRM:
        template = 'payment_gateways/easypay/response_3_payment_confirm_success.xml'
        ctx = {
            'status_code': 0,
            'status_detail': 'Платеж успешно проведен',
            'date_time': timezone.now().strftime(settings.EASYPAY_DATE_FORMAT),
            'signature': '',
            'order_date': ''
        }

        try:
            with transaction.atomic():
                payment = City24Payment.objects.select_for_update().get(
                    id=action_data['PaymentId']
                )
                payment.confirmed = True
                payment.confirmed_dt = timezone.now()
                payment.save()
                ctx['order_date'] = payment.confirmed_dt.strftime(
                    settings.EASYPAY_DATE_FORMAT
                )

                cash = Tcash.objects.create(
                    sum=payment.amount,
                    note='city24',
                    type='in',
                    service_code=payment.order_id
                )

        except Exception as e:
            print(e)
            ctx['status_code'] = -1
            ctx['status_detail'] = 'Платеж не найден'

        return render(request, template, ctx, content_type='application/xml')

    elif action == constants.EASYPAY_CANCEL:
        template = 'payment_gateways/easypay/response_4_payment_cancel_success.xml'
        ctx = {
            'status_code': 0,
            'status_detail': 'Платеж успешно отменен',
            'date_time': timezone.now().strftime(settings.EASYPAY_DATE_FORMAT),
            'signature': '',
            'cancel_date': ''
        }

        try:
            with transaction.atomic():
                payment = City24Payment.objects.select_for_update().get(
                    id=action_data['PaymentId']
                )
                payment.canceled = True
                payment.cancel_dt = timezone.now()
                payment.save()
                ctx['cancel_date'] = payment.cancel_dt.strftime(
                    settings.EASYPAY_DATE_FORMAT
                )

        except Exception as e:
            print(e)
            ctx['status_code'] = -1
            ctx['status_detail'] = 'Платеж не найден'

        return render(request, template, ctx, content_type='application/xml')
    else:
        resp = HttpResponse()

    return resp


class TurnesView(TemplateView):
    template_name = "test_turnes.html"

    def get_context_data(self, **kwargs):
        context = super(TurnesView, self).get_context_data()
        exfin_connection = MySQLdb.connect(
            host="10.10.100.27",                # host of MySQL database
            # host="77.88.239.48",                # host of MySQL database
            user="root",                        # user's username
            passwd="Orraveza(99)",              # your password
            db="mbank",                         # name of the database
            charset="utf8"
        )

        # create CURSOR and set UTF8 params
        exfin_cursor = exfin_connection.cursor()
        exfin_cursor.execute('SET NAMES utf8;')
        exfin_cursor.execute('SET CHARACTER SET utf8;')
        exfin_cursor.execute('SET character_set_connection=utf8;')

        exfin_cursor.execute(
            """
                SELECT city 
                FROM mbank.tobjects;
            """
        )
        context["rows"] = exfin_cursor.fetchall()
        return context
