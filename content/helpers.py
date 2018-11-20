from datetime import date

import requests

from django.contrib.gis.geoip2 import GeoIP2
from django.conf import settings

from payment_gateways.utils import create_database_connection


def get_client_ip(request):
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip


def get_coords_by_ip(request):
    g = GeoIP2()
    ip = get_client_ip(request)
    default_kiev_ip = '92.244.113.0'
    try:
        city_json = g.city(ip)
    except Exception as e:
        # raise if ip == 127.0.0.1
        # print(e)
        city_json = g.city(default_kiev_ip)

    # example of city_json:
    # {'country_name': 'Ukraine',
    #  'dma_code': None,
    #  'postal_code': '01044',
    #  'region': '30',
    #  'time_zone': 'Europe/Kiev',
    #  'latitude': 50.4333,
    #  'country_code': 'UA',
    #  'longitude': 30.5167,
    #  'city': 'Kiev'}

    return city_json


def get_city_name(request):
    city = None
    json_with_coords = get_coords_by_ip(request)

    if json_with_coords["city"]:
        return json_with_coords["city"]

    google_url = "https://maps.googleapis.com/maps/api/geocode/json?latlng={0}&key={1}"

    r = requests.get(
        google_url.format(
            # 50.4333,30.5167 without space between coords
            "{},{}".format(
                json_with_coords["latitude"],
                json_with_coords["longitude"]
            ),
            settings.GOOGLE_MAPS_API_KEY
        )
    )

    try:
        address_components = r.json()["results"][0]["address_components"]
    except Exception as e:
        # print(e)
        return city

    # search city name
    for component in address_components:
        if "locality" in component["types"]:
            city = component["long_name"]

    return city


def process_bid(bid):
    # send new Bid to Saleshub site

    partner_dict = {
        "website": {
            "partner_name": "website",
            "key": "46de62b4db97e9f855129f9f5edcd595",
        },
        "linkprofit": {
            "partner_name": "linkprofit",
            "key": "a47867d776f2fdbab60d9b7d0c7862c5"
        },
        "salesdoubler": {
            "partner_name": "salesdoubler",
            "key": "acbf4b4fb0556f9095b7a4fec43e97c9"
        },
        "doaffiliate": {
            "partner_name": "doaffiliate",
            "key": "d76d942bd38e59615d65a1c3f3b618e0"
        }
    }
    partner = "website"
    if bid.wm_id and bid.any_param:
        partner = "linkprofit"
    if bid.aff_sub and bid.aff_id:
        partner = "salesdoubler"
    if bid.v:
        partner = "doaffiliate"

    saleshub_URI = "https://saleshub.co.ua/api/v1/leads/"
    data = {
        "partner_name": partner_dict[partner]["partner_name"],
        "contact_phone": bid.contact_phone,
        "city": bid.city,
        "first_name": bid.name,
        "credit_sum": bid.credit_sum,
        "key": partner_dict[partner]["key"],
        "site_bid_id": bid.id
    }

    r = requests.post(
        saleshub_URI,
        data=data
    )

    # print(r.json())


def clear_contact_phone(contact_phone):
    return contact_phone.replace(
        "+", ""
    ).replace(
        "(", ""
    ).replace(
        ")", ""
    ).replace(
        " ", ""
    ).replace(
        "_", ""
    )


def check_blacklist(itn=None, mobile_phone=None,
                    passseria=None, passnumber=None):
    saleshub_URI = "https://saleshub.co.ua/api/v1/blacklist/"
    data = {
        "itn": itn,
        "mobile_phone": mobile_phone,
        "passseria": passseria,
        "passnumber": passnumber,
    }

    r = requests.post(
        saleshub_URI,
        data=data
    )

    return r.json()


def get_application_count():
    print("date", str(date.today()), date.today())
    try:
        conn, cursor = create_database_connection(
            host=settings.TURNES_HOST,
            user=settings.TURNES_USER,
            password=settings.TURNES_PASSWORD,
            db=settings.TURNES_DATABASE
        )
    except Exception:
        return None

    query = """
        SELECT count(1)
        FROM mbank.tstatuses
        WHERE date(dt_created) = '{0}'
          AND is_last = 1;
    """.format(str(date.today()))
    cursor.execute(query)
    data = cursor.fetchall()

    print("data", data)
    if data:
        return data[0][0]
    else:
        return None
