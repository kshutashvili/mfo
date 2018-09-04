import re

from django import forms
from django.urls import reverse
from django.contrib.auth.password_validation import validate_password
from django.utils.translation import ugettext_lazy as _
from django.contrib.auth.forms import (
    AdminPasswordChangeForm as DjangoAdminPasswordChangeForm
)
from django.http.response import HttpResponseRedirect

from users.models import (
    User, RequestPersonalArea,
    Questionnaire,
    RegistrationCountry
)
from users.utils import (
    get_person_id_and_tel, get_dropdown_data
)
from communication.views.sms import sms_verify
from communication.models import CallbackSuccessForm
from content.helpers import process_bid, clear_contact_phone


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
                'name': 'phone',
                'class': 'phone-mask'
            }
        )
    )

    def clean(self):
        cleaned_data = super(RegisterNumberForm, self).clean()

        phone = cleaned_data.get('phone')

        valid_phone = clear_contact_phone(phone)

        cleaned_data["phone"] = valid_phone

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


class SMSVerifyForm(forms.Form):
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
        verified = sms_verify(self.phone, code)

        if verified:
            return code
        else:
            msg = _("Вы ввели неверный код из СМС")
            raise forms.ValidationError(msg)


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
            msg = _("Пользователь с таким номером договора не зарегистрирован")
            raise forms.ValidationError(msg)
        if not user:
            msg = _("Пользователь с таким номером договора не зарегистрирован")
            raise forms.ValidationError(msg)
        return contract_num


class ResetPasswordVerifyForm(SMSVerifyForm):
    pass


class CallbackVerifyForm(SMSVerifyForm):
    def __init__(self, *args, **kwargs):
        self.bid = kwargs.pop('bid', None)
        super().__init__(*args, **kwargs)

    def clean_code(self):
        code = self.cleaned_data['code']
        verified = sms_verify(self.phone, code)

        if verified:
            process_bid(self.bid)
            return code
        else:
            msg = _("Вы ввели неверный код из СМС")
            raise forms.ValidationError(msg)


class RegisterVerifyForm(SMSVerifyForm):
    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        print("RegisterVerifyForm", self.user)
        super().__init__(*args, **kwargs)


