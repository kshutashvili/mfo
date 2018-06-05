from pprint import pprint
from datetime import datetime

from django.shortcuts import render
from django.http import (
    HttpResponseRedirect, JsonResponse,
    HttpResponseBadRequest, HttpResponse
)
from django.utils.translation import ugettext_lazy as _
from django.urls import reverse, reverse_lazy
from django.contrib.auth import (
    authenticate, login, logout, update_session_auth_hash
)
from django.contrib.auth.decorators import login_required
from django.core.validators import validate_email
from django.core.exceptions import ValidationError
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import CreateView, TemplateView, View
from django.views.generic.edit import FormView
from django.utils.decorators import method_decorator

from bids.models import Bid
from communication.forms import WriteCommentForm, WriteQuestionForm
from communication.models import (
    UserExistMessage, UserQuestion, CallbackSuccessForm
)
from communication.views.sms import sms
from content.helpers import clear_contact_phone, check_blacklist
from payments.forms import PayForm
from users.forms import (
    SetPasswordForm,
    RegisterNumberForm,
    LoginForm,
    RequestPersonalAreaForm,
    AdminPasswordChangeForm,
    ResetPasswordForm,
    ResetPasswordVerifyForm,
    CallbackVerifyForm,
    SMSVerifyForm,
    RegisterVerifyForm,
    RegisterPersonalStep1Form,
    RegisterPersonalStep2Form,
    RegisterPersonalStep3Form,
    RegisterPersonalStep4Form,
    RegisterPersonalStep5Form,
    RegisterPersonalForm
)
from users.helpers import make_user_password
from users.models import (
    Profile, RequestPersonalArea, User, Questionnaire
)
from users.utils import test_user_turnes


def register(request):
    if request.method == 'POST':
        form = RegisterNumberForm(request.POST)
        if form.is_valid():
            phone = form.cleaned_data.get('phone')
            user = User.objects.filter(mobile_phone=phone).first()
            print(phone, user)
            if user and user.ready_for_turnes:
                id_mess = UserExistMessage.get_solo().page.id
                url = reverse('success', kwargs={
                    'redirect_url': 'login',
                    'id_mess': id_mess
                })
                return HttpResponseRedirect(url)
            elif user and user.ready_for_turnes == False:
                print("Not active")
                return sms(
                    request,
                    "+380950968326",
                    reverse('register_verify')
                )
            else:
                user = User.objects.create(
                    mobile_phone=phone,
                    ready_for_turnes=False
                )
                print("No user")
                return sms(
                    request,
                    "+380950968326",
                    reverse('register_verify'),
                    user
                )
        # else:
        #     status_message = _('invalid phone')
        #     url = reverse('callback', kwargs={'status_message':status_message})
        #     return HttpResponseRedirect(url)


def set_password(request):
    if request.method == 'GET':
        form = SetPasswordForm()
        status_message = None
    elif request.method == 'POST':
        form = SetPasswordForm(request.POST)
        if form.is_valid():
            user = Profile.objects.filter(
                phone=request.session.get('phone', '')
            ).first()
            user.user.set_password(form.cleaned_data.get('password'))
            user.user.save()
            return HttpResponseRedirect(reverse('login'))
        else:
            status_message = form.errors.get('password', '')
    return render(
        request,
        'enter-password.html',
        {
            'form': form,
            'status_message': status_message
        }
    )


class FirstChangePassword(FormView):
    form_class = AdminPasswordChangeForm
    success_url = reverse_lazy('profile')
    template_name = 'enter-password.html'
    title = _('Password change')

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs

    def form_valid(self, form):
        form.save()
        # Updating the password logs out all other sessions for the user
        # except the current one.
        update_session_auth_hash(self.request, form.user)

        # set checkbox in user profile
        current_user = User.objects.get(id=form.user.id)
        current_user.changed_default_password = True
        current_user.save()

        return super().form_valid(form)


