import xmltodict

from payment_gateways import constants


def process_pb_request(request):
    """
    Check if PB terminal request is valid

    :param request: request object
    :return: is_valid, action, xml_data
    """

    SUPPORTED_ACTIONS = {
        constants.PB_SEARCH,
        constants.PB_PAY,
    }

    is_valid, action, xml_data = False, None, {}

    try:
        xml_data = xmltodict.parse(request.body)
    except Exception:
        return is_valid, action, xml_data

    try:
        action = xml_data['Transfer']['@action']
        if action not in SUPPORTED_ACTIONS:
            raise KeyError
    except (KeyError, TypeError):
        return is_valid, action, xml_data

    is_valid = True
    return is_valid, action, xml_data


def process_easypay_request(request):
    """

    :param request: body of request
    :return: is_valid, action, request_data
    """
    SUPPORTED_ACTIONS = [
        constants.EASYPAY_CHECK,
        constants.EASYPAY_PAYMENT,
        constants.EASYPAY_CONFIRM,
        constants.EASYPAY_CANCEL
    ]

    REQUIRED_FIELDS = {
        constants.EASYPAY_CHECK: {'ServiceId',
                                  'Account'},
        constants.EASYPAY_PAYMENT: {'ServiceId',
                                    'OrderId',
                                    'Account',
                                    'Amount'},
        constants.EASYPAY_CONFIRM: {'ServiceId',
                                    'PaymentId'},
        constants.EASYPAY_CANCEL: {'ServiceId',
                                   'PaymentId'}
    }

    is_valid, action, action_data = False, None, {}
    try:
        xml_data = xmltodict.parse(request.body)
    except Exception:
        return is_valid, action, action_data

    if 'Request' not in xml_data:
        return is_valid, action, action_data

    req_data = xml_data['Request']

    for x in SUPPORTED_ACTIONS:
        try:
            action_data = req_data[x]
            action = x
            break
        except KeyError:
            continue

    if action is None:
        return is_valid, action, action_data

    # verify fields
    action_data_keys = set(action_data.keys())
    missing_keys = REQUIRED_FIELDS[action] - action_data_keys
    if missing_keys:
        return is_valid, action, action_data

    is_valid = True
    return is_valid, action, action_data
