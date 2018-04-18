from django.shortcuts import render
from django.http import (HttpResponse, HttpResponseRedirect, JsonResponse,
                         HttpResponseBadRequest)
from django.utils.translation import ugettext_lazy as _
from django.utils.safestring import mark_safe
from django.urls import reverse
from django.http import Http404 
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.core.validators import validate_email
from django.core.exceptions import ValidationError

from users.models import Profile
from users.forms import SetPasswordForm, RegisterNumberForm, LoginForm
from communication.models import UserExistMessage, UserQuestion
from communication.forms import WriteCommentForm, WriteQuestionForm
from users.utils import test_user_turnes


def register(request):
    if request.method == 'POST':
        form = RegisterNumberForm(request.POST)
        if form.is_valid():
            phone = form.cleaned_data.get('phone')
            user_exist = Profile.objects.filter(phone=phone).first()
            if user_exist and user_exist.user.is_active:
                id_mess = UserExistMessage.get_solo().page.id
                url = reverse('success', kwargs={'redirect_url':'login',
                                                 'id_mess':id_mess})
                return HttpResponseRedirect(url)
            elif user_exist and user_exist.user.is_active == False:
                url = reverse('sms', kwargs={'phone':phone})
                return HttpResponseRedirect(url)
            else:
                user = Profile()
                us = User(username=phone)
                us.is_active = False
                us.save()
                user.user = us
                user.phone = phone
                user.save()
                url = reverse('sms', kwargs={'phone':phone})
                return HttpResponseRedirect(url)
        else:
            status_message = _('Неправильный номер')
            url = reverse('callback', kwargs={'status_message':status_message})
            return HttpResponseRedirect(url)


def set_password(request):
    if request.method == 'GET':
        form = SetPasswordForm()
        status_message = None
    elif request.method == 'POST':
        form = SetPasswordForm(request.POST)
        if form.is_valid():
            user = Profile.objects.filter(phone=request.session.get('phone','')).first()
            user.user.set_password(form.cleaned_data.get('password'))
            user.user.save()
            return HttpResponseRedirect(reverse('login'))
        else:
            status_message = form.errors.get('password','')
    return render(request, 'enter-password.html', {'form':form,
                                                   'status_message':status_message})


def user_login(request, status_message=None):
    if request.method == 'POST':
        form = LoginForm()
        data = {'phone':request.POST.get('username')}
        number_form = RegisterNumberForm(data)
        if number_form.is_valid():
            data = {'username':number_form.cleaned_data.get('phone'),
                    'password':request.POST.get('password')}
            form = LoginForm(data)
            if form.is_valid():
                username = form.cleaned_data.get('username')
                password = form.cleaned_data.get('password')
                user = authenticate(username=username, password=password)
                if user is not None:
                    login(request, user)
                    if request.POST.get('remember_me') is not None:
                        request.session.set_expiry(0)
                    return HttpResponseRedirect(reverse('profile'))
                else:
                    status_message = _("Неправильный номер или пароль")
                    url = reverse('login', kwargs={'status_message':status_message})
                    return HttpResponseRedirect(url)
            else:
                status_message = _("Неправильный номер или пароль")
                url = reverse('login', kwargs={'status_message':status_message})
                return HttpResponseRedirect(url)
        else:
            status_message = _('Неправильный номер')
            url = reverse('login', kwargs={'status_message':status_message})
            return HttpResponseRedirect(url)
    elif request.method == 'GET':
        form = LoginForm()
        return render(request, 'enter.html', {'form':form,
                                              'status_message':status_message})


def user_logout(request):
    logout(request)
    return HttpResponseRedirect(reverse('login'))


def profile(request, active=None):
    if request.method == 'GET':
        turnes_profile = test_user_turnes()

        profile = Profile.objects.filter(user=request.user).first()
        comment_form = WriteCommentForm()
        question_form = WriteQuestionForm()
        user = Profile.objects.filter(user=request.user).first()
        count = UserQuestion.objects.count()
        pagination = int(count / 8)
        if count % 8 != 0:
            pagination += 1
        pagination = [0 for x in range(0, pagination)]
        questions = UserQuestion.objects.filter(user=user).select_related().order_by('is_read', 'updated_at').reverse()
        count_not_read_questions = 0
        for obj in questions:
            if not obj.is_read == 'read':
                count_not_read_questions += 1
        questions = questions[:8]
        return render(request, 'private-profile.html', {'questions':questions,
                                                        'active':active,
                                                        'profile':profile,
                                                        'turnes_profile':turnes_profile,
                                                        'count_not_read_questions':count_not_read_questions,
                                                        'question_form':question_form,
                                                        'pagination':pagination,
                                                        'comment_form':comment_form})


def alter_profile(request):
    if request.method == 'POST':
        field = request.POST.get('field_name')

        if field == 'phone':
            phone = {'phone':request.POST.get('field_value')}
            number_form = RegisterNumberForm(phone)
            if number_form.is_valid():
                if number_form.cleaned_data.get('phone') != request.user.username:
                    url = reverse('sms', kwargs={'phone':number_form.cleaned_data.get('phone')})
                    result = {'url':url}
                    return JsonResponse(result)
                else:
                    return JsonResponse({'phone':number_form.cleaned_data.get('phone')})

            else:
                result = {'status':'500',
                          'status_message':_('Неправильный номер телефона')}
                return JsonResponse(result)

        elif field == 'email':
            email = request.POST.get('field_value')
            try:
                validate_email(email)
                if email != request.user.email:
                    request.session['email'] = email
                    url = reverse('change_email')
                    result = {'url':url}
                    return JsonResponse(result)
                else:
                    return JsonResponse({})

            except ValidationError:
                result = {'status':'500',
                          'status_message':_('Неправильный электронный адрес')}
                return JsonResponse(result)

        elif field == 'authy':
            profile = Profile.objects.filter(user=request.user).first()
            profile.two_authy = True if profile.two_authy == False else False
            profile.save()
            return JsonResponse({'status':'200'})

    else:
        return HttpResponseBadRequest()


def message_read(request):
    if request.method == 'POST':
        question = UserQuestion.objects.filter(id=request.POST.get('id_quest')).first()
        # choices: 'read', '!read', 'force read'
        question.is_read = 'force read'
        question.save()
        result = {'status':'200'}
        return JsonResponse(result)
    else:
        result = {'status':'500'}
        return JsonResponse(result)

