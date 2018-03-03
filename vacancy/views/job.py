from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.utils.translation import ugettext_lazy as _

from vacancy.models import Category

def job(request):
    categories = Category.objects.all()
    return render(request, 'job.html', {'categories':categories})

