from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.utils.translation import ugettext_lazy as _
from django.template.defaultfilters import urlencode, force_escape
from django.utils.safestring import mark_safe

from content.models import Spoiler, StaticPage, GetCredit, MenuAboutItem
from credit.models import CreditRate, CreditRateUp
from communication.models import Response
from department.models import Department
from efin.settings import GOOGLE_MAPS_API_KEY


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
        city = obj.address.split(',')[-2].strip()
        result[obj.id] = {'city':city,
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
        result[str(obj.id)] = {'term_min':obj.credit_rate.get_term_min_days(),
                               'term_max':obj.credit_rate.get_term_max_days(),
                               'sum_min':obj.credit_rate.sum_min,
                               'sum_max':obj.credit_rate.sum_max}
    return JsonResponse(result)


def agreement(request):
    menu_about = MenuAboutItem.objects.all()
    return render(request, 'default.html', {'menu_about':menu_about})