class RegisterPersonalForm(forms.ModelForm):
    registration_county_switch = forms.ChoiceField(
        choices=(('', ''),),
    )
    residence_county_switch = forms.ChoiceField(
        choices=(('', ''),),
    )

    class Meta:
        model = Questionnaire
        fields = [
            'last_name', 'first_name',
            'middle_name', 'birthday_date',
            'mobile_phone', 'email',
            'itn', 'passport_code',
            'passport_date', 'passport_outdate',
            'passport_authority', 'registration_country',
            'registration_state', 'registration_district',
            'registration_city', 'registration_street',
            'registration_building', 'registration_flat',
            'registration_index', 'residence_country',
            'residence_state', 'residence_district',
            'residence_city', 'residence_street',
            'residence_building', 'residence_flat',
            'residence_index', 'sex',
            'education', 'marital_status',
            'has_criminal_record',

            'employment_type', 'company_name',
            'edrpou_code', 'position',
            'position_type', 'service_type',
            'company_experience', 'overall_experience',
            'company_address', 'company_phone',
            'labor_relations', 'state_registration_date',
            'state_registration_authority', 'activity_type',
            'confirmed_document', 'employ_count',

            'bound_person_names', 'bound_person_itn',
            'bound_person_relationship', 'bound_person_job',
            'bound_person_phone', 'bound_person_address',

            'salary', 'partner_salary',
            'bonuses', 'social_benefits',
            'pension', 'partner_pension',
            'other_income', 'overall_income',
            'month_outgoing', 'month_loan_payments_outgoing',
            'other_outgoing', 'dwelling_type',
            'vehicle_count', 'vehicle_description',

            'credit_sum', 'credit_term',
            'credit_period',
        ]
        widgets = {
            'last_name': forms.TextInput(
                attrs={
                    'class': 'questionnaire__input',
                    'placeholder': _('Прізвище'),
                }
            ),
            'first_name': forms.TextInput(
                attrs={
                    'class': 'questionnaire__input',
                    'placeholder': _("Ім'я"),
                }
            ),
            'middle_name': forms.TextInput(
                attrs={
                    'class': 'questionnaire__input',
                    'placeholder': _('По батькові'),
                }
            ),
            'birthday_date': forms.DateInput(
                attrs={
                    'class': 'questionnaire__input date',
                    'placeholder': _('Дата народження'),
                }
            ),
            'mobile_phone': forms.TextInput(
                attrs={
                    'class': 'questionnaire__input phone-mask',
                    'placeholder': _('+38 (0__) ___ __ __'),
                }
            ),
            'email': forms.EmailInput(
                attrs={
                    'class': 'questionnaire__input',
                    'placeholder': _('example@mail.com'),
                }
            ),
            'itn': forms.TextInput(
                attrs={
                    'class': 'questionnaire__input',
                    'placeholder': _('XXXXXXXXXX'),
                }
            ),
            'passport_code': forms.TextInput(
                attrs={
                    'class': 'questionnaire__input',
                    'placeholder': _('AA XXXXXX / XXXXXXXXX'),
                }
            ),
            'passport_date': forms.DateInput(
                attrs={
                    'class': 'questionnaire__input date',
                    'placeholder': _('Дата видачі паспорту / ID-карти'),
                }
            ),
            'passport_outdate': forms.DateInput(
                attrs={
                    'class': 'questionnaire__input date',
                    'placeholder': _('Дата закінчення терміну дії ID-карти')
                }
            ),
            'passport_authority': forms.TextInput(
                attrs={
                    'class': 'questionnaire__input',
                    'placeholder': _('Ким виданий паспорт / ID-карта'),
                }
            ),
            'registration_country': forms.TextInput(
                attrs={
                    'class': 'questionnaire__input',
                }
            ),
            'registration_state': forms.Select(
                attrs={
                    'class': 'questionnaire__input',
                }
            ),
            'registration_district': forms.TextInput(
                attrs={
                    'class': 'questionnaire__input',
                    'placeholder': _('Район'),
                }
            ),
            'registration_city': forms.TextInput(
                attrs={
                    'class': 'questionnaire__input',
                    'placeholder': _('Назва населеного пункту'),
                }
            ),
            'registration_street': forms.TextInput(
                attrs={
                    'class': 'questionnaire__input',
                    'placeholder': _('Назва вулиці'),
                }
            ),
            'registration_building': forms.TextInput(
                attrs={
                    'class': 'questionnaire__input',
                    'placeholder': _('Номер будинку'),
                }
            ),
            'registration_flat': forms.TextInput(
                attrs={
                    'class': 'questionnaire__input',
                    'placeholder': _('Номер квартири'),
                }
            ),
            'registration_index': forms.TextInput(
                attrs={
                    'class': 'questionnaire__input',
                    'placeholder': _('XXXXX'),
                }
            ),
            'residence_country': forms.TextInput(
                attrs={
                    'class': 'questionnaire__input',
                }
            ),
            'residence_state': forms.Select(
                attrs={
                    'class': 'questionnaire__input',
                }
            ),
            'residence_district': forms.TextInput(
                attrs={
                    'class': 'questionnaire__input',
                    'placeholder': _('Район')
                }
            ),
            'residence_city': forms.TextInput(
                attrs={
                    'class': 'questionnaire__input',
                    'placeholder': _('Назва населеного пункту')
                }
            ),
            'residence_street': forms.TextInput(
                attrs={
                    'class': 'questionnaire__input',
                    'placeholder': _('Назва вулиці')
                }
            ),
            'residence_building': forms.TextInput(
                attrs={
                    'class': 'questionnaire__input',
                    'placeholder': _('Номер будинку')
                }
            ),
            'residence_flat': forms.TextInput(
                attrs={
                    'class': 'questionnaire__input',
                    'placeholder': _('Номер квартири')
                }
            ),
            'residence_index': forms.TextInput(
                attrs={
                    'class': 'questionnaire__input',
                    'placeholder': _('XXXXX')
                }
            ),
            'education': forms.Select(
                attrs={
                    'class': 'questionnaire__input',
                }
            ),
            'marital_status': forms.Select(
                attrs={
                    'class': 'questionnaire__input',
                }
            ),
            'company_name': forms.TextInput(
                attrs={
                    'class': 'questionnaire__input',
                    'placeholder': _('Назва компанії'),
                }
            ),
            'edrpou_code': forms.TextInput(
                attrs={
                    'class': 'questionnaire__input',
                    'placeholder': _('Код ЄДРПОУ'),
                }
            ),
            'position': forms.TextInput(
                attrs={
                    'class': 'questionnaire__input',
                    'placeholder': _('Посада'),
                }
            ),
            'position_type': forms.Select(
                attrs={
                    'class': 'questionnaire__input',
                }
            ),
            'service_type': forms.Select(
                attrs={
                    'class': 'questionnaire__input',
                }
            ),
            'company_experience': forms.TextInput(
                attrs={
                    'class': 'questionnaire__input',
                    'placeholder': _('Стаж роботи в компанії'),
                }
            ),
            'overall_experience': forms.TextInput(
                attrs={
                    'class': 'questionnaire__input',
                    'placeholder': _('Загальний трудовий стаж'),
                }
            ),
            'company_address': forms.TextInput(
                attrs={
                    'class': 'questionnaire__input',
                    'placeholder': _('Фактична адреса місця праці'),
                }
            ),
            'company_phone': forms.TextInput(
                attrs={
                    'class': 'questionnaire__input',
                    'placeholder': _('Контактний номер компанії'),
                }
            ),
            'labor_relations': forms.Select(
                attrs={
                    'class': 'questionnaire__input',
                    'placeholder': _('Трудові правовідносини'),
                }
            ),
            'state_registration_date': forms.TextInput(
                attrs={
                    'class': 'questionnaire__input',
                    'placeholder': _('Дата державної реєстрації')
                }
            ),
            'state_registration_authority': forms.TextInput(
                attrs={
                    'class': 'questionnaire__input',
                    'placeholder': _('Орган державної реєстрації')
                }
            ),
            'activity_type': forms.TextInput(
                attrs={
                    'class': 'questionnaire__input',
                    'placeholder': _('Вид діяльності (КВЕД)')
                }
            ),
            'confirmed_document': forms.TextInput(
                attrs={
                    'class': 'questionnaire__input',
                    'placeholder': _('Серія та номер')
                }
            ),
            'employ_count': forms.Select(
                attrs={
                    'class': 'questionnaire__input',
                    'placeholder': _('Кількість співробітників')
                }
            ),
            'bound_person_names': forms.TextInput(
                attrs={
                    'class': 'questionnaire__input',
                    'placeholder': _('ПІБ'),
                }
            ),
            'bound_person_itn': forms.TextInput(
                attrs={
                    'class': 'questionnaire__input',
                    'placeholder': _('Індивідуальний податковий номер (ІПН)'),
                }
            ),
            'bound_person_relationship': forms.Select(
                attrs={
                    'class': 'questionnaire__input',
                }
            ),
            'bound_person_job': forms.TextInput(
                attrs={
                    'class': 'questionnaire__input',
                    'placeholder': _('Дані про роботу'),
                }
            ),
            'bound_person_phone': forms.TextInput(
                attrs={
                    'class': 'questionnaire__input',
                    'placeholder': _('Контактний номер телефону'),
                }
            ),
            'bound_person_address': forms.TextInput(
                attrs={
                    'class': 'questionnaire__input',
                    'placeholder': _('Адреса фактичного проживання'),
                }
            ),
            'salary': forms.TextInput(
                attrs={
                    'class': 'questionnaire__input',
                    'placeholder': _('Заробітна плата, грн'),
                }
            ),
            'partner_salary': forms.TextInput(
                attrs={
                    'class': 'questionnaire__input',
                    'placeholder': _('Заробітна плата чоловіка/дружини, грн'),
                }
            ),
            'bonuses': forms.TextInput(
                attrs={
                    'class': 'questionnaire__input',
                    'placeholder': _('Бонуси та премії, грн'),
                }
            ),
            'social_benefits': forms.TextInput(
                attrs={
                    'class': 'questionnaire__input',
                    'placeholder': _('Соціальні пільги, грн'),
                }
            ),
            'pension': forms.TextInput(
                attrs={
                    'class': 'questionnaire__input',
                    'placeholder': _('Пенсія, грн'),
                }
            ),
            'partner_pension': forms.TextInput(
                attrs={
                    'class': 'questionnaire__input',
                    'placeholder': _('Пенсія чоловіка/дружини, грн'),
                }
            ),
            'other_income': forms.TextInput(
                attrs={
                    'class': 'questionnaire__input',
                    'placeholder': _('Інший дохід, грн'),
                }
            ),
            'overall_income': forms.TextInput(
                attrs={
                    'class': 'questionnaire__input',
                    'placeholder': _('Загальний дохід, грн'),
                }
            ),
            'month_outgoing': forms.TextInput(
                attrs={
                    'class': 'questionnaire__input',
                    'placeholder': _('Щомісячні витрати, грн'),
                }
            ),
            'month_loan_payments_outgoing': forms.TextInput(
                attrs={
                    'class': 'questionnaire__input',
                    'placeholder': _('Щомісячні платежі по кредитам, грн'),
                }
            ),
            'other_outgoing': forms.TextInput(
                attrs={
                    'class': 'questionnaire__input',
                    'placeholder': _('Інші витрати, грн'),
                }
            ),
            'dwelling_type': forms.Select(
                attrs={
                    'class': 'questionnaire__input',
                }
            ),
            'vehicle_count': forms.NumberInput(
                attrs={
                    'class': 'questionnaire__input',
                    'placeholder': _('Кількість автомобілів'),
                }
            ),
            'vehicle_description': forms.Textarea(
                attrs={
                    'class': 'questionnaire__input',
                    'placeholder': _('Опис авто (марка, модель тощо)'),
                }
            ),
            'credit_sum': forms.TextInput(
                attrs={
                    'class': 'questionnaire__input',
                    'placeholder': _('Сума кредиту'),
                }
            ),
            'credit_term': forms.TextInput(
                attrs={
                    'class': 'questionnaire__input',
                    'placeholder': _('Термін кредиту (кількість тижнів/місяців)'),
                }
            ),
        }

    def __init__(self, *args, **kwargs):

        super(RegisterPersonalForm, self).__init__(*args, **kwargs)

        self.fields['registration_county_switch'].choices = [
            (country.value, country.name) for country in RegistrationCountry.objects.all()
        ]
        self.fields['registration_county_switch'].choices.insert(
            0, ('', _('Виберіть країну'))
        )
        self.fields['registration_county_switch'].widget.attrs.update({
            'class': 'b-select',
            'id': 'selectRegistration'
        })
        self.fields['registration_county_switch'].required = False

        self.fields['residence_county_switch'].choices = [
            (country.value, country.name) for country in RegistrationCountry.objects.all()
        ]
        self.fields['residence_county_switch'].choices.insert(
            0, ('', _('Виберіть країну'))
        )
        self.fields['residence_county_switch'].widget.attrs.update({
            'class': 'b-select',
            'id': 'residence'
        })
        self.fields['residence_county_switch'].required = False

        self.fields['sex'].widget.attrs.update({
            'class': 'b-select',
            'id': 'sex'
        })

        self.fields['education'].widget.choices = [
            (dropdown[0], dropdown[1]) for dropdown in get_dropdown_data(5)
        ]
        self.fields['education'].widget.choices.insert(
            0, ('', _('Освіта'))
        )

        self.fields['marital_status'].widget.choices = [
            (dropdown[0], dropdown[1]) for dropdown in get_dropdown_data(4)
        ]
        self.fields['marital_status'].widget.choices.insert(
            0, ('', _('Сімейний стан'))
        )

        state_dopdown = get_dropdown_data(2)
        self.fields['registration_state'].widget.choices = [
            (dropdown[0], dropdown[1]) for dropdown in state_dopdown
        ]
        self.fields['registration_state'].widget.choices.insert(
            0, ('', _('Область'))
        )
        self.fields['residence_state'].widget.choices = [
            (dropdown[0], dropdown[1]) for dropdown in state_dopdown
        ]
        self.fields['residence_state'].widget.choices.insert(
            0, ('', _('Область'))
        )

        self.fields['employment_type'].widget.attrs.update({
            'class': 'b-select',
            'id': 'employment_type'
        })

        self.fields['position_type'].widget.choices = [
            (dropdown[0], dropdown[1]) for dropdown in get_dropdown_data(20)
        ]
        self.fields['position_type'].widget.choices.insert(
            0, ('', _('Вид персоналу'))
        )

        self.fields['service_type'].widget.choices = [
            (dropdown[0], dropdown[1]) for dropdown in get_dropdown_data(6)
        ]
        self.fields['service_type'].widget.choices.insert(
            0, ('', _('Сфера діяльності'))
        )

        self.fields['labor_relations'].widget.choices = [
            (dropdown[0], dropdown[1]) for dropdown in get_dropdown_data(7)
        ]
        self.fields['labor_relations'].widget.choices.insert(
            0, ('', _('Трудові правовідносини'))
        )

        self.fields['bound_person_relationship'].widget.choices = [
            (dropdown[0], dropdown[1]) for dropdown in get_dropdown_data(12)
        ]
        self.fields['bound_person_relationship'].widget.choices.insert(
            0, ('', _('Ступінь відносин'))
        )

        self.fields['dwelling_type'].widget.choices = [
            (dropdown[0], dropdown[1]) for dropdown in get_dropdown_data(10)
        ]
        self.fields['dwelling_type'].widget.choices.insert(
            0, ('', _('Тип житла'))
        )


