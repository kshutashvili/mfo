from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.utils.translation import ugettext_lazy as _

from communication.models import BlogItem

def blog_item(request, item_id):
    article = BlogItem.objects.filter(id=item_id).first()
    return render(request, 'blog-item.html', {'article':article})


def blog(request):
    articles = BlogItem.objects.order_by('date').reverse()
    return render(request, 'blog.html', {'articles':articles})

