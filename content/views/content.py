import json

from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.utils.translation import ugettext_lazy as _
from django.template.defaultfilters import urlencode, force_escape
from django.utils.safestring import mark_safe

from content.models import Spoiler, StaticPage, GetCredit, MenuAboutItem
from credit.models import CreditRate, CreditRateUp
from communication.models import Response
from department.models import Department
from efin.settings import GOOGLE_MAPS_API_KEY, BASE_DIR


def pages(request, page_url):
    page = StaticPage.objects.filter(link=page_url).first()
    return render(request, 'spoiler-page.html', {'page':page})


def main(request):
    return render(request, 'main.html', {})


def index(request):
    return render(request, 'index.html', {})


def departments_generate(request, dep_id):
    departments = Department.objects.filter(id=int(dep_id))
    result = dict()
    for obj in departments:
        link = mark_safe('https://www.google.com/maps/embed/v1/place?key=%s&q=%s,%s' % \
                         (GOOGLE_MAPS_API_KEY,
                          obj.geolocation.lat,
                          obj.geolocation.lon))
        result[obj.id] = {'city':obj.city,
                        'address':obj.address,
                        'schedule':obj.schedule,
                        'email':obj.email,
                        'phone':obj.phone,
                        'link':link}
    return JsonResponse(result)


def slider_filler(request):
    data = CreditRateUp.objects.all()
    result = dict()
    for obj in data:
        result[str(obj.id)] = {'term_min':obj.credit_rate.term_min,
                               'term_max':obj.credit_rate.term_max,
                               'sum_min':obj.credit_rate.sum_min,
                               'sum_max':obj.credit_rate.sum_max}
    return JsonResponse(result)


def agreement(request):
    menu_about = MenuAboutItem.objects.all()
    return render(request, 'default.html', {'menu_about':menu_about})


def credit_calculator(request, rate_id, term, summ):
    rate = CreditRate.objects.filter(id=rate_id).first()
    json_data = rate.rate_file.read()
    data = json.loads(json_data.decode('utf-8'))
    key = ''
    for obj in sorted(map(int, data.keys())):
        if summ >= obj:
            continue
        else:
            key = str(obj)
    else:
        if not key:
            key = str(sorted(map(int, data.keys()))[-1])
    percents = data[key]
    for obj in sorted(map(int, percents.keys())):
        if term >= int(obj):
            rate_percent = percents[str(obj)]
        else:
            break
    if rate.term_type:
        rate_percent /= 12
    else:
        rate_percent /= 52
    # rate_percent , term, summ
    if not rate_percent or not term or not summ:
        return 0
    else:
        on_loan = (1 + rate_percent) ** term
        res = round(summ * ( rate_percent * on_loan)/(on_loan - 1), 2)
        result = {'result':res}
        return JsonResponse(result)

