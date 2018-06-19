from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect
from django.urls import reverse
from django.utils.translation import ugettext_lazy as _

from communication.models import SuccessFormStatic


def success_message(request, id_mess, redirect_url=None):
    success = SuccessFormStatic.objects.filter(id=id_mess).first()
    if not redirect_url:
        redirect = request.META.get('HTTP_REFERER')
        if redirect:
            redirect = redirect.split('/')[-2]
            if redirect == 'resume':
                redirect = reverse('job').split('/')[-2]
            else:
                redirect = None
    else:
        redirect = redirect_url
    return render(
        request,
        'form-success.html',
        {
            'success': success,
            'previous_page': redirect
        }
    )