class RegisterPersonalStep1Form(forms.ModelForm):
    registration_county_switch = forms.ChoiceField(
        choices=(('', ''),),
    )
    residence_county_switch = forms.ChoiceField(
        choices=(('', ''),),
    )

    class Meta:
        model = Questionnaire
        fields = [
            'user',
            'last_name', 'first_name',
            'middle_name', 'birthday_date',
            'mobile_phone', 'email',
            'itn', 'passport_code',
            'passport_date', 'passport_outdate',
            'passport_authority', 'registration_country',
            'registration_state', 'registration_district',
            'registration_city', 'registration_street',
            'registration_building', 'registration_flat',
            'registration_index', 'residence_country',
            'residence_state', 'residence_district',
            'residence_city', 'residence_street',
            'residence_building', 'residence_flat',
            'residence_index', 'sex',
            'education', 'marital_status',
            'has_criminal_record'
        ]
        widgets = {
            'last_name': forms.TextInput(
                attrs={
                    'class': 'questionnaire__input',
                    'placeholder': _('Прізвище'),
                }
            ),
            'first_name': forms.TextInput(
                attrs={
                    'class': 'questionnaire__input',
                    'placeholder': _("Ім'я"),
                }
            ),
            'middle_name': forms.TextInput(
                attrs={
                    'class': 'questionnaire__input',
                    'placeholder': _('По батькові'),
                }
            ),
            'birthday_date': forms.DateInput(
                attrs={
                    'class': 'questionnaire__input date',
                    'placeholder': _('Дата народження'),
                }
            ),
            'mobile_phone': forms.TextInput(
                attrs={
                    'class': 'questionnaire__input phone-mask',
                    'placeholder': _('+38 (0__) ___ __ __'),
                }
            ),
            'email': forms.EmailInput(
                attrs={
                    'class': 'questionnaire__input',
                    'placeholder': _('example@mail.com'),
                }
            ),
            'itn': forms.TextInput(
                attrs={
                    'class': 'questionnaire__input',
                    'placeholder': _('XXXXXXXXXX'),
                }
            ),
            'passport_code': forms.TextInput(
                attrs={
                    'class': 'questionnaire__input',
                    'placeholder': _('AA XXXXXX / XXXXXXXXX'),
                }
            ),
            'passport_date': forms.DateInput(
                attrs={
                    'class': 'questionnaire__input date',
                    'placeholder': _('Дата видачі паспорту / ID-карти'),
                }
            ),
            'passport_outdate': forms.DateInput(
                attrs={
                    'class': 'questionnaire__input date',
                    'placeholder': _('Дата закінчення терміну дії ID-карти')
                }
            ),
            'passport_authority': forms.TextInput(
                attrs={
                    'class': 'questionnaire__input',
                    'placeholder': _('Ким виданий паспорт / ID-карта'),
                }
            ),
            'registration_country': forms.TextInput(
                attrs={
                    'class': 'questionnaire__input',
                }
            ),
            'registration_state': forms.Select(
                attrs={
                    'class': 'questionnaire__input',
                }
            ),
            'registration_district': forms.TextInput(
                attrs={
                    'class': 'questionnaire__input',
                    'placeholder': _('Район'),
                }
            ),
            'registration_city': forms.TextInput(
                attrs={
                    'class': 'questionnaire__input',
                    'placeholder': _('Назва населеного пункту'),
                }
            ),
            'registration_street': forms.TextInput(
                attrs={
                    'class': 'questionnaire__input',
                    'placeholder': _('Назва вулиці'),
                }
            ),
            'registration_building': forms.TextInput(
                attrs={
                    'class': 'questionnaire__input',
                    'placeholder': _('Номер будинку'),
                }
            ),
            'registration_flat': forms.TextInput(
                attrs={
                    'class': 'questionnaire__input',
                    'placeholder': _('Номер квартири'),
                }
            ),
            'registration_index': forms.TextInput(
                attrs={
                    'class': 'questionnaire__input',
                    'placeholder': _('XXXXX'),
                }
            ),
            'residence_country': forms.TextInput(
                attrs={
                    'class': 'questionnaire__input',
                }
            ),
            'residence_state': forms.Select(
                attrs={
                    'class': 'questionnaire__input',
                }
            ),
            'residence_district': forms.TextInput(
                attrs={
                    'class': 'questionnaire__input',
                    'placeholder': _('Район')
                }
            ),
            'residence_city': forms.TextInput(
                attrs={
                    'class': 'questionnaire__input',
                    'placeholder': _('Назва населеного пункту')
                }
            ),
            'residence_street': forms.TextInput(
                attrs={
                    'class': 'questionnaire__input',
                    'placeholder': _('Назва вулиці')
                }
            ),
            'residence_building': forms.TextInput(
                attrs={
                    'class': 'questionnaire__input',
                    'placeholder': _('Номер будинку')
                }
            ),
            'residence_flat': forms.TextInput(
                attrs={
                    'class': 'questionnaire__input',
                    'placeholder': _('Номер квартири')
                }
            ),
            'residence_index': forms.TextInput(
                attrs={
                    'class': 'questionnaire__input',
                    'placeholder': _('XXXXX')
                }
            ),
            'education': forms.Select(
                attrs={
                    'class': 'questionnaire__input',
                }
            ),
            'marital_status': forms.Select(
                attrs={
                    'class': 'questionnaire__input',
                }
            ),
        }

    def __init__(self, *args, **kwargs):

        super(RegisterPersonalStep1Form, self).__init__(*args, **kwargs)

        self.fields['registration_county_switch'].choices = [
            (country.value, country.name) for country in RegistrationCountry.objects.all()
        ]
        self.fields['registration_county_switch'].choices.insert(
            0, ('', _('Виберіть країну'))
        )
        self.fields['registration_county_switch'].widget.attrs.update({
            'class': 'b-select',
            'id': 'selectRegistration'
        })
        self.fields['registration_county_switch'].required = False

        self.fields['residence_county_switch'].choices = [
            (country.value, country.name) for country in RegistrationCountry.objects.all()
        ]
        self.fields['residence_county_switch'].choices.insert(
            0, ('', _('Виберіть країну'))
        )
        self.fields['residence_county_switch'].widget.attrs.update({
            'class': 'b-select',
            'id': 'residence'
        })
        self.fields['residence_county_switch'].required = False

        self.fields['sex'].widget.attrs.update({
            'class': 'b-select',
            'id': 'sex'
        })

        self.fields['education'].widget.choices = [
            (dropdown[0], dropdown[1]) for dropdown in get_dropdown_data(5)
        ]
        self.fields['education'].widget.choices.insert(
            0, ('', _('Освіта'))
        )

        self.fields['marital_status'].widget.choices = [
            (dropdown[0], dropdown[1]) for dropdown in get_dropdown_data(4)
        ]
        self.fields['marital_status'].widget.choices.insert(
            0, ('', _('Сімейний стан'))
        )

        state_dopdown = get_dropdown_data(2)
        self.fields['registration_state'].widget.choices = [
            (dropdown[0], dropdown[1]) for dropdown in state_dopdown
        ]
        self.fields['registration_state'].widget.choices.insert(
            0, ('', _('Область'))
        )
        self.fields['residence_state'].widget.choices = [
            (dropdown[0], dropdown[1]) for dropdown in state_dopdown
        ]
        self.fields['residence_state'].widget.choices.insert(
            0, ('', _('Область'))
        )


