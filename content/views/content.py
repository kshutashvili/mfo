import json
import os
from wsgiref.util import FileWrapper

from django.shortcuts import render
from django.http import (HttpResponse, HttpResponseRedirect, JsonResponse,
                         HttpResponseBadRequest)
from django.utils.translation import ugettext_lazy as _
from django.template.defaultfilters import urlencode, force_escape
from django.utils.safestring import mark_safe
from django.utils import translation
from django.views.generic.base import TemplateView
from django.urls import reverse

from content.models import Spoiler, StaticPage, GetCredit, MenuAboutItem,\
                           MainPageStatic, IndexPageStatic, StaticPageDefault
from credit.models import CreditRate, CreditRateUp
from communication.models import Response
from department.models import Department
from efin.settings import GOOGLE_MAPS_API_KEY, BASE_DIR
from content.helpers import get_city_name
from bids.models import Bid


def pages(request, page_url):
    page = StaticPage.objects.filter(link=page_url).first()
    template = 'spoiler-page.html'
    if not page:
        page = StaticPageDefault.objects.filter(link=page_url).first()
        template = 'default.html'
    menu_about = MenuAboutItem.objects.all()
    return render(request, template, {'page':page,
                                      'menu_about':menu_about})


def main(request):
    city = get_city_name(request)
    main = MainPageStatic.get_solo()
    departments = []
    for obj in main.departments.get_queryset():
        if obj.city not in departments:
            departments.append(obj.city)
    departments = sorted(departments)
    length = len(departments)
    column_list = [0, 0, 0, 0]
    while length > 0:
        for i in range(0, 4):
            if length > 0:
                column_list[i] += 1
                length -= 1
    return render(request, 'main.html', {'main':main,
                                         'departments':departments,
                                         'column_list':column_list,
                                         'user_city': city if city else 'Другой город'
                                         })


def index(request):
    index = IndexPageStatic.get_solo()
    main = MainPageStatic.get_solo()
    departments = []
    for obj in index.departments.get_queryset():
        if obj.city not in departments:
            departments.append(obj.city)
    departments = sorted(departments)
    length = len(departments)
    column_list = [0, 0, 0, 0]
    while length > 0:
        for i in range(0, 4):
            if length > 0:
                column_list[i] += 1
                length -= 1
    return render(request, 'index.html', {'index':index,
                                          'main':main,
                                          'departments':departments,
                                          'column_list':column_list})


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


class CallbackView(TemplateView):
    template_name = "form-callback.html"

    def get_context_data(self, **kwargs):
        context = super(CallbackView, self).get_context_data()

        bid_id = None
        # get bid's ID form session which set in save_credit_request function
        if self.request.session.has_key('bid_id'):
           bid_id = self.request.session.get('bid_id')
           del self.request.session['bid_id']

        context['bid_id'] = bid_id

        city = get_city_name(self.request)
        context['city'] = city or "Другой город"

        return context


def save_credit_request(request):
    if request.method == 'POST':
        # create new Bid
        new_bid = Bid.objects.create(
            credit_sum=request.POST.get('credit_sum', 0),
            termin=request.POST.get('termin'),
            termin_type=request.POST.get('term_type'),
            city=request.POST.get('city')
        )
        new_bid.save()

        if new_bid.id:
            # set bid's id to session for accesing in other page
            request.session["bid_id"] = new_bid.id
        return HttpResponseRedirect(redirect_to=request.POST.get('callback'))


def request_callback(request):
    if request.method == 'POST':
        bid_id = request.POST.get("bid_id", None)
        if bid_id:
            # if Bid has been created in save_credit_request function
            if Bid.objects.filter(id=int(bid_id)).exists():
                bid = Bid.objects.get(id=int(bid_id))
                bid.contact_phone = request.POST.get("contact_phone")
                bid.name = request.POST.get("client_name")
                bid.save()
            else:
                new_bid = Bid.objects.create(
                    city=request.POST.get('city'),
                    name=request.POST.get("client_name"),
                    contact_phone=request.POST.get("contact_phone")
                )
                new_bid.save()
        else:
            new_bid = Bid.objects.create(
                city=request.POST.get('city'),
                name=request.POST.get("client_name"),
                contact_phone=request.POST.get("contact_phone")
            )
            new_bid.save()
        return HttpResponseRedirect(redirect_to=reverse('callback_success'))
    return HttpResponseBadRequest()


class CallbackSuccessView(TemplateView):
    template_name = "form-success.html"
