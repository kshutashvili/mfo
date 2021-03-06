from decimal import Decimal
from datetime import date, datetime, timedelta

from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from django.views.generic import View
from django.http.response import HttpResponseBadRequest, HttpResponse
from django.conf import settings
from django.db import transaction
from django.utils.formats import number_format
from django.utils.decorators import method_decorator

from payment_gateways.utils import (
    process_pb_request,
    process_easypay_request,
    process_fam_request
)
from payment_gateways.models import (
    EasypayPayment, City24Payment,
    PrivatbankPayment,
    SkyEasypayPayment, SkyCity24Payment,
    SkyPrivatbankPayment,
    C24Payment, SkyC24Payment,
    PortmonePrivatPayment, PortmoneEasypayPayment,
    OkciPrivatPayment, OkciEasypayPayment
)
from payment_gateways import constants
from payment_gateways.utils import create_database_connection
from payment_gateways.helpers import (
    search_credit, save_payment,
    telegram_notification,
    telegram_notification_sky,
    search_skycredit,
    search_okcicredit
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

        telegram_notification(
            message='Search (pb_terminal_view) {0}'.format(
                contract_num
            )
        )
        telegram_notification(
            message=xml_data
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

        telegram_notification(
            message='Pay (pb_terminal_view) {0}'.format(
                contract_num
            )
        )
        telegram_notification(
            message=xml_data
        )

        # replace payment's date if payment processed after 22:00
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

        p2 = SkyPrivatbankPayment.objects.filter(transaction_id=pb_code)
        if p2:
            telegram_notification_sky(
                err='Дубль',
                message='Дубль платежа {0}'.format(pb_code)
            )
            telegram_notification(
                err='Дубль',
                message='Дубль платежа {0}'.format(pb_code)
            )
            resp = render(
                request,
                "payment_gateways/pb_response_pay_success.xml",
                {"cash_id": p2[0].id},
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
            "status": 55 if str(credit[0][4]) in ('55', '555') else 0,
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

        if str(credit[0][4]) == '55' or str(credit[0][4]) == '555':
            payment = SkyPrivatbankPayment.objects.create(
                transaction_id=pb_code,
                inrazpredelenie_id=lastrowid,
                contract_num=contract_num,
                client_name=name,
                amount=total_sum,
                created_dt=create_time,
                confirm_dt=confirm_time
            )
            telegram_notification_sky(
                message='Оплата кредита Skybank(Приватбанк)\nДог.{0}; Сумма {1}. Статус {2}'.format(
                    contract_num,
                    total_sum,
                    credit[0][4]
                )
            )
            telegram_notification(
                message='Оплата кредита Skybank(Приватбанк)\nДог.{0}; Сумма {1}. Статус {2}'.format(
                    contract_num,
                    total_sum,
                    credit[0][4]
                )
            )
            telegram_notification(
                message='{0}\n{1}\n{2}'.format(
                    request.META['REMOTE_ADDR'] if 'REMOTE_ADDR' in request.META.keys() else 'REMOTE_ADDR',
                    request.META['REMOTE_HOST'] if 'REMOTE_HOST' in request.META.keys() else 'REMOTE_HOST',
                    request.META['PATH_INFO'] if 'PATH_INFO' in request.META.keys() else 'PATH_INFO'
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

        # try:
        #     with transaction.atomic():
        #         query = """
        #             SELECT mbank.RunRazpredelenieOnlineNew("{0}");
        #         """.format(
        #             date.today()
        #         )
        #         cursor.execute(query)
        #         conn.commit()
        # except Exception as e:
        #     telegram_notification(
        #         err=e,
        #         message='Проблема с разнесением платежа'
        #     )
        #     resp = render(
        #         request,
        #         "payment_gateways/pb_response_pay_error.xml",
        #         {"error_msg": "Ошибка при оплате. Обратитесь в контакт-центр по тел. 0800211112"},
        #         content_type="application/xml"
        #     )
        #     return resp

        # try:
        #     with transaction.atomic():
        #         query = """
        #             SELECT mbank.RunRazpredelenieSkyOnline("{0}");
        #         """.format(
        #             date.today()
        #         )
        #         cursor.execute(query)
        #         conn.commit()
        # except Exception as e:
        #     telegram_notification_sky(
        #         err=e,
        #         message='Проблема с разнесением Sky платежа (status {0})'.format(
        #             str(credit[0][4])
        #         )
        #     )
        #     telegram_notification(
        #         err=e,
        #         message='Проблема с разнесением Sky платежа (status {0})'.format(
        #             str(credit[0][4])
        #         )
        #     )
        #     resp = render(
        #         request,
        #         "payment_gateways/pb_response_pay_error.xml",
        #         {"error_msg": "Ошибка при оплате. Обратитесь в контакт-центр по тел. 0800211112"},
        #         content_type="application/xml"
        #     )
        #     return resp

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

        telegram_notification(
            message='Search (easypay_terminal_view) {0}'.format(
                contract_num
            )
        )
        telegram_notification(
            message=action_data
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

        telegram_notification(
            message='Pay (easypay_terminal_view) {0}'.format(
                contract_num
            )
        )
        telegram_notification(
            message=action_data
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
            if str(credit[0][4]) == '55' or str(credit[0][4]) == '555':
                payment = SkyEasypayPayment.objects.create(
                    service_id=action_data['ServiceId'],
                    order_id=action_data['OrderId'],
                    account=action_data['Account'],
                    amount=action_data['Amount'],
                    client_name=credit_row[2]
                )
                telegram_notification_sky(
                    message='Оплата кредита Skybank(Easy)\nДог.{0}; Сумма {1}. Статус {2}'.format(
                        contract_num,
                        action_data['Amount'],
                        credit[0][4]
                    )
                )
                telegram_notification(
                    message='Оплата кредита Skybank(Easy)\nДог.{0}; Сумма {1}. Статус {2}'.format(
                        contract_num,
                        action_data['Amount'],
                        credit[0][4]
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
            'payment_id': str(payment.order_id)
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
                order_id=action_data['PaymentId']
            )
        except Exception:
            try:
                payment = SkyEasypayPayment.objects.get(
                    order_id=action_data['PaymentId']
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

        telegram_notification(
            message='Confirm (easypay_terminal_view) {0}'.format(
                payment.account
            )
        )
        telegram_notification(
            message=action_data
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
            "status": 55 if str(credit[0][4]) in ('55', '555') else 0,
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

        telegram_notification(
            message='Search (fam_terminal_view) {0}'.format(
                contract_num
            )
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
                message='Проблема с подключением к Турнесу (Фам)'
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
                message='Договор не найден - {0} (Фам)'.format(
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

        telegram_notification(
            message='Pay (fam_terminal_view) {0}'.format(
                contract_num
            )
        )

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
                message='Проблема с подключением к Турнесу (Фам)'
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
                message='Договор не найден - {0} (Фам)'.format(
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
            if str(credit[0][4]) == '55' or str(credit[0][4]) == '555':
                payment = SkyCity24Payment.objects.create(
                    service_id=action_data['ServiceId'],
                    order_id=action_data['OrderId'],
                    account=action_data['Account'],
                    amount=action_data['Amount'],
                    client_name=credit_row[2]
                )
                telegram_notification_sky(
                    message='Оплата кредита Skybank(Фам)\nДог.{0}; Сумма {1}. Статус {2}'.format(
                        contract_num,
                        action_data['Amount'],
                        credit[0][4]
                    )
                )
                telegram_notification(
                    message='Оплата кредита Skybank(Фам)\nДог.{0}; Сумма {1}. Статус {2}'.format(
                        contract_num,
                        action_data['Amount'],
                        credit[0][4]
                    )
                )
            else:
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
                message='Ошибка при создании платежа (Фам)'
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
            'payment_id': str(payment.order_id)
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
                order_id=action_data['PaymentId']
            )
        except Exception:
            try:
                payment = SkyCity24Payment.objects.get(
                    order_id=action_data['PaymentId']
                )
            except Exception:
                telegram_notification(
                    err='',
                    message='Платеж не найден на сайте (Фам)'
                )
                ctx['status_code'] = -1
                ctx['status_detail'] = 'Платеж не найден'
                return render(
                    request,
                    template,
                    ctx,
                    content_type='application/xml'
                )

        telegram_notification(
            message='Confirm (fam_terminal_view) {0}'.format(
                payment.account
            )
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
                message='Проблема с подключением к Турнесу (Фам)'
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
                message='Не указан ИНН (Фам)'
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
            "status": 55 if str(credit[0][4]) in ('55', '555') else 0,
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
                message='Ошибка при отмене платежа (Фам)'
            )
            ctx['status_code'] = -1
            ctx['status_detail'] = 'Платеж не найден'

        return render(request, template, ctx, content_type='application/xml')

    else:
        resp = HttpResponse()

    return resp


@csrf_exempt
@require_POST
def city_terminal_view(request):

    is_valid, action, action_data = process_fam_request(request)

    if not is_valid:
        return HttpResponseBadRequest("Операция не поддерживается")

    if action == constants.EASYPAY_CHECK:
        template = 'payment_gateways/fam/response_1_check.xml'
        contract_num = action_data['Account']

        telegram_notification(
            message='Search (city_terminal_view) {0}'.format(
                contract_num
            )
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

        telegram_notification(
            message='Pay (city_terminal_view) {0}'.format(
                contract_num
            )
        )

        p = C24Payment.objects.filter(order_id=action_data['OrderId'])
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
            if str(credit[0][4]) == '55' or str(credit[0][4]) == '555':
                payment = SkyC24Payment.objects.create(
                    service_id=action_data['ServiceId'] if action_data['ServiceId'] else 95,
                    order_id=action_data['OrderId'],
                    account=action_data['Account'],
                    amount=action_data['Amount'],
                    client_name=credit_row[2]
                )
                telegram_notification_sky(
                    message='Оплата кредита Skybank(C24)\nДог.{0}; Сумма {1}. Статус {2}'.format(
                        contract_num,
                        action_data['Amount'],
                        credit[0][4]
                    )
                )
                telegram_notification(
                    message='Оплата кредита Skybank(C24)\nДог.{0}; Сумма {1}. Статус {2}'.format(
                        contract_num,
                        action_data['Amount'],
                        credit[0][4]
                    )
                )
            else:
                payment = C24Payment.objects.create(
                    service_id=action_data['ServiceId'] if action_data['ServiceId'] else 95,
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
            'payment_id': str(payment.order_id)
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
            payment = C24Payment.objects.get(
                order_id=action_data['PaymentId']
            )
        except Exception:
            try:
                payment = SkyC24Payment.objects.get(
                    order_id=action_data['PaymentId']
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

        telegram_notification(
            message='Confirm (city_terminal_view) {0}'.format(
                payment.account
            )
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
            "status": 55 if str(credit[0][4]) in ('55', '555') else 0,
            "ibank": 101
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
                payment = C24Payment.objects.select_for_update().get(
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


class PrivatPaymentView(View):

    error_response_template = "payment_gateways/pb_response_pay_error.xml"
    http_method_names = ['post', ]

    @method_decorator(csrf_exempt)
    @method_decorator(require_POST)
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)

    def _error_response(self, error='', notify_message=''):
        telegram_notification(
            err=error,
            message=notify_message
        )
        resp = render(
            self.request,
            self.error_response_template,
            {"error_msg": "Произошла ошибка. Обратитесь в контакт-центр по тел. 0800211112"},
            content_type="application/xml"
        )

        return resp

    def _process_request(self, request):
        return process_pb_request(request)

    def _get_data(self):
        try:
            return self.xml_data["Transfer"]["Data"]
        except Exception:
            return None

    def _create_db_conn(self):
        """
            Create connection to MySQL database with cursor

            return connection_object, cursor_object
        """

        conn, cursor = create_database_connection(
            host=settings.TURNES_HOST,
            user=settings.TURNES_USER,
            password=settings.TURNES_PASSWORD,
            db=settings.TURNES_DATABASE
        )

        return conn, cursor

    def _search(self):
        self.data = self._get_data()

        if not self.data:
            return self._error_response(
                error="XML has not data",
                notify_message=""
            )

        try:
            conn, cur = self._create_db_conn()
        except Exception as e:
            pass

    def post(self, request, *args, **kwargs):
        self.is_valid, self.action, self.xml_data = self._process_request(
            request
        )

        if not self.is_valid:
            return HttpResponseBadRequest("Операция не поддерживается")

        if self.action == "Search":
            return self._search()
        elif self.action == "Pay":
            return self._pay()
        else:
            return HttpResponse()


@csrf_exempt
@require_POST
def portmone_ep_view(request):

    is_valid, action, action_data = process_fam_request(request)

    if not is_valid:
        return HttpResponseBadRequest("Операция не поддерживается")

    if action == constants.EASYPAY_CHECK:
        template = 'payment_gateways/fam/response_1_check.xml'
        contract_num = action_data['Account']

        telegram_notification(
            message='Search (portmone_ep_view) {0}'.format(
                contract_num
            )
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
                message='Проблема с подключением к Турнесу (Portmone ep)'
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

        credit = search_skycredit(
            cursor=cursor,
            contract_num=contract_num
        )

        conn.close()

        try:
            credit_row = credit[0]
        except Exception:
            telegram_notification(
                err='',
                message='Договор не найден - {0} (Portmone ep)'.format(
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
                'Balance': str(credit_row[6]) if credit_row[6] > 0 else 0,
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

        telegram_notification(
            message='Pay (portmone_ep_view) {0}'.format(
                contract_num
            )
        )

        p = PortmoneEasypayPayment.objects.filter(
            order_id=action_data['OrderId']
        )
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
                message='Проблема с подключением к Турнесу (Portmone ep)'
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

        credit = search_skycredit(
            cursor=cursor,
            contract_num=contract_num
        )

        conn.close()

        try:
            credit_row = credit[0]
        except Exception:
            telegram_notification(
                err='',
                message='Договор не найден - {0} (Portmone ep)'.format(
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
            payment = PortmoneEasypayPayment.objects.create(
                service_id=action_data['ServiceId'],
                order_id=action_data['OrderId'],
                account=action_data['Account'],
                amount=action_data['Amount'],
                client_name=credit_row[2]
            )
            telegram_notification_sky(
                message='Оплата кредита Skybank(Portmone ep)\nДог.{0}; Сумма {1}. Статус {2}'.format(
                    contract_num,
                    action_data['Amount'],
                    credit[0][4]
                )
            )
            telegram_notification(
                message='Оплата кредита Skybank(Portmone ep)\nДог.{0}; Сумма {1}. Статус {2}'.format(
                    contract_num,
                    action_data['Amount'],
                    credit[0][4]
                )
            )

        except Exception as e:
            telegram_notification(
                err=e,
                message='Ошибка при создании платежа (Portmone ep)'
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
            'payment_id': str(payment.order_id)
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
            payment = PortmoneEasypayPayment.objects.get(
                order_id=action_data['PaymentId']
            )
        except Exception:
            telegram_notification(
                err='',
                message='Платеж не найден на сайте (Portmone ep)'
            )
            ctx['status_code'] = -1
            ctx['status_detail'] = 'Платеж не найден'
            return render(
                request,
                template,
                ctx,
                content_type='application/xml'
            )

        telegram_notification(
            message='Confirm (portmone_ep_view) {0}'.format(
                payment.account
            )
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
                message='Проблема с подключением к Турнесу (Portmone ep)'
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
        credit = search_skycredit(
            cursor=cursor,
            contract_num=payment.account
        )

        try:
            ipn = credit[0][5]
        except Exception as e:
            telegram_notification(
                err=e,
                message='Не указан ИНН (Portmone ep)'
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
            "status": 10,
            "ibank": '156'
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
                payment = PortmoneEasypayPayment.objects.select_for_update().get(
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
                message='Ошибка при отмене платежа (Portmone ep)'
            )
            ctx['status_code'] = -1
            ctx['status_detail'] = 'Платеж не найден'

        return render(request, template, ctx, content_type='application/xml')

    else:
        resp = HttpResponse()

    return resp


@csrf_exempt
@require_POST
def portmone_pb_view(request):

    is_valid, action, xml_data = process_pb_request(request)

    if True: #if not is_valid:
        return HttpResponseBadRequest("Операция не поддерживается")

    if action == "Search":
        data = xml_data['Transfer']['Data']
        contract_num = data['Unit']['@value']

        telegram_notification(
            message='Search (portmone_pb_view) {0}'.format(
                contract_num
            )
        )
        telegram_notification(
            message=xml_data
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
                message='Проблема с подключением к Турнесу'
            )
            resp = render(
                request,
                "payment_gateways/pb_response_pay_error.xml",
                {"error_msg": "Ошибка при поиске. Обратитесь в контакт-центр по тел. 0800211112"},
                content_type="application/xml"
            )
            return resp

        credit = search_skycredit(
            cursor=cursor,
            contract_num=contract_num
        )

        conn.close()

        try:
            credit_row = credit[0]
        except Exception as e:
            telegram_notification(
                err=e,
                message='Неправильно введен номер договора, №{0}.{1}'.format(
                    contract_num,
                    '(Portmone pb)'
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

        telegram_notification(
            message='Pay (portmone_pb_view) {0}'.format(
                contract_num
            )
        )
        telegram_notification(
            message=xml_data
        )

        # replace payment's date if payment processed after 22:00
        date_for_turnes = date.today()
        if datetime.now().hour >= 22:
            date_for_turnes = date_for_turnes + timedelta(days=1)

        p = PortmonePrivatPayment.objects.filter(transaction_id=pb_code)
        if p:
            telegram_notification(
                err='',
                message='Дубль платежа {0}'.format(pb_code)
            )
            telegram_notification_sky(
                err='Дубль',
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

        credit = search_skycredit(
            cursor=cursor,
            contract_num=contract_num
        )

        try:
            ipn = credit[0][5]
        except Exception as e:
            telegram_notification(
                err=e,
                message='Проблема с поиском кредита при оплате, дог.{0}.{1}'.format(
                    contract_num,
                    '(Portmone pb)'
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
            "status": 10,
            "ibank": '155'
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

        payment = PortmonePrivatPayment.objects.create(
            transaction_id=pb_code,
            inrazpredelenie_id=lastrowid,
            contract_num=contract_num,
            client_name=name,
            amount=total_sum,
            created_dt=create_time,
            confirm_dt=confirm_time
        )
        telegram_notification_sky(
            message='Оплата кредита Skybank(Portmone pb)\nДог.{0}; Сумма {1}. Статус {2}'.format(
                contract_num,
                total_sum,
                credit[0][4]
            )
        )
        telegram_notification(
            message='Оплата кредита Skybank(Portmone pb)\nДог.{0}; Сумма {1}. Статус {2}'.format(
                contract_num,
                total_sum,
                credit[0][4]
            )
        )

        # try:
        #     with transaction.atomic():
        #         query = """
        #             SELECT mbank.RunRazpredelenieOnlineNew("{0}");
        #         """.format(
        #             date.today()
        #         )
        #         cursor.execute(query)
        #         conn.commit()
        # except Exception as e:
        #     telegram_notification(
        #         err=e,
        #         message='Проблема с разнесением платежа'
        #     )
        #     resp = render(
        #         request,
        #         "payment_gateways/pb_response_pay_error.xml",
        #         {"error_msg": "Ошибка при оплате. Обратитесь в контакт-центр по тел. 0800211112"},
        #         content_type="application/xml"
        #     )
        #     return resp

        # try:
        #     with transaction.atomic():
        #         query = """
        #             SELECT mbank.RunRazpredelenieSkyOnline("{0}");
        #         """.format(
        #             date.today()
        #         )
        #         cursor.execute(query)
        #         conn.commit()
        # except Exception as e:
        #     telegram_notification_sky(
        #         err=e,
        #         message='Проблема с разнесением Sky платежа (status {0})'.format(
        #             str(credit[0][4])
        #         )
        #     )
        #     telegram_notification(
        #         err=e,
        #         message='Проблема с разнесением Sky платежа (status {0})'.format(
        #             str(credit[0][4])
        #         )
        #     )
        #     resp = render(
        #         request,
        #         "payment_gateways/pb_response_pay_error.xml",
        #         {"error_msg": "Ошибка при оплате. Обратитесь в контакт-центр по тел. 0800211112"},
        #         content_type="application/xml"
        #     )
        #     return resp

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
def okci_pb_terminal_view(request):

    is_valid, action, xml_data = process_pb_request(request)

    if not is_valid:
        return HttpResponseBadRequest("Операция не поддерживается")

    if action == "Search":
        data = xml_data['Transfer']['Data']
        contract_num = data['Unit']['@value']

        telegram_notification(
            message='Search (okci_pb_terminal_view) {0}'.format(
                contract_num
            )
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
                message='Проблема с подключением к Турнесу'
            )
            resp = render(
                request,
                "payment_gateways/pb_response_pay_error.xml",
                {
                    "error_msg": "Ошибка при поиске. "
                                 "Обратитесь в контакт-центр "
                                 "по тел. 0800211112"
                },
                content_type="application/xml"
            )
            return resp

        credit = search_okcicredit(
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
                {
                    "error_msg": "Договор не найден. "
                                 "Обратитесь в контакт-центр по "
                                 "тел. 0800211112"
                },
                content_type="application/xml"
            )
            return resp

        # Render general payment info
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

        telegram_notification(
            message='Pay (okci_pb_terminal_view) {0}'.format(
                contract_num
            )
        )

        # replace payment's date if payment processed after 22:00
        date_for_turnes = date.today()
        if datetime.now().hour >= 22:
            date_for_turnes = date_for_turnes + timedelta(days=1)

        p = OkciPrivatPayment.objects.filter(transaction_id=pb_code)
        if p:
            telegram_notification(
                err='',
                message='Дубль платежа OKCI {0}'.format(pb_code)
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
                {
                    "error_msg": "Ошибка при оплате. "
                                 "Обратитесь в контакт-центр по "
                                 "тел. 0800211112"
                },
                content_type="application/xml"
            )
            return resp

        credit = search_okcicredit(
            cursor=cursor,
            contract_num=contract_num
        )

        try:
            ipn = credit[0][5]
        except Exception as e:
            telegram_notification(
                err=e,
                message='Проблема с поиском кредита при оплате дог.{0}'.format(
                    contract_num
                )
            )
            resp = render(
                request,
                "payment_gateways/pb_response_pay_error.xml",
                {
                    "error_msg": "Ошибка при оплате. "
                                 "Обратитесь в контакт-центр "
                                 "по тел. 0800211112"
                },
                content_type="application/xml"
            )
            return resp

        data = {
            'No': pb_code,
            'DogNo': contract_num,
            'IPN': ipn,
            'dt': date_for_turnes,
            'sm': total_sum,
            'status': 59,
            'ibank': '60 (ПБ)'
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
                message='Проблема с сохранением '
                        'транзакции в Турнес. {0}'.format(
                            str(data)
                        )
            )
            resp = render(
                request,
                "payment_gateways/pb_response_pay_error.xml",
                {
                    "error_msg": "Ошибка при оплате. "
                                 "Обратитесь в контакт-центр по "
                                 "тел. 0800211112"
                },
                content_type="application/xml"
            )
            return resp

        payment = OkciPrivatPayment.objects.create(
            transaction_id=pb_code,
            inrazpredelenie_id=lastrowid,
            contract_num=contract_num,
            client_name=name,
            amount=total_sum,
            created_dt=create_time,
            confirm_dt=confirm_time
        )
        telegram_notification(
            message='Оплата кредита OKCI (Приватбанк)\n'
                    'Дог.{0}; Сумма {1}. Статус {2}'.format(
                        contract_num,
                        total_sum,
                        credit[0][4]
                    )
        )

        # try:
        #     with transaction.atomic():
        #         query = """
        #             SELECT mbank.RunRazpredelenieOnlineNew("{0}");
        #         """.format(
        #             date.today()
        #         )
        #         cursor.execute(query)
        #         conn.commit()
        # except Exception as e:
        #     telegram_notification(
        #         err=e,
        #         message='Проблема с разнесением платежа'
        #     )
        #     resp = render(
        #         request,
        #         "payment_gateways/pb_response_pay_error.xml",
        #         {
        #             "error_msg": "Ошибка при оплате. "
        #                          "Обратитесь в контакт-центр по "
        #                          "тел. 0800211112"
        #         },
        #         content_type="application/xml"
        #     )
        #     return resp

        # try:
        #     with transaction.atomic():
        #         query = """
        #             SELECT mbank.RunRazpredelenieSkyOnline("{0}");
        #         """.format(
        #             date.today()
        #         )
        #         cursor.execute(query)
        #         conn.commit()
        # except Exception as e:
        #     telegram_notification_sky(
        #         err=e,
        #         message='Проблема с разнесением Sky платежа (status {0})'.format(
        #             str(credit[0][4])
        #         )
        #     )
        #     telegram_notification(
        #         err=e,
        #         message='Проблема с разнесением Sky платежа (status {0})'.format(
        #             str(credit[0][4])
        #         )
        #     )
        #     resp = render(
        #         request,
        #         "payment_gateways/pb_response_pay_error.xml",
        #         {"error_msg": "Ошибка при оплате. Обратитесь в контакт-центр по тел. 0800211112"},
        #         content_type="application/xml"
        #     )
        #     return resp

        try:
            with transaction.atomic():
                query = """
                    SELECT mbank.RunRazpredelenieOkciOnline("{0}");
                """.format(
                    date.today()
                )
                cursor.execute(query)
                conn.commit()
        except Exception as e:
            telegram_notification(
                err=e,
                message='Проблема с разнесением OKCI '
                        'платежа (status {0})'.format(
                            str(credit[0][4])
                        )
            )
            resp = render(
                request,
                "payment_gateways/pb_response_pay_error.xml",
                {
                    "error_msg": "Ошибка при оплате. "
                                 "Обратитесь в контакт-центр по "
                                 "тел. 0800211112"
                },
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
def okci_ep_terminal_view(request):

    is_valid, action, action_data = process_fam_request(request)

    if not is_valid:
        return HttpResponseBadRequest("Операция не поддерживается")

    if action == constants.EASYPAY_CHECK:
        template = 'payment_gateways/fam/response_1_check.xml'
        contract_num = action_data['Account']

        telegram_notification(
            message='Search (okci_ep_terminal_view) {0}'.format(
                contract_num
            )
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
                message='Проблема с подключением к Турнесу (Okci ep)'
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

        credit = search_okcicredit(
            cursor=cursor,
            contract_num=contract_num
        )

        conn.close()

        try:
            credit_row = credit[0]
        except Exception:
            telegram_notification(
                err='',
                message='Договор не найден - {0} (Okci ep)'.format(
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
                'Balance': str(credit_row[6]) if credit_row[6] > 0 else 0,
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

        telegram_notification(
            message='Pay (okci_ep_terminal_view) {0}'.format(
                contract_num
            )
        )

        p = OkciEasypayPayment.objects.filter(
            order_id=action_data['OrderId']
        )
        if p:
            telegram_notification(
                err='',
                message='Дубль платежа Okci {0}'.format(action_data['OrderId'])
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
                message='Проблема с подключением к Турнесу (Okci ep)'
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

        credit = search_okcicredit(
            cursor=cursor,
            contract_num=contract_num
        )

        conn.close()

        try:
            credit_row = credit[0]
        except Exception:
            telegram_notification(
                err='',
                message='Договор не найден - {0} (Okci ep)'.format(
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
            payment = OkciEasypayPayment.objects.create(
                service_id=action_data['ServiceId'],
                order_id=action_data['OrderId'],
                account=action_data['Account'],
                amount=action_data['Amount'],
                client_name=credit_row[2]
            )
            telegram_notification(
                message='Оплата кредита OKCI(ep)\n'
                        'Дог.{0}; Сумма {1}. Статус {2}'.format(
                            contract_num,
                            action_data['Amount'],
                            credit[0][4]
                        )
            )

        except Exception as e:
            telegram_notification(
                err=e,
                message='Ошибка при создании платежа (Okci ep)'
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
            'payment_id': str(payment.order_id)
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
            payment = OkciEasypayPayment.objects.get(
                order_id=action_data['PaymentId']
            )
        except Exception:
            telegram_notification(
                err='',
                message='Платеж не найден на сайте (Okci ep)'
            )
            ctx['status_code'] = -1
            ctx['status_detail'] = 'Платеж не найден'
            return render(
                request,
                template,
                ctx,
                content_type='application/xml'
            )

        telegram_notification(
            message='Confirm (okci_ep_terminal_view) {0}'.format(
                payment.account
            )
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
                message='Проблема с подключением к Турнесу (Okci ep)'
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
        credit = search_okcicredit(
            cursor=cursor,
            contract_num=payment.account
        )

        try:
            ipn = credit[0][5]
        except Exception as e:
            telegram_notification(
                err=e,
                message='Не указан ИНН (Okci ep)'
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
            "status": 59,
            "ibank": '60 (ПБ)'
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
                message='Проблема с сохранением '
                        'транзакции в Турнес. {0}'.format(str(data))
            )
            ctx['status_code'] = -1
            ctx['status_detail'] = 'Ошибка при оплате'
            return render(
                request,
                template,
                ctx,
                content_type='application/xml'
            )

        # save payment confirmation to site's DB
        payment.confirmed = True
        payment.confirmed_dt = datetime.now()
        payment.inrazpredelenie_id = lastrowid
        payment.save()

        try:
            with transaction.atomic():
                query = """
                    SELECT mbank.RunRazpredelenieOkciOnline("{0}");
                """.format(
                    date.today()
                )
                cursor.execute(query)
                conn.commit()
        except Exception as e:
            telegram_notification(
                err=e,
                message='Проблема с разнесением OKCI (ep)'
                        'платежа (status {0})'.format(
                            str(credit[0][4])
                        )
            )

        conn.close()

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
                payment = OkciEasypayPayment.objects.select_for_update().get(
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
                message='Ошибка при отмене платежа (Okci ep)'
            )
            ctx['status_code'] = -1
            ctx['status_detail'] = 'Платеж не найден'

        return render(request, template, ctx, content_type='application/xml')

    else:
        resp = HttpResponse()

    return resp
