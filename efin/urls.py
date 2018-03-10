"""efin URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from django.views.generic import TemplateView
from django.conf import settings
from django.conf.urls.static import static

from communication.views import contacts, about, blog, faq
from content.views import content
from vacancy.views import job

urlpatterns = [
    path('', content.index, name='index'),
    path('callback/', TemplateView.as_view(template_name='form-callback.html'), name='callback'),
    path('main/', content.main, name='main'),
    path('job/', job.job, name='job'),
    path('about/', about.about, name='about'),
    path('about/agreement/', content.agreement, name='agreement'),
    path('about/contacts/', contacts.contacts, name='contacts'),
    path('blog/', blog.blog, name='blog'),
    path('blog/item<int:item_id>/', blog.blog_item, name='blog_item'),
    path('faq/', faq.faq, name='faq'),
    path('static_pages/<str:page_url>/', content.pages, name='static_pages'),
    path('ajax/departments_generate/<int:dep_id>/', content.departments_generate, name='departments_generate'),
    path('ajax/slider_filler/', content.slider_filler, name='slider_generate'),
    path('ajax/credit_calculate/<int:rate_id>/<int:term>/<int:summ>/', content.credit_calculator, name='cred_calc'),
    path('admin/', admin.site.urls),
]
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
