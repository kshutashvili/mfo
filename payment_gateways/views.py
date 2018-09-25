from decimal import Decimal
from datetime import date, datetime, timedelta

from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from django.http.response import HttpResponseBadRequest, HttpResponse
from django.conf import settings
from django.db import transaction
from django.utils.formats import number_format

from payment_gateways.utils import (
    process_pb_request,
    process_easypay_request,
    process_fam_request
)
from payment_gateways.models import (
    EasypayPayment, City24Payment,
    PrivatbankPayment,
    SkyEasypayPayment, SkyCity24Payment,
    SkyPrivatbankPayment
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

        date_for_turnes = date.today()
        if datetime.now().hour >= 22:
            date_for_turnes = date_for_turnes + timedelta(days=1)

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
            "dt": date_for_turnes,
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

        if str(credit[0][4]) == '55':
            payment = SkyPrivatbankPayment.objects.create(
                transaction_id=pb_code,
                inrazpredelenie_id=lastrowid,
                contract_num=contract_num,
                client_name=name,
                amount=total_sum,
                created_dt=create_time,
                confirm_dt=confirm_time
            )
            telegram_notification(
                err='',
                message='Privat Оплата по кредиту Skyбанка. Дог.{0}.'.format(
                    contract_num
                )
            )
        else:
            payment = PrivatbankPayment.objects.create(
                transaction_id=pb_code,
                inrazpredelenie_id=lastrowid,
                contract_num=contract_num,
                client_name=name,
                amount=total_sum,
                created_dt=create_time,
                confirm_dt=confirm_time
            )

        try:
            with transaction.atomic():
                query = """
                    SELECT mbank.RunRazpredelenieOnlineNew("{0}");
                """.format(
                    date.today()
                )
                cursor.execute(query)
                conn.commit()
        except Exception as e:
            telegram_notification(
                err=e,
                message='Проблема с разнесением платежа'
            )
            resp = render(
                request,
                "payment_gateways/pb_response_pay_error.xml",
                {"error_msg": "Ошибка при оплате. Обратитесь в контакт-центр по тел. 0800211112"},
                content_type="application/xml"
            )
            return resp

        conn.close()

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
            telegram_notification(
                err=e,
                message='Проблема с подключением к Турнесу (Easy)'
            )
            ctx = {
                'status_code': -1,
                'status_detail': 'Ошибка при поиске',
                'date_time': datetime.now().strftime(
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
            telegram_notification(
                err='',
                message='Договор не найден - {0} (Easy)'.format(
                    contract_num
                )
            )
            # Render error if credit_row is empty
            # (Credit with particular contract number not found)
            ctx = {
                'status_code': -1,
                'status_detail': 'Договор не найден',
                'date_time': datetime.now().strftime(
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
            'date_time': datetime.now().strftime(
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
        contract_num = action_data['Account']

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
                message='Проблема с подключением к Турнесу (Easy)'
            )
            ctx = {
                'status_code': -1,
                'status_detail': 'Ошибка при поиске',
                'date_time': datetime.now().strftime(
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
            telegram_notification(
                err='',
                message='Договор не найден - {0} (Easy)'.format(
                    contract_num
                )
            )
            # Render error if credit_row is empty
            # (Credit with particular contract number not found)
            ctx = {
                'status_code': -1,
                'status_detail': 'Договор не найден',
                'date_time': datetime.now().strftime(
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

        try:
            if str(credit[0][4]) == '55':
                payment = SkyEasypayPayment.objects.create(
                    service_id=action_data['ServiceId'],
                    order_id=action_data['OrderId'],
                    account=action_data['Account'],
                    amount=action_data['Amount'],
                    client_name=credit_row[2]
                )
                telegram_notification(
                    err='',
                    message='Easy Оплата по кредиту Skyбанка. Дог.{0}.'.format(
                        contract_num
                    )
                )
            else:
                payment = EasypayPayment.objects.create(
                    service_id=action_data['ServiceId'],
                    order_id=action_data['OrderId'],
                    account=action_data['Account'],
                    amount=action_data['Amount'],
                    client_name=credit_row[2]
                )
        except Exception as e:
            telegram_notification(
                err=e,
                message='Ошибка при создании платежа (Easy)'
            )
            ctx = {
                'status_code': -1,
                'status_detail': 'Ошибка при создании платежа',
                'date_time': datetime.now().strftime(
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
            'date_time': datetime.now().strftime(
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
            'date_time': datetime.now().strftime(settings.EASYPAY_DATE_FORMAT),
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
            try:
                payment = SkyEasypayPayment.objects.get(
                    id=action_data['PaymentId']
                )
            except Exception:
                telegram_notification(
                    err='',
                    message='Платеж не найден на сайте (Easy)'
                )
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
        except Exception as e:
            telegram_notification(
                err=e,
                message='Проблема с подключением к Турнесу (Easy)'
            )
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
        except Exception as e:
            telegram_notification(
                err=e,
                message='Не указан ИНН (Easy)'
            )
            ctx['status_code'] = -1
            ctx['status_detail'] = 'Ошибка при оплате'
            return render(
                request,
                template,
                ctx,
                content_type='application/xml'
            )

        date_for_turnes = date.today()
        if datetime.now().hour >= 22:
            date_for_turnes = date_for_turnes + timedelta(days=1)

        data = {
            "No": payment.order_id,
            "DogNo": payment.account,
            "IPN": ipn,
            "dt": date_for_turnes,
            "sm": payment.amount,
            "status": 0,
            "ibank": 284
        }

        names = credit[0][2].split(" ")

        try:
            data["F"] = names[0]
        except Exception as e:
            telegram_notification(
                err=e,
                message='Неполное ФИО'
            )
            data["F"] = credit[0][2]

        try:
            data["I"] = names[1]
        except Exception:
            data["I"] = ''

        try:
            data["O"] = names[2]
        except Exception:
            data["O"] = ''

        # save payment to Turnes in_razpredelenie table
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
        payment.confirmed_dt = datetime.now()
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
            'date_time': datetime.now().strftime(settings.EASYPAY_DATE_FORMAT),
            'signature': '',
            'cancel_date': ''
        }

        try:
            with transaction.atomic():
                payment = EasypayPayment.objects.select_for_update().get(
                    id=action_data['PaymentId']
                )
                payment.canceled = True
                payment.cancel_dt = datetime.now()
                payment.save()
                ctx['cancel_date'] = payment.cancel_dt.strftime(
                    settings.EASYPAY_DATE_FORMAT
                )

        except Exception:
            telegram_notification(
                err='',
                message='Ошибка при отмене платежа (Easy)'
            )
            ctx['status_code'] = -1
            ctx['status_detail'] = 'Платеж не найден'

        return render(request, template, ctx, content_type='application/xml')

    else:
        resp = HttpResponse()

    return resp


@csrf_exempt
@require_POST
def fam_terminal_view(request):

    is_valid, action, action_data = process_fam_request(request)

    if not is_valid:
        return HttpResponseBadRequest("Операция не поддерживается")

    if action == constants.EASYPAY_CHECK:
        template = 'payment_gateways/fam/response_1_check.xml'
        contract_num = action_data['Account']

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
                message='Проблема с подключением к Турнесу (C24)'
            )
            ctx = {
                'status_code': -1,
                'status_detail': 'Ошибка при поиске',
                'date_time': datetime.now().strftime(
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
            telegram_notification(
                err='',
                message='Договор не найден - {0} (C24)'.format(
                    contract_num
                )
            )
            # Render error if credit_row is empty
            # (Credit with particular contract number not found)
            ctx = {
                'status_code': -1,
                'status_detail': 'Договор не найден',
                'date_time': datetime.now().strftime(
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
            'date_time': datetime.now().strftime(
                settings.EASYPAY_DATE_FORMAT
            ),
            'signature': '',
            'account_params': {
                'Contract': str(contract_num),
                'Name': credit_row[2],
                'Balance': str(credit_row[3]),
            }
        }
        return render(
            request,
            template,
            ctx,
            content_type='application/xml'
        )

    elif action == constants.EASYPAY_PAYMENT:
        template = 'payment_gateways/fam/response_2_payment.xml'
        contract_num = action_data['Account']

        p = City24Payment.objects.filter(order_id=action_data['OrderId'])
        if p:
            telegram_notification(
                err='',
                message='Дубль платежа {0}'.format(action_data['OrderId'])
            )
            ctx = {
                'status_code': -1,
                'status_detail': 'Ошибка при создании платежа',
                'date_time': datetime.now().strftime(
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
                message='Проблема с подключением к Турнесу (C24)'
            )
            ctx = {
                'status_code': -1,
                'status_detail': 'Ошибка при поиске',
                'date_time': datetime.now().strftime(
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
            telegram_notification(
                err='',
                message='Договор не найден - {0} (C24)'.format(
                    contract_num
                )
            )
            # Render error if credit_row is empty
            # (Credit with particular contract number not found)
            ctx = {
                'status_code': -1,
                'status_detail': 'Договор не найден',
                'date_time': datetime.now().strftime(
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

        try:
            payment = City24Payment.objects.create(
                service_id=action_data['ServiceId'],
                order_id=action_data['OrderId'],
                account=action_data['Account'],
                amount=action_data['Amount'],
                client_name=credit_row[2]
            )
        except Exception as e:
            telegram_notification(
                err=e,
                message='Ошибка при создании платежа (C24)'
            )
            ctx = {
                'status_code': -1,
                'status_detail': 'Ошибка при создании платежа',
                'date_time': datetime.now().strftime(
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
            'date_time': datetime.now().strftime(
                settings.EASYPAY_DATE_FORMAT
            ),
            'signature': '',
            'payment_id': str(payment.id)
        }

        return render(request, template, ctx, content_type='application/xml')

    elif action == constants.EASYPAY_CONFIRM:
        # defaults
        template = 'payment_gateways/fam/response_3_payment_confirm.xml'
        ctx = {
            'status_code': 0,
            'status_detail': 'Платеж успешно проведен',
            'date_time': datetime.now().strftime(settings.EASYPAY_DATE_FORMAT),
            'signature': '',
            'order_date': ''
        }

        # get payment object, created on previous
        # constants.EASYPAY_PAYMENT step
        try:
            payment = City24Payment.objects.get(
                id=action_data['PaymentId']
            )
        except Exception:
            telegram_notification(
                err='',
                message='Платеж не найден на сайте (C24)'
            )
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
        except Exception as e:
            telegram_notification(
                err=e,
                message='Проблема с подключением к Турнесу (C24)'
            )
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
        except Exception as e:
            telegram_notification(
                err=e,
                message='Не указан ИНН (C24)'
            )
            ctx['status_code'] = -1
            ctx['status_detail'] = 'Ошибка при оплате'
            return render(
                request,
                template,
                ctx,
                content_type='application/xml'
            )

        date_for_turnes = date.today()
        if datetime.now().hour >= 22:
            date_for_turnes = date_for_turnes + timedelta(days=1)

        data = {
            "No": payment.order_id,
            "DogNo": payment.account,
            "IPN": ipn,
            "dt": date_for_turnes,
            "sm": payment.amount,
            "status": 0,
            "ibank": 100
        }

        names = credit[0][2].split(" ")

        try:
            data["F"] = names[0]
        except Exception as e:
            telegram_notification(
                err=e,
                message='Неполное ФИО'
            )
            data["F"] = credit[0][2]

        try:
            data["I"] = names[1]
        except Exception:
            data["I"] = ''

        try:
            data["O"] = names[2]
        except Exception:
            data["O"] = ''

        # save payment to Turnes in_razpredelenie table
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
        payment.confirmed_dt = datetime.now()
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
        template = 'payment_gateways/fam/response_4_payment_cancel.xml'
        ctx = {
            'status_code': 0,
            'status_detail': 'Платеж успешно отменен',
            'date_time': datetime.now().strftime(settings.EASYPAY_DATE_FORMAT),
            'signature': '',
            'cancel_date': ''
        }

        try:
            with transaction.atomic():
                payment = City24Payment.objects.select_for_update().get(
                    id=action_data['PaymentId']
                )
                payment.canceled = True
                payment.cancel_dt = datetime.now()
                payment.save()
                ctx['cancel_date'] = payment.cancel_dt.strftime(
                    settings.EASYPAY_DATE_FORMAT
                )

        except Exception:
            telegram_notification(
                err='',
                message='Ошибка при отмене платежа (C24)'
            )
            ctx['status_code'] = -1
            ctx['status_detail'] = 'Платеж не найден'

        return render(request, template, ctx, content_type='application/xml')

    else:
        resp = HttpResponse()

    return resp
