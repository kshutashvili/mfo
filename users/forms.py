import re

from django import forms
from django.contrib.auth.password_validation import validate_password
from django.utils.translation import ugettext, ugettext_lazy as _

from users.models import User, RequestPersonalArea


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
    phone = forms.CharField(
        widget=forms.TextInput(
            attrs={
                'placeholder': _('+38 (0__) ___ __ __'),
                'type': 'tel',
                'name': 'phone'
            }
        )
    )

    def clean(self):
        cleaned_data = super(RegisterNumberForm, self).clean()

        phone = cleaned_data.get('phone')
        phone = phone.translate(
            {ord(c): "" for c in " !@#$%^&*()[]{};:,./<>?\|`~-=_+"}
        )
        if len(phone) == 12:
            phone = phone[3:]
        elif len(phone) == 11:
            phone = phone[2:]
        elif len(phone) == 10:
            phone = phone[1:]

        if re.match(r'\d{9}$', phone) is None:
            self.add_error('phone', _('Неправильный телефон'))

        if not self.errors:
            cleaned_data = {'phone': phone}

        return cleaned_data


class LoginForm(forms.Form):
    username = forms.CharField(
        widget=forms.TextInput(
            attrs={
                'placeholder': _('+38 (0__) ___ __ __'),
                'type': 'tel',
                'name': 'username'
            }
        )
    )

    password = forms.CharField(
        widget=forms.PasswordInput(
            attrs={
                'placeholder': _('Введите пароль'),
                'type': 'password',
                'name': 'password'
            }
        )
    )


class RequestPersonalAreaForm(forms.ModelForm):
    error_css_class = 'error'

    class Meta:
        model = RequestPersonalArea
        fields = ('name', 'birthday', 'contract_num', 'mobile_phone_number')
        widgets = {
            'name': forms.TextInput(
                attrs={
                    'class': 'f-form__input',
                    'placeholder': _('ФИО')
                }
            ),
            'birthday': forms.DateInput(
                attrs={
                    'class': 'f-form__input date',
                    'placeholder': _('Дата рождения')
                }
            ),
            'contract_num': forms.TextInput(
                attrs={
                    'class': 'f-form__input contract-num',
                    'placeholder': _('Номер договора'),
                    # 'min': 1
                }
            ),
            'mobile_phone_number': forms.TextInput(
                attrs={
                    'class': 'f-form__input mobile-phone',
                    'placeholder': _('Номер телефона')
                }
            ),
        }

    def __init__(self, *args, **kwargs):
        super(RequestPersonalAreaForm, self).__init__(*args, **kwargs)
        for field_name in self.fields:
            if field_name in self.errors:
                self.fields[field_name].widget.attrs["class"] += " error"
            else:
                self.fields[field_name].widget.attrs["class"].replace(" error", "")
