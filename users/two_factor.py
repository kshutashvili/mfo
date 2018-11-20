from django_otp.admin import (OTPAdminSite as OTPAdmin)
from django_otp.forms import (
    OTPAuthenticationFormMixin as SourceOTPAuthenticationFormMixin,
    match_token
)
from django_otp.models import Device

from django import forms
from django.contrib.admin.forms import AdminAuthenticationForm
from django.core.exceptions import ValidationError
from django.utils.translation import ugettext_lazy as _


class OTPAuthenticationFormMixin(SourceOTPAuthenticationFormMixin):
    def _handle_challenge(self, device):
        try:
            challenge = device.generate_challenge() if (device is not None) else None
        except Exception as e:
            raise forms.ValidationError(
                _('Error generating challenge: {0}'.format(e))
            )
        else:
            if challenge is None:
                raise forms.ValidationError(
                    _('The selected OTP device is not interactive')
                )
            else:
                if challenge == 'sent by email':
                    raise forms.ValidationError(
                        _('Токен для входа в систему отправлен на адрес: {0}'.format(
                            device.user.email
                        ))
                    )
                raise forms.ValidationError(
                    _('OTP Challenge: {0}').format(challenge)
                )

    def _verify_token(self, user, token, device=None):
        if device is not None:
            device = device if device.verify_token(token) else None
        else:
            device = match_token(user, token)

        if device is None:
            raise forms.ValidationError(
                _('Неверный токен. Убедитесь, что вы ввели его правильно.'),
                code='invalid'
            )

        return device


class CustomOTPAdminAuthenticationForm(OTPAuthenticationFormMixin,
                                       AdminAuthenticationForm):

    otp_device = forms.CharField(required=False, widget=forms.Select)
    otp_token = forms.CharField(required=False, widget=forms.TextInput(
        attrs={'autocomplete': 'off'}
    ))
    otp_challenge = forms.CharField(required=False)

    def clean(self):
        self.cleaned_data = super(CustomOTPAdminAuthenticationForm,
                                  self).clean()

        user = self.get_user()
        token = self.cleaned_data.get('otp_token', None)

        if token is None or token == '':

            # added otp_device field (for this project, only with Email device)
            self._update_form(user)

            try:
                # get EmailDevice object related with current user by device ID
                device = Device.from_persistent_id(
                    # device_choices return[('otp_email.emaildevice/1','mail')]
                    self.device_choices(user)[0][0]
                )
            except Exception as e:
                print(e)
                raise ValidationError(
                    message="Вашему аккаунту не подлючено 2FA"
                )

            # generate Token and send user's email
            self._handle_challenge(device)

        # clean and verify Token
        self.clean_otp(self.get_user())

        return self.cleaned_data

    def __init__(self, *args, **kwargs):
        super(CustomOTPAdminAuthenticationForm, self).__init__(*args, **kwargs)
        self.fields['username'].widget.attrs.update({'placeholder': 'Username'})
        self.fields['password'].widget.attrs.update({'placeholder': 'Password'})


class OTPAdminSite(OTPAdmin):
    login_form = CustomOTPAdminAuthenticationForm
