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
