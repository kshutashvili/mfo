from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect
from django.utils.translation import ugettext_lazy as _

from content.models import Spoiler, StaticPage


def pages(request, page_url):
    page = StaticPage.objects.filter(link=page_url).first()
    return render(request, 'spoiler-page.html', {'page':page})

