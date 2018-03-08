from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.utils.translation import ugettext_lazy as _

from communication.models import FaqCategory


def faq(request):
    faq_categories = FaqCategory.objects.all()
    length = FaqCategory.objects.count()
    column_list = [0, 0, 0]
    while length > 0:    
        for i in range(0, 3):
            if length > 0:
                column_list[i] += 1
                length -= 1
    print(column_list)
    return render(request, 'faq.html', {'faq_categories':faq_categories,
                                        'column_list':column_list})