class RegisterPersonalStep2Form(forms.ModelForm):
    class Meta:
        model = Questionnaire
        fields = [
            'employment_type', 'company_name',
            'edrpou_code', 'position',
            'position_type', 'service_type',
            'company_experience', 'overall_experience',
            'company_address', 'company_phone',
            'labor_relations', 'state_registration_date',
            'state_registration_authority', 'activity_type',
            'confirmed_document', 'employ_count'
        ]
        widgets = {
            'company_name': forms.TextInput(
                attrs={
                    'class': 'questionnaire__input',
                    'placeholder': _('Назва компанії'),
                }
            ),
            'edrpou_code': forms.TextInput(
                attrs={
                    'class': 'questionnaire__input',
                    'placeholder': _('Код ЄДРПОУ'),
                }
            ),
            'position': forms.TextInput(
                attrs={
                    'class': 'questionnaire__input',
                    'placeholder': _('Посада'),
                }
            ),
            'position_type': forms.Select(
                attrs={
                    'class': 'questionnaire__input',
                }
            ),
            'service_type': forms.Select(
                attrs={
                    'class': 'questionnaire__input',
                }
            ),
            'company_experience': forms.TextInput(
                attrs={
                    'class': 'questionnaire__input',
                    'placeholder': _('Стаж роботи в компанії'),
                }
            ),
            'overall_experience': forms.TextInput(
                attrs={
                    'class': 'questionnaire__input',
                    'placeholder': _('Загальний трудовий стаж'),
                }
            ),
            'company_address': forms.TextInput(
                attrs={
                    'class': 'questionnaire__input',
                    'placeholder': _('Фактична адреса місця праці'),
                }
            ),
            'company_phone': forms.TextInput(
                attrs={
                    'class': 'questionnaire__input',
                    'placeholder': _('Контактний номер компанії'),
                }
            ),
            'labor_relations': forms.Select(
                attrs={
                    'class': 'questionnaire__input',
                    'placeholder': _('Трудові правовідносини'),
                }
            ),
            'state_registration_date': forms.TextInput(
                attrs={
                    'class': 'questionnaire__input',
                    'placeholder': _('Дата державної реєстрації')
                }
            ),
            'state_registration_authority': forms.TextInput(
                attrs={
                    'class': 'questionnaire__input',
                    'placeholder': _('Орган державної реєстрації')
                }
            ),
            'activity_type': forms.TextInput(
                attrs={
                    'class': 'questionnaire__input',
                    'placeholder': _('Вид діяльності (КВЕД)')
                }
            ),
            'confirmed_document': forms.TextInput(
                attrs={
                    'class': 'questionnaire__input',
                    'placeholder': _('Серія та номер')
                }
            ),
            'employ_count': forms.Select(
                attrs={
                    'class': 'questionnaire__input',
                    'placeholder': _('Кількість співробітників')
                }
            ),
        }

    def __init__(self, *args, **kwargs):

        super(RegisterPersonalStep2Form, self).__init__(*args, **kwargs)

        self.fields['employment_type'].widget.attrs.update({
            'class': 'b-select',
            'id': 'employment_type'
        })

        self.fields['position_type'].widget.choices = [
            (dropdown[0], dropdown[1]) for dropdown in get_dropdown_data(20)
        ]
        self.fields['position_type'].widget.choices.insert(
            0, ('', _('Вид персоналу'))
        )

        self.fields['service_type'].widget.choices = [
            (dropdown[0], dropdown[1]) for dropdown in get_dropdown_data(6)
        ]
        self.fields['service_type'].widget.choices.insert(
            0, ('', _('Сфера діяльності'))
        )

        self.fields['labor_relations'].widget.choices = [
            (dropdown[0], dropdown[1]) for dropdown in get_dropdown_data(7)
        ]
        self.fields['labor_relations'].widget.choices.insert(
            0, ('', _('Трудові правовідносини'))
        )


