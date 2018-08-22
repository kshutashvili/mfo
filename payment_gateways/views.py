from decimal import Decimal
from datetime import date

from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from django.http.response import HttpResponseBadRequest, HttpResponse
from django.conf import settings
from django.db import transaction
from django.utils import timezone
from django.utils.formats import number_format

from payment_gateways.utils import process_pb_request, process_easypay_request
from payment_gateways.models import (
    Tcredits, Tpersons, Tcash,
    EasypayPayment, City24Payment,
    PrivatbankPayment
)
from payment_gateways import constants
from payment_gateways.utils import create_database_connection
from payment_gateways.helpers import (
    search_credit, save_payment,
    telegram_notification
)


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
            conn, cursor = create_database_connection(
                host=settings.TURNES_HOST,
                user=settings.TURNES_USER,
                password=settings.TURNES_PASSWORD,
                db=settings.TURNES_DATABASE
            )
        except Exception as e:
            telegram_notification(
                err=e,
                message='Проблема с подключением к Турнесу'
            )
            resp = render(
                request,
                "payment_gateways/pb_response_pay_error.xml",
                {"error_msg": "Ошибка при поиске. Обратитесь в контакт-центр по тел. 0800211112"},
                content_type="application/xml"
            )
            return resp

        credit = search_credit(
            cursor=cursor,
            contract_num=contract_num
        )

        conn.close()

        try:
            credit_row = credit[0]
        except Exception as e:
            telegram_notification(
                err=e,
                message='Неправильно введен номер договора, №{0}'.format(
                    contract_num
                )
            )
            # Render error if credit_row is empty
            # (Credit with particular contract number not found)
            resp = render(
                request,
                "payment_gateways/pb_response_search_error.xml",
                {"error_msg": "Договор не найден. Обратитесь в контакт-центр по тел. 0800211112"},
                content_type="application/xml"
            )
            return resp

        resp = render(
            request,
            "payment_gateways/pb_response_search_success.xml",
            {
                "contract_num": contract_num,
                "service_code": settings.PB_SERVICE_CODE,
                "vnoska": number_format(
                    value=credit_row[6] if credit_row[6] > 0 else 0,
                    use_l10n=False
                ),
                "client_fio": credit_row[2]
            },
            content_type="application/xml"
        )
        return resp

    elif action == "Pay":
        data = xml_data['Transfer']['Data']
        pb_code = data['@id']
        contract_num = data['PayerInfo']['@billIdentifier']
        name = data['PayerInfo']['Fio']
        total_sum = Decimal(data['TotalSum'])
        create_time = data['CreateTime']
        confirm_time = data['ConfirmTime']

        p = PrivatbankPayment.objects.filter(transaction_id=pb_code)
        if p:
            telegram_notification(
                err='',
                message='Дубль платежа {0}'.format(pb_code)
            )
            resp = render(
                request,
                "payment_gateways/pb_response_pay_success.xml",
                {"cash_id": p[0].id},
                content_type="application/xml"
            )
            return resp

        try:
            conn, cursor = create_database_connection(
                host=settings.TURNES_HOST,
                user=settings.TURNES_USER,
                password=settings.TURNES_PASSWORD,
                db=settings.TURNES_DATABASE
            )
        except Exception as e:
            telegram_notification(
                err=e,
                message='Проблема с подключением к Турнесу'
            )
            resp = render(
                request,
                "payment_gateways/pb_response_pay_error.xml",
                {"error_msg": "Ошибка при оплате. Обратитесь в контакт-центр по тел. 0800211112"},
                content_type="application/xml"
            )
            return resp

        credit = search_credit(
            cursor=cursor,
            contract_num=contract_num
        )
        try:
            ipn = credit[0][5]
        except Exception as e:
            telegram_notification(
                err=e,
                message='Проблема с поиском кредита при оплате, дог.{0}'.format(
                    contract_num
                )
            )
            resp = render(
                request,
                "payment_gateways/pb_response_pay_error.xml",
                {"error_msg": "Ошибка при оплате. Обратитесь в контакт-центр по тел. 0800211112"},
                content_type="application/xml"
            )
            return resp

        data = {
            "No": pb_code,
            "DogNo": contract_num,
            "IPN": ipn,
            "dt": date.today(),
            "sm": total_sum,
            "status": 0,
            "ibank": '26509056200284'
        }

        names = name.split(" ")

        try:
            data["F"] = names[0]
        except Exception as e:
            telegram_notification(
                err=e,
                message='Неполное ФИО'
            )
            data["F"] = name

        try:
            data["I"] = names[1]
        except Exception:
            data["I"] = ''

        try:
            data["O"] = names[2]
        except Exception:
            data["O"] = ''

        try:
            with transaction.atomic():
                lastrowid = save_payment(
                    conn=conn,
                    cursor=cursor,
                    data=data
                )
        except Exception as e:
            telegram_notification(
                err=e,
                message='Проблема с сохранением транзакции в Турнес. {0}'.format(str(data))
            )
            resp = render(
                request,
                "payment_gateways/pb_response_pay_error.xml",
                {"error_msg": "Ошибка при оплате. Обратитесь в контакт-центр по тел. 0800211112"},
                content_type="application/xml"
            )
            return resp

        payment = PrivatbankPayment.objects.create(
            transaction_id=pb_code,
            inrazpredelenie_id=lastrowid,
            contract_num=contract_num,
            client_name=name,
            amount=total_sum,
            created_dt=create_time,
            confirm_dt=confirm_time
        )
        resp = render(
            request,
            "payment_gateways/pb_response_pay_success.xml",
            {"cash_id": payment.id},
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

        try:
            conn, cursor = create_database_connection(
                host=settings.TURNES_HOST,
                user=settings.TURNES_USER,
                password=settings.TURNES_PASSWORD,
                db=settings.TURNES_DATABASE
            )
        except Exception as e:
            ctx = {
                'status_code': -1,
                'status_detail': 'Ошибка при поиске',
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

        credit = search_credit(
            cursor=cursor,
            contract_num=contract_num
        )

        conn.close()

        try:
            credit_row = credit[0]
        except Exception:
            # Render error if credit_row is empty
            # (Credit with particular contract number not found)
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

        ctx = {
            'status_code': 0,
            'status_detail': 'Платеж разрешен',
            'date_time': timezone.now().strftime(
                settings.EASYPAY_DATE_FORMAT
            ),
            'signature': '',
            'account_params': {
                'Contract': str(contract_num),
                'Fio': credit_row[2],
                'Sum': str(credit_row[3]),
            }
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
            payment = EasypayPayment.objects.create(
                service_id=action_data['ServiceId'],
                order_id=action_data['OrderId'],
                account=action_data['Account'],
                amount=action_data['Amount'],
            )
        except Exception:
            ctx = {
                'status_code': -1,
                'status_detail': 'Ошибка при создании платежа',
                'date_time': timezone.now().strftime(
                    settings.EASYPAY_DATE_FORMAT
                ),
                'signature': '',
                'payment_id': ''
            }
            return render(
                request,
                template,
                ctx,
                content_type='application/xml'
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

        return render(request, template, ctx, content_type='application/xml')

    elif action == constants.EASYPAY_CONFIRM:
        # defaults
        template = 'payment_gateways/easypay/response_3_payment_confirm_success.xml'
        ctx = {
            'status_code': 0,
            'status_detail': 'Платеж успешно проведен',
            'date_time': timezone.now().strftime(settings.EASYPAY_DATE_FORMAT),
            'signature': '',
            'order_date': ''
        }

        # get payment object, created on previous
        # constants.EASYPAY_PAYMENT step
        try:
            payment = EasypayPayment.objects.get(
                id=action_data['PaymentId']
            )
        except Exception:
            ctx['status_code'] = -1
            ctx['status_detail'] = 'Платеж не найден'
            return render(
                request,
                template,
                ctx,
                content_type='application/xml'
            )

        # create turnes connection
        try:
            conn, cursor = create_database_connection(
                host=settings.TURNES_HOST,
                user=settings.TURNES_USER,
                password=settings.TURNES_PASSWORD,
                db=settings.TURNES_DATABASE
            )
        except Exception:
            ctx['status_code'] = -1
            ctx['status_detail'] = 'Ошибка при оплате'
            return render(
                request,
                template,
                ctx,
                content_type='application/xml'
            )

        # get credit object from Turnes
        credit = search_credit(
            cursor=cursor,
            contract_num=payment.account
        )

        try:
            ipn = credit[0][5]
        except Exception:
            ctx['status_code'] = -1
            ctx['status_detail'] = 'Ошибка при оплате'
            return render(
                request,
                template,
                ctx,
                content_type='application/xml'
            )

        data = {
            "No": payment.order_id,
            "DogNo": payment.account,
            "IPN": ipn,
            "dt": date.today(),
            "sm": payment.amount,
            "status": 0,
            "ibank": 100
        }
        data["F"], data["I"], data["O"] = credit[0][2].split(" ")

        # save payment to Turnes in_razpredelenie table
        try:
            with transaction.atomic():
                lastrowid = save_payment(
                    conn=conn,
                    cursor=cursor,
                    data=data
                )
        except Exception:
            ctx['status_code'] = -1
            ctx['status_detail'] = 'Ошибка при оплате'
            return render(
                request,
                template,
                ctx,
                content_type='application/xml'
            )

        conn.close()

        # save payment confirmation to site's DB
        payment.confirmed = True
        payment.confirmed_dt = timezone.now()
        payment.inrazpredelenie_id = lastrowid
        payment.save()

        ctx['order_date'] = payment.confirmed_dt.strftime(
            settings.EASYPAY_DATE_FORMAT
        )
        return render(
            request,
            template,
            ctx,
            content_type='application/xml'
        )

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

        except Exception:
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
