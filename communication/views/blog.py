from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.utils.translation import ugettext_lazy as _
from django.http import Http404

from communication.models import BlogItem, BlogCategory


def blog_item(request, item_id):
    article = BlogItem.objects.filter(id=item_id).first()
    return render(request, 'blog-item.html', {'article':article})


def blog_category(request, category_link):
	category = BlogCategory.objects.filter(link=category_link).first()
	if category:
		return render(request, 'blog.html', {'articles':category.blog_items.get_queryset(),
											 'title':category.name})
	else:
		return Http404()


def blog(request):
    articles = BlogItem.objects.order_by('date').reverse()
    return render(request, 'blog.html', {'articles':articles})