class RegisterPersonalStep3Form(forms.ModelForm):
    class Meta:
        model = Questionnaire
        fields = [
            'bound_person_names', 'bound_person_itn',
            'bound_person_relationship', 'bound_person_job',
            'bound_person_phone', 'bound_person_address',
        ]
        widgets = {
            'bound_person_names': forms.TextInput(
                attrs={
                    'class': 'questionnaire__input',
                    'placeholder': _('ПІБ'),
                }
            ),
            'bound_person_itn': forms.TextInput(
                attrs={
                    'class': 'questionnaire__input',
                    'placeholder': _('Індивідуальний податковий номер (ІПН)'),
                }
            ),
            'bound_person_relationship': forms.Select(
                attrs={
                    'class': 'questionnaire__input',
                }
            ),
            'bound_person_job': forms.TextInput(
                attrs={
                    'class': 'questionnaire__input',
                    'placeholder': _('Дані про роботу'),
                }
            ),
            'bound_person_phone': forms.TextInput(
                attrs={
                    'class': 'questionnaire__input',
                    'placeholder': _('Контактний номер телефону'),
                }
            ),
            'bound_person_address': forms.TextInput(
                attrs={
                    'class': 'questionnaire__input',
                    'placeholder': _('Адреса фактичного проживання'),
                }
            ),
        }

    def __init__(self, *args, **kwargs):

        super(RegisterPersonalStep3Form, self).__init__(*args, **kwargs)

        self.fields['bound_person_relationship'].widget.choices = [
            (dropdown[0], dropdown[1]) for dropdown in get_dropdown_data(12)
        ]
        self.fields['bound_person_relationship'].widget.choices.insert(
            0, ('', _('Ступінь відносин'))
        )


