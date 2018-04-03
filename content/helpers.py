import requests

from django.contrib.gis.geoip2 import GeoIP2
from django.conf import settings


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

    saleshub_URI = "https://saleshub.co.ua/api/v1/leads/"
    data = {
        "partner_name": "website",
        "contact_phone": bid.contact_phone,
        "city": bid.city,
        "first_name": bid.name,
        # "first_name": " ".join(bid.name.split(" ")[0]),
        # "last_name": " ".join(bid.name.split(" ")[1]),
        "credit_sum": bid.credit_sum,
        "key": "46de62b4db97e9f855129f9f5edcd595"
    }

    r = requests.post(
        saleshub_URI,
        data=data
    )

    print(r.json())
