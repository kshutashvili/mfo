import re

from django import forms
from django.contrib.auth.password_validation import validate_password
from django.utils.translation import ugettext, ugettext_lazy as _

from users.models import User


class SetPasswordForm(forms.Form):
    password = forms.CharField(validators=[validate_password])
    password_confirm = forms.CharField(validators=[validate_password])

    def clean(self):
        cleaned_data = super(SetPasswordForm, self).clean()

        password = cleaned_data.get('password')
        password_confirm = cleaned_data.get('password_confirm')

        if password != password_confirm:
            self.add_error('password', _('Введенные пароли не совпадают'))

        if not self.errors:
            cleaned_data = {'password': cleaned_data.get('password')}

        return cleaned_data


class RegisterNumberForm(forms.Form):
    phone = forms.CharField(widget=forms.TextInput(attrs={'placeholder':_('+38 (0__) ___ __ __'),
                                                          'type':'tel',
                                                          'name':'phone'}))
    def clean(self):
        cleaned_data = super(RegisterNumberForm, self).clean()

        phone = cleaned_data.get('phone')
        phone = phone.translate ({ord(c): "" for c in " !@#$%^&*()[]{};:,./<>?\|`~-=_+"})
        if len(phone) == 12:
            phone = phone[3:]
        elif len(phone) == 11:
            phone = phone[2:]
        elif len(phone) == 10:
            phone = phone[1:]
        if re.match(r'\d{9}$', phone) == None:
            self.add_error('phone', _('Неправильный телефон'))
        
        if not self.errors:
            cleaned_data = {'phone':phone}
        
        return cleaned_data


class LoginForm(forms.Form):
    username = forms.CharField(widget=forms.TextInput(attrs={'placeholder':_('+38 (0__) ___ __ __'),
                                                             'type':'tel',
                                                             'name':'username'}))
    password = forms.CharField(widget=forms.PasswordInput(attrs={'placeholder':_('Введите пароль'),
                                                                 'type':'password',
                                                                 'name':'password'}))
