from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect
from django.utils.translation import ugettext_lazy as _

from communication.models import Contact


def contacts(request):
	if request.method == 'GET':
		contact = Contact.objects.first()
		return render(request, 'contacts.html', {'contact':contact})