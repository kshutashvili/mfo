import json
import os
from wsgiref.util import FileWrapper

from django.shortcuts import render
from django.template.loader import render_to_string
from django.http import (HttpResponse, HttpResponseRedirect, JsonResponse,
                         HttpResponseBadRequest)
from django.utils.translation import ugettext_lazy as _
from django.template.defaultfilters import urlencode, force_escape
from django.utils.safestring import mark_safe
from django.utils import translation
from django.views.generic.base import TemplateView
from django.urls import reverse
from django.http import Http404

from content.models import Spoiler, StaticPage, GetCredit, MenuAboutItem,\
                           MainPageStatic, IndexPageStatic, StaticPageDefault
from credit.models import CreditRate, CreditRateUp
from communication.models import Response, QuestionComment, UserQuestion,\
                                 QuestionConfig, CallbackSuccessForm,\
                                 SocialNetUnderHeader
from communication.forms import WriteCommentForm, WriteQuestionForm
from department.models import Department
from efin.settings import GOOGLE_MAPS_API_KEY, BASE_DIR
from content.helpers import get_city_name, process_bid, clear_contact_phone
from bids.models import Bid
from users.forms import RegisterNumberForm
from users.models import Profile
from communication.views.sms import sms


def pages(request, page_url):
    page = StaticPage.objects.filter(link=page_url).first()
    template = 'spoiler-page.html'
    if not page:
        page = StaticPageDefault.objects.filter(link=page_url).first()
        if not page:
            raise Http404
        template = 'default.html'
    menu_about = MenuAboutItem.objects.all()
    return render(request, template, {'page':page,
                                      'menu_about':menu_about})


def main(request):
    any_param = request.GET.get('any_param', '')
    wm_id = request.GET.get('wm_id', '')

    city = get_city_name(request)
    main = MainPageStatic.get_solo()
    nets = SocialNetUnderHeader.objects.all()
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
    return render(request, 'main.html', {'main': main,
                                         'departments': departments,
                                         'nets': nets,
                                         'wm_id': wm_id,
                                         'any_param': any_param,
                                         'column_list': column_list,
                                         'user_city': city if city else 'Другой город'})