def user_login(request, status_message=None):
    if request.method == 'POST':
        form = LoginForm()

        data = {
            'mobile_phone': clear_contact_phone(
                request.POST.get('mobile_phone')
            ),
            'password': request.POST.get('password')
        }

        form = LoginForm(data)
        if form.is_valid():
            mobile_phone = form.cleaned_data.get('mobile_phone')
            password = form.cleaned_data.get('password')
            user = authenticate(mobile_phone=mobile_phone, password=password)

            if user is not None:
                login(request, user)

                if request.POST.get('remember_me') is not None:
                    request.session.set_expiry(0)

                # checking if user changed password which received from SMS
                if user.changed_default_password:
                    return HttpResponseRedirect(reverse('profile'))
                elif not user.ready_for_turnes:
                    return HttpResponseRedirect(reverse('questionnaire'))
                else:
                    # if no, redirects to change password page
                    return HttpResponseRedirect(reverse('set_password'))
            else:
                status_message = _("Неправильный номер или пароль")
                return render(
                    request,
                    'enter.html',
                    {
                        'form': LoginForm(),
                        'status_message': status_message
                    }
                )
        else:
            status_message = _("Неправильный номер или пароль")
            return render(
                request,
                'enter.html',
                {
                    'form': LoginForm(),
                    'status_message': status_message
                }
            )
    elif request.method == 'GET':
        form = LoginForm()
        return render(
            request,
            'enter.html',
            {
                'form': form,
                'status_message': status_message
            }
        )


def user_logout(request):
    logout(request)
    return HttpResponseRedirect(reverse('login'))


def profile(request, active=None):
    if request.method == 'GET':
        turnes_profile = test_user_turnes(
            turnes_id=request.user.turnes_person_id
        )
        pay_form = PayForm()

        profile = Profile.objects.filter(user=request.user).first()
        comment_form = WriteCommentForm()
        question_form = WriteQuestionForm()
        user = Profile.objects.filter(user=request.user).first()
        count = UserQuestion.objects.count()
        pagination = int(count / 8)
        if count % 8 != 0:
            pagination += 1
        pagination = [0 for x in range(0, pagination)]

        questions = UserQuestion.objects.filter(
            user=user
        ).select_related().order_by(
            'is_read', 'updated_at'
        ).reverse()

        count_not_read_questions = 0
        for obj in questions:
            if not obj.is_read == 'read':
                count_not_read_questions += 1
        questions = questions[:8]

        return render(
            request,
            'private-profile.html',
            {
                'questions': questions,
                'active': active,
                'profile': profile,
                'turnes_profile': turnes_profile,
                'count_not_read_questions': count_not_read_questions,
                'question_form': question_form,
                'pagination': pagination,
                'comment_form': comment_form,
                'pay_form': pay_form
            }
        )


def alter_profile(request):
    if request.method == 'POST':
        field = request.POST.get('field_name')

        if field == 'phone':
            phone = {
                'phone': request.POST.get('field_value')
            }
            number_form = RegisterNumberForm(phone)
            if number_form.is_valid():
                if number_form.cleaned_data.get('phone') != request.user.username:
                    url = reverse(
                        'sms', kwargs={
                            'phone': number_form.cleaned_data.get('phone')
                        }
                    )
                    result = {'url': url}
                    return JsonResponse(result)
                else:
                    return JsonResponse(
                        {'phone': number_form.cleaned_data.get('phone')}
                    )

            else:
                result = {
                    'status': '500',
                    'status_message': _('Неправильный номер телефона')
                }
                return JsonResponse(result)

        elif field == 'email':
            email = request.POST.get('field_value')
            try:
                validate_email(email)
                if email != request.user.email:
                    request.session['email'] = email
                    url = reverse('change_email')
                    result = {'url': url}
                    return JsonResponse(result)
                else:
                    return JsonResponse({})

            except ValidationError:
                result = {
                    'status': '500',
                    'status_message': _('Неправильный электронный адрес')
                }
                return JsonResponse(result)

        elif field == 'authy':
            profile = Profile.objects.filter(user=request.user).first()
            profile.two_authy = not profile.two_authy
            profile.save()
            return JsonResponse(
                {
                    'status': '200'
                }
            )
    else:
        return HttpResponseBadRequest()


def message_read(request):
    if request.method == 'POST':
        question = UserQuestion.objects.filter(
            id=request.POST.get('id_quest')
        ).first()
        # choices: 'read', '!read', 'force read'
        question.is_read = 'force read'
        question.save()
        result = {
            'status': '200'
        }
        return JsonResponse(result)
    else:
        result = {
            'status': '500'
        }
        return JsonResponse(result)


class SMSVerifyView(FormView):
    form_class = SMSVerifyForm
    success_url = reverse_lazy('main')
    template_name = 'sms-verify.html'

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        phone = self.request.session.get('phone', '')
        kwargs.update({
            'phone': phone,
        })
        return kwargs


