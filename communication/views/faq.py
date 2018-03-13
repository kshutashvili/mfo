from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.utils.translation import ugettext_lazy as _
from django.utils.translation import activate

from communication.models import FaqPageStatic


def faq(request):
    faq = FaqPageStatic.get_solo()
    length = faq.faq_categories.values_list().count()
    column_list = [0, 0, 0]
    while length > 0:    
        for i in range(0, 3):
            if length > 0:
                column_list[i] += 1
                length -= 1
    return render(request, 'faq.html', {'faq':faq,
                                        'column_list':column_list})

