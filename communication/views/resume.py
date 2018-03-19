from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect
from django.urls import reverse
from django.utils.translation import ugettext_lazy as _
from django.core.mail import EmailMessage

from communication.forms import SendResumeForm
from vacancy.models import Category
from department.models import Department
from content.models import JobStaticPage
from communication.models import Resume


def resume(request):
    status_message = ''
    cities = []
    for obj in Department.objects.all():
        if obj.city not in cities:
            cities.append(obj.city)
    vacancies = []
    categories = Category.objects.all().select_related()
    for category in categories:
        for vacancy in category.vacancies.get_queryset():
            vacancies.append(' : '.join([category.name, vacancy.name]))
    if request.method == 'GET':
        form = SendResumeForm()
    elif request.method == 'POST':
        form = SendResumeForm(request.POST, request.FILES)
        if form.is_valid():
            
            resume = Resume()
            resume.first_name = form.cleaned_data.get('first_name')
            resume.last_name = form.cleaned_data.get('last_name')
            resume.city = form.cleaned_data.get('city')
            resume.phone = form.cleaned_data.get('phone')
            resume.email = form.cleaned_data.get('email')
            resume.file = request.FILES['file']
            vacancy_full_name = form.cleaned_data.get('vacancy')
            category_name = vacancy_full_name.split(':')[0].strip()
            vacancy_name = vacancy_full_name.split(':')[1].strip()
            category = Category.objects.filter(name=category_name).first()
            for obj in category.vacancies.get_queryset():
                if vacancy_name == obj.name:
                    resume.vacancy = obj
                    break
            resume.save()

            job_page = JobStaticPage.get_solo()
            to_email = job_page.email.email
            from_email = form.cleaned_data.get('email')
            subject = ' '.join([form.cleaned_data.get('first_name'),
                                form.cleaned_data.get('last_name')])
            message = 'Город: '.join(['', form.cleaned_data.get('city')])
            message = '\nВакансия --- '.join([message, form.cleaned_data.get('vacancy')])
            message = '\nТелефон --- '.join([message, form.cleaned_data.get('phone')])
            message = '\nE-mail --- '.join([message, from_email])
            try:
                file = request.FILES['file']
                mail = EmailMessage(subject, message, from_email, [to_email,])
                mail.attach(file.name, file.read(), file.content_type)
                mail.send()
                url = reverse('success', kwargs={'id_mess':job_page.success_form.id})
                return HttpResponseRedirect(url)
            except:
                status_message = _('Произошла ошибка при отправке заявки, '
                                   'попробуйте позже...')
        else:
            status_message = _('Исправьте ошибки в данных')
    previous_page = request.META.get('HTTP_REFERER')
    if previous_page:
        previous_page = previous_page.split('/')[-2]
    return render(request, 'form-resume.html', {'form':form,
                                                'cities':cities,
                                                'vacancies':vacancies,
                                                'status_message':status_message,
                                                'previous_page':previous_page})