class RequestPersonalAreaView(CreateView):
    model = RequestPersonalArea
    form_class = RequestPersonalAreaForm
    template_name = 'request-personal-area.html'
    success_url = '/'


class ResetPasswordView(FormView):
    form_class = ResetPasswordForm
    success_url = reverse_lazy('reset-password-verify')
    template_name = 'reset-password.html'

    def form_valid(self, form):
        """If the form is valid, redirect to the supplied URL."""
        # self.request.session['phone'] = form.person_phone  # "+380950968326"
        # print("form_valid", form.person_phone)

        # sms(self.request, "+380950968326", reverse('reset-password-verify'))
        # sms(self.request, form.person_phone, reverse('reset-password-verify'))

        # url = reverse(
        #     "sms",
        #     kwargs={
        #         "phone": "+380950968326",
        #         "url": reverse('reset-password-verify')
        #     }
        # )
        # return HttpResponseRedirect(url)
        return sms(self.request, "+380950968326", reverse('reset-password-verify'))


class ResetPasswordVerifyView(SMSVerifyView):
    form_class = ResetPasswordVerifyForm
    success_url = reverse_lazy('reset-password-confirm')


class ResetPasswordConfirmView(FormView):
    form_class = AdminPasswordChangeForm
    success_url = reverse_lazy('profile')
    template_name = 'enter-password.html'

    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        phone = self.request.session.get('phone', '')
        print("ResetPasswordConfirmView", phone)
        if phone:
            phone = phone.split("+")[1]
        kwargs['user'] = User.objects.get(mobile_phone=phone)
        print("USERR", kwargs['user'])
        return kwargs

    def form_valid(self, form):
        form.save()
        # Updating the password logs out all other sessions for the user
        # except the current one.
        update_session_auth_hash(self.request, form.user)

        # set checkbox in user profile
        current_user = User.objects.get(id=form.user.id)
        current_user.changed_default_password = True
        current_user.save()

        return super().form_valid(form)


class CallbackVerifyView(SMSVerifyView):
    form_class = CallbackVerifyForm
    success_url = reverse_lazy('callback_success')

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        bid_id = self.request.session.get('bid_id', '')
        bid = Bid.objects.filter(id=int(bid_id))
        if bid:
            kwargs.update({
                'bid': bid[0]
            })
        return kwargs


class RegisterVerifyView(SMSVerifyView):
    form_class = RegisterVerifyForm
    success_url = reverse_lazy('questionnaire')
    user = None

    def form_valid(self, form):
        user_id = self.request.session.pop('user_id', '')
        mobile_phone = form.phone
        print('form_valid mobile_phone', mobile_phone)
        if not user_id:
            return HttpResponseRedirect(reverse('login'))

        user = User.objects.filter(id=int(user_id))[0]
        print('form_valid user', user)

        if user:
            password = make_user_password(user)
            auth_user = authenticate(mobile_phone=user.mobile_phone, password=password)
            print("auth_user 1", auth_user)
            if auth_user is not None:
                print("auth_user 2", auth_user)
                login(self.request, auth_user)
                return HttpResponseRedirect(self.get_success_url())
        return HttpResponseRedirect(reverse('login'))


class QuestionnaireView(TemplateView):
    template_name = 'questionnaire.html'

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super(QuestionnaireView, self).get_context_data(*kwargs)
        context['form_step1'] = RegisterPersonalStep1Form()
        context['form_step2'] = RegisterPersonalStep2Form()
        context['form_step3'] = RegisterPersonalStep3Form()
        context['form_step4'] = RegisterPersonalStep4Form()
        context['form_step5'] = RegisterPersonalStep5Form()
        anketa_exists = Questionnaire.objects.filter(
            user=self.request.user
        ).exists()
        if anketa_exists:
            anketa_object = Questionnaire.objects.filter(
                user=self.request.user
            ).values()[0]
            context['form'] = RegisterPersonalForm(initial=anketa_object)
        else:
            context['form'] = RegisterPersonalForm()
        return context


@csrf_exempt
def questionnaire_step1(request):
    if request.method == 'POST':
        print("step", request.POST.get('step'))
        form = RegisterPersonalStep1Form(data=request.POST)
        if form.is_valid():
            print('ok')
            step_obj = form.save()
            step_obj.user = request.user
            return JsonResponse(
                {
                    'result': 'ok',
                    'errors': None
                },
                safe=False
            )
        else:
            print(form.errors)
            for err in form.errors:
                print(err)
        return JsonResponse(
            {
                'result': 'bad',
                'errors': form.errors
            },
            safe=False
        )