def index(request):
    city = get_city_name(request)
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
    form = RegisterNumberForm()
    return render(request, 'index.html', {'index':index,
                                          'main':main,
                                          'form':form,
                                          'user_city': city if city else 'Другой город',
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
        sum_min = obj.credit_rate.sum_min if not obj.credit_rate.is_insurance \
                                          else obj.credit_rate.sum_min / 1.25
        sum_max = obj.credit_rate.sum_max if not obj.credit_rate.is_insurance \
                                          else obj.credit_rate.sum_max / 1.25
        result[str(obj.id)] = {'term_min':obj.credit_rate.term_min,
                               'term_max':obj.credit_rate.term_max,
                               'sum_min':sum_min,
                               'sum_max':sum_max}
    return JsonResponse(result)


def agreement(request):
    menu_about = MenuAboutItem.objects.all()
    return render(request, 'default.html', {'menu_about':menu_about})


def credit_calculator(request, rate_id, term, summ):
    rate = CreditRate.objects.filter(id=rate_id).first()
    if rate.is_insurance:
        summ /= 0.8
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
        context['form'] = RegisterNumberForm()
        if kwargs.get('status_message'):
            context['status_message'] = kwargs.get('status_message')

        return context


def save_credit_request(request):
    if request.method == 'POST':
        try:
            credit_sum = int(request.POST.get('credit_sum', 0))
        except ValueError:
            credit_sum = 0
        # create new Bid
        new_bid = Bid.objects.create(
            credit_sum=credit_sum,
            termin=request.POST.get('termin'),
            termin_type=request.POST.get('term_type'),
            city=request.POST.get('city'),
            wm_id=request.POST.get('wm_id', ''),
            any_param=request.POST.get('any_param', '')
        )
        new_bid.save()

        if new_bid.id:
            # set bid's id to session for accesing in other page
            request.session["bid_id"] = new_bid.id

        # for ajax query from index.html shoudn't redirect
        if request.POST.get('no_redirect', False):
            return JsonResponse({'status':'200',
                                 'bid_id':new_bid.id})
        else:
            return HttpResponseRedirect(redirect_to=request.POST.get('callback'))
    else:
        return HttpResponseBadRequest()


def request_callback(request):
    if request.method == 'POST':
        bid_id = request.POST.get("bid_id", None)
        contact_phone = request.POST.get("contact_phone")
        clean_phone = clear_contact_phone(contact_phone)

        if bid_id:
            # if Bid has been created in save_credit_request function
            if Bid.objects.filter(id=int(bid_id)).exists():
                bid = Bid.objects.get(id=int(bid_id))
                bid.contact_phone = clean_phone
                bid.name = request.POST.get("client_name")
                bid.save()
                process_bid(bid)
                request.session['bid_id'] = bid.id
            else:
                new_bid = Bid.objects.create(
                    city=request.POST.get('city'),
                    name=request.POST.get("client_name"),
                    contact_phone=clean_phone
                )
                new_bid.save()
                process_bid(new_bid)
                request.session['bid_id'] = new_bid.id
        else:
            new_bid = Bid.objects.create(
                city=request.POST.get('city'),
                name=request.POST.get("client_name"),
                contact_phone=clean_phone
            )
            new_bid.save()
            process_bid(new_bid)
            request.session['bid_id'] = new_bid.id

        # for NEXT COMMITS
        # return sms(request, "+380950968326", reverse('callback_verify'))

        callback_success = CallbackSuccessForm.get_solo()
        url = reverse('success', kwargs={
            'id_mess': callback_success.success.id,
            'redirect_url': 'main'
        })
        return HttpResponseRedirect(url)

    return HttpResponseBadRequest()


class CallbackSuccessView(TemplateView):
    template_name = "form-success.html"


def comment_add(request):
    if request.method == 'POST':
        content = {'content':request.POST.get('content')}
        comment_form = WriteCommentForm(content)
        if comment_form.is_valid():
            question = UserQuestion.objects.filter(id=request.POST.get('id_quest')).first()
            comment = QuestionComment(content=comment_form.cleaned_data.get('content'))
            comment.save()
            question.comments.add(comment)
            question.save()
            result = render(request, 'ajax_generate/comment_generate.html', {'comment':comment})
            return HttpResponse(result)
        else:
            result = 'fail'
            return HttpResponse(result)
    else:
        result = 'fail'
        return HttpResponse(result)


def question_add(request):
    if request.method == 'POST':
        question_form = WriteQuestionForm(request.POST, request.FILES)
        if question_form.is_valid():
            user = Profile.objects.filter(user=request.user).first()
            content = question_form.cleaned_data.get('support_text')
            file = question_form.cleaned_data.get('file')
            question = UserQuestion.objects.create(content=content,
                                                   file=file,
                                                   user=user,
                                                   is_read='force read')
            url = reverse('profile', kwargs={'active':'mess'})
            return HttpResponseRedirect(url)
        else:
            return HttpResponseBadRequest()
    else:
        return HttpResponseBadRequest()


def question_generate(request):
    try:
        page = request.GET.get('page')
        start = int(page) * 8 - 8
        end = int(page) * 8
        user = Profile.objects.filter(user=request.user).first()
        questions = UserQuestion.objects.filter(user=user).order_by('updated_at').reverse()[start:end]
        str1 = render_to_string('ajax_generate/quest_generate.html', {'questions':questions})
        str2 = render_to_string('ajax_generate/chat_generate.html', {'questions':questions})
        result = 'ёёёёё'.join([str1, str2])
        return HttpResponse(result)
    except:
        result = 'fail'
        return HttpResponse(result)
