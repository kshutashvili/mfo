from django.shortcuts import render
from django.http import (
    HttpResponseRedirect, JsonResponse,
    HttpResponseBadRequest
)
from django.utils.translation import ugettext_lazy as _
from django.urls import reverse, reverse_lazy
from django.contrib.auth import (
    authenticate, login, logout, update_session_auth_hash
)
from django.contrib.auth.decorators import login_required
from django.core.validators import validate_email
from django.core.exceptions import ValidationError
from django.views.generic import CreateView
from django.views.generic.edit import FormView
from django.utils.decorators import method_decorator

from bids.models import Bid
from communication.forms import WriteCommentForm, WriteQuestionForm
from communication.models import UserExistMessage, UserQuestion
from communication.views.sms import sms
from content.helpers import clear_contact_phone
from payments.forms import PayForm
from users.forms import (
    SetPasswordForm,
    RegisterNumberForm,
    LoginForm,
    RequestPersonalAreaForm,
    AdminPasswordChangeForm,
    ResetPasswordForm,
    ResetPasswordVerifyForm,
    CallbackConfirmForm
)
from users.models import Profile, RequestPersonalArea, User
from users.utils import test_user_turnes


def register(request):
    if request.method == 'POST':
        form = RegisterNumberForm(request.POST)
        if form.is_valid():
            phone = form.cleaned_data.get('phone')
            user_exist = Profile.objects.filter(phone=phone).first()
            if user_exist and user_exist.user.is_active:
                id_mess = UserExistMessage.get_solo().page.id
                url = reverse('success', kwargs={'redirect_url':'login',
                                                 'id_mess':id_mess})
                return HttpResponseRedirect(url)
            elif user_exist and user_exist.user.is_active == False:
                url = reverse('sms', kwargs={'phone': phone})
                return HttpResponseRedirect(url)
            else:
                user = Profile()
                us = User(username=phone)
                us.is_active = False
                us.save()
                user.user = us
                user.phone = phone
                user.save()
                url = reverse('sms', kwargs={'phone':phone})
                return HttpResponseRedirect(url)
        else:
            status_message = _('Неправильный номер')
            url = reverse('callback', kwargs={'status_message':status_message})
            return HttpResponseRedirect(url)


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
        self.request.session['phone'] = form.person_phone  # "+380950968326"
        # print("form_valid", form.person_phone)

        # sms(self.request, "+380950968326", reverse('reset-password-verify'))
        sms(self.request, form.person_phone, reverse('reset-password-verify'))

        # url = reverse(
        #     "sms",
        #     kwargs={
        #         "phone": "+380950968326",
        #         "url": reverse('reset-password-verify')
        #     }
        # )
        # return HttpResponseRedirect(url)
        return HttpResponseRedirect(self.get_success_url())


class ResetPasswordVerifyView(FormView):
    form_class = ResetPasswordVerifyForm
    success_url = reverse_lazy('reset-password-confirm')
    template_name = 'reset_password_verify.html'

    def get_form_kwargs(self):
        """Return the keyword arguments for instantiating the form."""
        kwargs = super().get_form_kwargs()
        phone = self.request.session.get('phone', '')
        print("get_form_kwargs", phone)
        kwargs.update({
            'phone': phone,
        })
        return kwargs


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


class CallbackConfirmView(FormView):
    form_class = CallbackConfirmForm
    success_url = reverse_lazy('callback_success')
    template_name = 'form-callback-confirm.html'

    def get_form_kwargs(self):
        """Return the keyword arguments for instantiating the form."""
        kwargs = super().get_form_kwargs()
        phone = self.request.session.get('phone', '')
        bid_id = self.request.session.get('bid_id', '')
        print("get_form_kwargs", phone)
        bid = Bid.objects.filter(id=int(bid_id))
        if bid:
            print("BID", bid_id, bid[0])
            kwargs.update({
                'phone': phone,
                'bid': bid[0]
            })
        else:
            kwargs.update({
                'phone': phone,
            })
        return kwargs