class SaveQuestionnaireStepView(View):
    @method_decorator(csrf_exempt)
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)

    def post(self, *args, **kwargs):
        print("args", self.request.POST)
        # print("step", self.request.POST.get("step"))
        # step = self.request.POST.get('step')
        anketa_exists = Questionnaire.objects.filter(
            user=self.request.user
        ).exists()

        if not anketa_exists:
            if self.request.user.is_authenticated:
                form = RegisterPersonalForm(data=self.request.POST)
                if form.is_valid():
                    anketa = form.save(commit=False)
                    anketa.user = self.request.user
                    anketa.save()
                else:
                    return JsonResponse(
                        {
                            'result': 'bad0',
                            'errors': form.errors
                        },
                        safe=False
                    )
            else:
                return JsonResponse(
                    {
                        'result': 'bad1',
                        'errors': form.errors
                    },
                    safe=False
                )
        else:
            # data_dict = dict(self.request.POST)
            data_dict = self.request.POST.dict()
            if 'switchResidence' in data_dict:
                data_dict.pop('switchResidence')
            if 'the-same' in data_dict:
                data_dict.pop('the-same')
            if 'step' in data_dict:
                data_dict.pop('step')
            if 'registration_county_switch' in data_dict:
                data_dict.pop('registration_county_switch')
            if 'residence_county_switch' in data_dict:
                data_dict.pop('residence_county_switch')
            if 'switchRegistration' in data_dict:
                data_dict.pop('switchRegistration')
            if 'birthday_date' in data_dict:
                if data_dict['birthday_date']:
                    data_dict['birthday_date'] = datetime.strptime(data_dict.get('birthday_date'), '%Y-%m-%d')
                else:
                    data_dict['birthday_date'] = datetime.strptime('9999-01-01', '%Y-%m-%d')
            if 'passport_date' in data_dict:
                if data_dict['passport_date']:
                    data_dict['passport_date'] = datetime.strptime(data_dict.get('passport_date'), '%Y-%m-%d')
                else:
                    data_dict['passport_date'] = datetime.strptime('9999-01-01', '%Y-%m-%d')
            if 'passport_outdate' in data_dict:
                if data_dict['passport_outdate']:
                    data_dict['passport_outdate'] = datetime.strptime(data_dict.get('passport_outdate'), '%Y-%m-%d')
                else:
                    data_dict['passport_outdate'] = datetime.strptime('9999-01-01', '%Y-%m-%d')
            if 'has_criminal_record' in data_dict:
                if data_dict['has_criminal_record'] == 'off':
                    data_dict['has_criminal_record'] = False
                else:
                    data_dict['has_criminal_record'] = True
            pprint(data_dict)
            anketa_qs = Questionnaire.objects.filter(
                user=self.request.user
            ).update(
                **data_dict
            )

            if int(self.request.POST["step"]) == 5:
                # id_mess = CallbackSuccessForm.get_solo().success.id
                # url = reverse('success', kwargs={
                #     'redirect_url': 'profile',
                #     'id_mess': id_mess
                # })
                print("step 5")
                resp = check_blacklist(
                    itn=self.request.user.anketa.itn,
                    mobile_phone=self.request.user.anketa.mobile_phone,
                    passseria=self.request.user.anketa.passport_code[:2] if self.request.user.anketa.passport_code else 'АА',
                    passnumber=self.request.user.anketa.passport_code[1:] if self.request.user.anketa.passport_code else 000000,
                )
                print("resp", resp)
                if 'in_blacklist' in resp:
                    if resp['in_blacklist']:
                        user = User.objects.filter(
                            id=self.request.user.id
                        )[0]
                        anketa_qs = Questionnaire.objects.filter(
                            user=user
                        ).update(
                            blacklist=True
                        )
                        user.active = False
                        user.save()
                    else:
                        user = User.objects.filter(
                            id=self.request.user.id
                        )[0]
                        user.ready_for_turnes = True
                        user.save()
                return JsonResponse(
                    {
                        'result': 'ok',
                        'errors': None,
                        'url': reverse('profile')
                    },
                    safe=False
                )
        print("kwargs", kwargs)
        return JsonResponse(
            {
                'result': 'ok',
                'errors': None
            },
            safe=False
        )
