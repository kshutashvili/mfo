from django import forms
from django.core.validators import validate_email
from django.core.exceptions import ValidationError
from django.utils.translation import ugettext, ugettext_lazy as _


class SendEmailForm(forms.Form):
    name = forms.CharField(widget=forms.TextInput(attrs={'class':'f-contact-input',
                                                         'name':'username',
                                                         'placeholder':_('ФИО')}))
    email = forms.CharField(validators=[validate_email],
                            widget=forms.TextInput(attrs={'placeholder':_('E-mail'),
                                                          'class':'f-contact-input',
                                                          'name':'email'}))
    message = forms.CharField(widget=forms.Textarea(attrs={'class':'f-contact-textarea',
                                                           'name':'message',
                                                           'placeholder':'Ваше сообщение...'}))

