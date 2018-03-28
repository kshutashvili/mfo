from django.shortcuts import render
from django.http import (HttpResponse, HttpResponseRedirect, JsonResponse,
                         HttpResponseBadRequest)
from django.utils.translation import ugettext_lazy as _
from django.utils.safestring import mark_safe
from django.urls import reverse
from django.http import Http404 
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout

from users.models import Profile
from users.forms import SetPasswordForm, RegisterNumberForm, LoginForm
from communication.models import UserExistMessage, UserQuestion
from communication.forms import WriteCommentForm, WriteQuestionForm


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
        comment_form = WriteCommentForm()
        question_form = WriteQuestionForm()
        user = Profile.objects.filter(user=request.user).first()
        count = UserQuestion.objects.count()
        pagination = int(count / 8)
        if count % 8 != 0:
            pagination += 1
        pagination = [0 for x in range(0, pagination)]
        questions = UserQuestion.objects.filter(user=user).order_by('updated_at').reverse()[:8]
        return render(request, 'private-profile.html', {'questions':questions,
                                                        'active':active,
                                                        'question_form':question_form,
                                                        'pagination':pagination,
                                                        'comment_form':comment_form})

