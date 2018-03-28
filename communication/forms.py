import re

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
                                                           'placeholder':_('Ваше сообщение...')}))


class SendResumeForm(forms.Form):
    first_name = forms.CharField(widget=forms.TextInput(attrs={'class':'f-form__input f-form__input--mt',
                                                               'name':'first_name',
                                                               'placeholder':_('Имя')}))
    last_name = forms.CharField(widget=forms.TextInput(attrs={'class':'f-form__input',
                                                              'name':'last_name',
                                                              'placeholder':_('Фамилия')}))
    city = forms.CharField(widget=forms.TextInput(attrs={'class':'f-form__input',
                                                         'name':'city'}))
    vacancy = forms.CharField(widget=forms.TextInput(attrs={'class':'f-form__input',
                                                            'name':'vacancy'}))
    phone = forms.CharField(widget=forms.TextInput(attrs={'class':'f-form__input',
                                                          'name':'phone',
                                                          'placeholder':_('Телефон')}))
    email = forms.CharField(validators=[validate_email],
                            widget=forms.TextInput(attrs={'placeholder':_('E-mail'),
                                                          'class':'f-form__input',
                                                          'name':'email'}))
    file = forms.FileField(widget=forms.ClearableFileInput(attrs={'name':'file'}))


    def clean(self):
        cleaned_data = super(SendResumeForm, self).clean()

        phone = cleaned_data.get('phone')
        if re.match(r'^\+{0,1}\d{9,15}$', phone) == None:
            self.add_error('phone', _('Неправильный формат телефона'))

        return cleaned_data


class WriteCommentForm(forms.Form):
    content = forms.CharField(widget=forms.TextInput(attrs={'class':'chat__send-input',
                                                            'placeholder':_('Ваше сообщение...'),
                                                            'name':'content'}))


class WriteQuestionForm(forms.Form):
    support_text = forms.CharField(widget=forms.Textarea(attrs={'class':'chat__send-input',
                                                                'cols':'30',
                                                                'rows':'10',
                                                                'id':'question_input',
                                                                'placeholder':_('Ваше сообщение...'),
                                                                'name':'support-text'}))
    file = forms.FileField(widget=forms.ClearableFileInput(attrs={'name':'file'}),
                           required=False)

