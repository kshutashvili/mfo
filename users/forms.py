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
            cleaned_data = {
                'password': cleaned_data.get('password'),
            }

        return cleaned_data

