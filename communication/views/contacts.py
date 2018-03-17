from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect
from django.urls import reverse
from django.utils.translation import ugettext_lazy as _
from django.core.mail import EmailMessage

from communication.models import Contact
from communication.forms import SendEmailForm
from content.models import MenuAboutItem


def contacts(request):
    contact = Contact.get_solo()
    menu_about = MenuAboutItem.objects.all()
    if request.method == 'GET':
        form = SendEmailForm()
        return render(request, 'contacts.html', {'contact':contact,
                                                 'form':form,
                                                 'menu_about':menu_about})
    elif request.method == 'POST':
        form = SendEmailForm(request.POST)
        if form.is_valid():
            to_email = Contact.get_solo().to_email.email
            from_email = form.cleaned_data.get('email')
            subject = form.cleaned_data.get('name')
            message = form.cleaned_data.get('message')
            message = '\nFrom E-mail: '.join([message, from_email])
            try:
                mail = EmailMessage(subject, message, from_email, [to_email,])
                mail.send()
                status_message = _('Сообщение успешно отправлено')
                return render(request, 'contacts.html', {'contact':contact,
                                                         'status_message':status_message,
                                                         'form':SendEmailForm()})
            except Exception as e:
                status_message = _('Произошла ошибка при отправке сообщения, попробуйте позже...')
        else:
            status_message = _('Исправьте ошибки в данных')
        return render(request, 'contacts.html', {'contact':contact,
                                                 'form':form,
                                                 'status_message':status_message,
                                                 'menu_about':menu_about})

