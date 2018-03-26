from django.shortcuts import render
from django.http import (HttpResponse, HttpResponseRedirect, JsonResponse,
                         HttpResponseBadRequest)
from django.utils.translation import ugettext_lazy as _
from django.utils.safestring import mark_safe
from django.urls import reverse
from django.http import Http404 
from django.contrib.auth.models import User

from users.models import Profile
from users.forms import SetPasswordForm
from communication.models import UserExistMessage


def register(request):
    if request.method == 'POST':
        phone = request.POST.get('phone', '')
        phone = clear_phone(phone)
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



def clear_phone(phone):
    phone = phone.replace(' -_()+','')
    for i in range(0,100):
        if len(phone) != 9:
            phone = phone[1:]
        else:
            break
    return phone

