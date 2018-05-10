import re

from django import forms
from django.urls import reverse
from django.contrib.auth.password_validation import validate_password
from django.utils.translation import ugettext_lazy as _
from django.contrib.auth.forms import (
    AdminPasswordChangeForm as DjangoAdminPasswordChangeForm
)
from django.http.response import HttpResponseRedirect

from users.models import User, RequestPersonalArea
from users.utils import get_person_id_and_tel
from communication.views.sms import verify_resetting
from communication.models import CallbackSuccessForm
from content.helpers import process_bid


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
    mobile_phone = forms.CharField(
        widget=forms.TextInput(
            attrs={
                'placeholder': _('+38 (0__) ___ __ __'),
                'type': 'tel',
                'name': 'mobile_phone'
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


class AdminPasswordChangeForm(DjangoAdminPasswordChangeForm):
    def __init__(self, user, *args, **kwargs):
        super().__init__(user, *args, **kwargs)
        self.fields["password1"].widget.attrs["placeholder"] = _('Введите пароль')
        self.fields["password2"].widget.attrs["placeholder"] = _('Повторите пароль')


class ResetPasswordForm(forms.Form):
    contract_num = forms.CharField(
        widget=forms.TextInput(
            attrs={
                'placeholder': _('Номер договора'),
                'class': 'f-form__input',
                'name': 'contract_num'
            }
        )
    )

    def clean_contract_num(self):
        contract_num = self.cleaned_data['contract_num']
        person_data = get_person_id_and_tel(contract_num)
        print("VALIDATNG", person_data)
        self.person_phone = person_data[1]
        if person_data:
            user = User.objects.filter(
                turnes_person_id=person_data[0],
                # person_data phone w/o +3
                mobile_phone__icontains=person_data[1][2:],
            )
        else:
            msg = _("Пользователь с таким номером договора не зарегистрирован1")
            raise forms.ValidationError(msg)
        if not user:
            msg = _("Пользователь с таким номером договора не зарегистрирован2")
            raise forms.ValidationError(msg)
        return contract_num


class ResetPasswordVerifyForm(forms.Form):
    code = forms.CharField(
        widget=forms.TextInput(
            attrs={
                'placeholder': _('Введите код из смс'),
                'class': 'f-form__input',
                'name': 'code'
            }
        )
    )

    def __init__(self, *args, **kwargs):
        self.phone = kwargs.pop('phone', None)
        super().__init__(*args, **kwargs)

    def clean_code(self):
        code = self.cleaned_data['code']
        verified = verify_resetting(self.phone, code)

        print(verified)
        if verified:
            return HttpResponseRedirect(reverse('profile'))
        else:
            msg = _("Вы ввели неверный код из СМС")
            raise forms.ValidationError(msg)


class CallbackConfirmForm(forms.Form):
    code = forms.CharField(
        widget=forms.TextInput(
            attrs={
                'placeholder': _('Введите код из смс'),
                'class': 'f-form__input',
                'name': 'code'
            }
        )
    )

    def __init__(self, *args, **kwargs):
        self.phone = kwargs.pop('phone', None)
        self.bid = kwargs.pop('bid', None)
        super().__init__(*args, **kwargs)

    def clean_code(self):
        code = self.cleaned_data['code']
        verified = verify_resetting(self.phone, code)
        print("BID form", self.bid)
        print(verified)
        if verified:
            process_bid(self.bid)
            callback_success = CallbackSuccessForm.get_solo()
            url = reverse(
                'success',
                kwargs={
                    'id_mess': callback_success.success.id,
                    'redirect_url': 'main'
                }
            )
            return HttpResponseRedirect(url)
        else:
            msg = _("Вы ввели неверный код из СМС")
            raise forms.ValidationError(msg)
