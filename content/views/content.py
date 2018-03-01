from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.utils.translation import ugettext_lazy as _
from django.template.defaultfilters import urlencode, force_escape
from django.utils.safestring import mark_safe

from content.models import Spoiler, StaticPage
from communication.models import Response
from department.models import Department


def pages(request, page_url):
    page = StaticPage.objects.filter(link=page_url).first()
    return render(request, 'spoiler-page.html', {'page':page})


def main(request):
    responces = Response.objects.all()
    departments = Department.objects.all()
    department_cities = []
    for obj in departments:
        if obj.city not in department_cities:
            department_cities.append(obj.city)
    return render(request, 'main.html', {'responces':responces,
                                         'department_cities':department_cities})


def departments_generate(request, city):
    departments = Department.objects.filter(city=city)
    result = dict()
    for obj in departments:
        link = mark_safe('https://maps.google.com/maps?t=m&amp;q=%s' % \
                         urlencode(force_escape(obj.city + obj.address))) 
        result[obj.city] = {'city':obj.city,
                            'address':obj.address,
                            'schedule':obj.schedule,
                            'email':obj.email,
                            'phone':obj.phone,
                            'link':link}
    print(link)
    return JsonResponse(result)