class RegisterPersonalStep4Form(forms.ModelForm):
    class Meta:
        model = Questionnaire
        fields = [
            'salary', 'partner_salary',
            'bonuses', 'social_benefits',
            'pension', 'partner_pension',
            'other_income', 'overall_income',
            'month_outgoing', 'month_loan_payments_outgoing',
            'other_outgoing', 'dwelling_type',
            'vehicle_count', 'vehicle_description',
        ]
        widgets = {
            'salary': forms.TextInput(
                attrs={
                    'class': 'questionnaire__input',
                    'placeholder': _('Заробітна плата, грн'),
                }
            ),
            'partner_salary': forms.TextInput(
                attrs={
                    'class': 'questionnaire__input',
                    'placeholder': _('Заробітна плата чоловіка/дружини, грн'),
                }
            ),
            'bonuses': forms.TextInput(
                attrs={
                    'class': 'questionnaire__input',
                    'placeholder': _('Бонуси та премії, грн'),
                }
            ),
            'social_benefits': forms.TextInput(
                attrs={
                    'class': 'questionnaire__input',
                    'placeholder': _('Соціальні пільги, грн'),
                }
            ),
            'pension': forms.TextInput(
                attrs={
                    'class': 'questionnaire__input',
                    'placeholder': _('Пенсія, грн'),
                }
            ),
            'partner_pension': forms.TextInput(
                attrs={
                    'class': 'questionnaire__input',
                    'placeholder': _('Пенсія чоловіка/дружини, грн'),
                }
            ),
            'other_income': forms.TextInput(
                attrs={
                    'class': 'questionnaire__input',
                    'placeholder': _('Інший дохід, грн'),
                }
            ),
            'overall_income': forms.TextInput(
                attrs={
                    'class': 'questionnaire__input',
                    'placeholder': _('Загальний дохід, грн'),
                }
            ),
            'month_outgoing': forms.TextInput(
                attrs={
                    'class': 'questionnaire__input',
                    'placeholder': _('Щомісячні витрати, грн'),
                }
            ),
            'month_loan_payments_outgoing': forms.TextInput(
                attrs={
                    'class': 'questionnaire__input',
                    'placeholder': _('Щомісячні платежі по кредитам, грн'),
                }
            ),
            'other_outgoing': forms.TextInput(
                attrs={
                    'class': 'questionnaire__input',
                    'placeholder': _('Інші витрати, грн'),
                }
            ),
            'dwelling_type': forms.Select(
                attrs={
                    'class': 'questionnaire__input',
                }
            ),
            'vehicle_count': forms.NumberInput(
                attrs={
                    'class': 'questionnaire__input',
                    'placeholder': _('Кількість автомобілів'),
                }
            ),
            'vehicle_description': forms.Textarea(
                attrs={
                    'class': 'questionnaire__input',
                    'placeholder': _('Опис авто (марка, модель тощо)'),
                }
            ),
        }

    def __init__(self, *args, **kwargs):

        super(RegisterPersonalStep4Form, self).__init__(*args, **kwargs)

        self.fields['dwelling_type'].widget.choices = [
            (dropdown[0], dropdown[1]) for dropdown in get_dropdown_data(10)
        ]
        self.fields['dwelling_type'].widget.choices.insert(
            0, ('', _('Тип житла'))
        )


class RegisterPersonalStep5Form(forms.ModelForm):
    class Meta:
        model = Questionnaire
        fields = [
            'credit_sum', 'credit_term',
            'credit_period',
        ]
        widgets = {
            'credit_sum': forms.TextInput(
                attrs={
                    'class': 'questionnaire__input',
                    'placeholder': _('Сума кредиту'),
                }
            ),
            'credit_term': forms.TextInput(
                attrs={
                    'class': 'questionnaire__input',
                    'placeholder': _('Термін кредиту (кількість тижнів/місяців)'),
                }
            ),
        }
