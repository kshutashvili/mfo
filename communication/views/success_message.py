from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect
from django.urls import reverse
from django.utils.translation import ugettext_lazy as _

from communication.models import SuccessFormStatic


def success_message(request, id_mess):
    success = SuccessFormStatic.objects.filter(id=id_mess).first()
    previous_page = request.META.get('HTTP_REFERER')
    if previous_page:
        previous_page = previous_page.split('/')[-2]
        if previous_page == 'resume':
            previous_page = reverse('job').split('/')[-2]
    return render(request, 'form-success.html', {'success':success,
                                                 'previous_page':previous_page})

