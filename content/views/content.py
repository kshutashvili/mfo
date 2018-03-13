import json
import os
from wsgiref.util import FileWrapper

from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.utils.translation import ugettext_lazy as _
from django.template.defaultfilters import urlencode, force_escape
from django.utils.safestring import mark_safe
from django.utils import translation

from content.models import Spoiler, StaticPage, GetCredit, MenuAboutItem,\
                           MainPageStatic, IndexPageStatic
from credit.models import CreditRate, CreditRateUp
from communication.models import Response
from department.models import Department
from efin.settings import GOOGLE_MAPS_API_KEY, BASE_DIR


def pages(request, page_url):
    page = StaticPage.objects.filter(link=page_url).first()
    return render(request, 'spoiler-page.html', {'page':page})


def main(request):
    main = MainPageStatic.get_solo()
    departments = []
    for obj in main.departments.get_queryset():
        if obj.city not in departments:
            departments.append(obj.city)
    return render(request, 'main.html', {'main':main,
                                         'departments':departments})


def index(request):
    index = IndexPageStatic.get_solo()
    main = MainPageStatic.get_solo()
    departments = []
    for obj in index.departments.get_queryset():
        if obj.city not in departments:
            departments.append(obj.city)
    return render(request, 'index.html', {'index':index,
                                          'main':main,
                                          'departments':departments})


def departments_generate(request, dep_id):
    if translation.get_language() == 'ua':
        lang = 'ua'
    else:
        lang = 'ru'
    city_departs = dict()
    departments = Department.objects.filter(city=dep_id)
    for obj in departments:
        #link = mark_safe('https://www.google.com/maps/embed/v1/place?key=%s&q=%s,%s' % \
        #                (GOOGLE_MAPS_API_KEY,
        #                obj.geolocation.lat,
        #                obj.geolocation.lon))
        address = obj.address if lang == 'ru' else obj.address_ua
        city_departs[obj.id] = {'city':obj.city,
                                'lats':{'lat':obj.geolocation.lat,
                                        'lng':obj.geolocation.lon},
                                'address':address,
                                'schedule':obj.schedule,
                                'email':obj.email,
                                'phone':obj.phone}
    return JsonResponse(city_departs)


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
    if not term:
        term = rate.term_min
    if not summ:
        summ = rate.sum_min
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
    if not rate_percent:
        return 0
    else:
        on_loan = (1 + rate_percent) ** term
        res = round(summ * rate_percent * on_loan / (on_loan - 1) , 2)
        result = {'result':res}
        return JsonResponse(result)


def download_pdf(request, spoiler_id):
    spoiler = Spoiler.objects.filter(id=spoiler_id).first()
    if os.path.exists(spoiler.file.path):
        with open(spoiler.file.path, 'rb') as fh:
            response = HttpResponse(fh.read(), content_type="application/pdf")
            response['Content-Disposition'] = 'attachment; filename=%s.pdf' % os.path.basename(spoiler.file.path)
            return response
    raise Http404


def open_pdf(request, spoiler_id):
    spoiler = Spoiler.objects.filter(id=spoiler_id).first()
    file_data = open(spoiler.file.path, 'rb').read()
    return HttpResponse(file_data, content_type='application/pdf')


def translate(request, lang_code):
    translation.activate(lang_code)
    request.session[translation.LANGUAGE_SESSION_KEY] = lang_code
    return HttpResponseRedirect("/")

