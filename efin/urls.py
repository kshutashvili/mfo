"""efin URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, re_path, include
from django.views.generic import TemplateView
from django.conf import settings
from django.conf.urls.i18n import i18n_patterns
from django.conf.urls.static import static
from django.contrib.auth.decorators import login_required

from communication.views import contacts, about, blog, faq, resume,\
                                success_message, sms
from content.views import content
from vacancy.views import job
from users.views import (
    register,
    set_password,
    user_login,
    user_logout,
    profile,
    alter_profile,
    message_read,
    RequestPersonalAreaView,
    FirstChangePassword,
    ResetPasswordView,
    ResetPasswordVerifyView,
    ResetPasswordConfirmView,
    CallbackVerifyView,
    RegisterVerifyView,
    QuestionnaireView,
    questionnaire_step1,
    SaveQuestionnaireStepView
)
from payment_gateways.views import (pb_terminal_view, easypay_terminal_view,
                                    city24_terminal_view, TurnesView)
from bankid.views import protected_view


urlpatterns = i18n_patterns(
    path('admin/', admin.site.urls),

    path('loan/', content.index, name='index'),
    path('', content.main, name='main'),

    path('kak-poluchit-kredit/', content.CallbackView.as_view(), name='callback'),
    path('kak-poluchit-kredit/<str:status_message>/', content.CallbackView.as_view(), name='callback'),

    path('request-callback/', content.request_callback, name='request_callback'),
    path('callback-verify/', CallbackVerifyView.as_view(), name='callback_verify'),
    path('callback-success/', content.CallbackSuccessView.as_view(), name='callback_success'),
    path('save_credit_request/', content.save_credit_request, name='save_credit_request'),

    path('download_pdf/<int:spoiler_id>/', content.download_pdf, name='download_pdf'),
    path('open_pdf/<int:spoiler_id>/', content.open_pdf, name='open_pdf'),

    path('translate/<str:lang_code>/', content.translate, name='translate'),
    path('job/', job.job, name='job'),
    path('questionnaire/', QuestionnaireView.as_view(), name='questionnaire'),
    path('questionnaire-step1/', questionnaire_step1, name='questionnaire-step1'),
    path('questionnaire-steps/', SaveQuestionnaireStepView.as_view(), name='save-questionnaire'),

    path('login/', user_login, name='login'),
    # path('login/<str:status_message>/', user_login, name='login'),
    path('logout/', user_logout, name='logout'),

    path('register/', register, name='register'),
    path('register-verify/', RegisterVerifyView.as_view(), name='register_verify'),

    path('password/', FirstChangePassword.as_view(), name='set_password'),
    path('sms/<str:phone>/', sms.sms, name='sms'),
    path('reset/', ResetPasswordView.as_view(), name="reset-password"),
    path('reset-verify/', ResetPasswordVerifyView.as_view(), name='reset-password-verify'),
    path('reset-confirm/', ResetPasswordConfirmView.as_view(), name='reset-password-confirm'),

    path('my/', login_required(profile), name='profile'),
    path('my/<str:active>/', login_required(profile), name='profile'),
    path('my/<str:active>/<str:page>/', login_required(profile), name='profile'),

    path('change_email/', login_required(sms.change_email), name='change_email'),
    re_path(r'^email_confirm/(?P<uidb64>[0-9A-Za-z_\-]+)/(?P<token>[0-9A-Za-z]{1,13}-[0-9A-Za-z]{1,20})',
            sms.email_confirm, name='email_confirm'),
    path('payonline/', TemplateView.as_view(template_name='form-payment.html'), name='payonline'),

    path('pro-kompaniyu/', about.about, name='about'),
    path('about/contacts/', contacts.contacts, name='contacts'),
    path('blog/', blog.blog, name='blog'),
    path('blog/item<int:item_id>/', blog.blog_item, name='blog_item'),
    path('blog/<str:category_link>/', blog.blog_category, name='blog_category'),
    path('faq/', faq.faq, name='faq'),
    path('resume/', resume.resume, name='resume'),

    path('message/<int:id_mess>/', success_message.success_message, name='success'),
    path('message/<int:id_mess>/<str:redirect_url>/', success_message.success_message, name='success'),

    path('test_turnes1/', TurnesView.as_view(), name="test_turnes"),

    path('ajax/departments_generate/<str:dep_id>/', content.departments_generate, name='departments_generate'),
    path('ajax/slider_filler/', content.slider_filler, name='slider_generate'),
    path('ajax/credit_calculate/<int:rate_id>/<int:term>/<int:summ>/', content.credit_calculator, name='cred_calc'),
    path('ajax/comment_add/', content.comment_add, name='comment_add'),
    path('question_add/', content.question_add, name='question_add'),
    path('ajax/question_generate/', login_required(content.question_generate), name='question_generate'),
    path('ajax/profile_alter/', login_required(alter_profile), name='alter_profile'),
    path('ajax/message_read/', login_required(message_read), name='message_read'),

    path('pay/', include('payments.urls', namespace='payments')),
    path('request_personal_area/', RequestPersonalAreaView.as_view(), name="request-personal-area"),

    path('<str:page_url>/', content.pages, name='static_pages'),

    path('bankid/', include('bankid.urls', namespace='bankid')),
)

urlpatterns += [
    path('payment/pb/', pb_terminal_view, name='pb_terminal'),
    path('payment/easypay/', easypay_terminal_view, name='easypay_terminal'),
    path('payment/city24/', city24_terminal_view, name='city24_terminal'),
]

if settings.DEBUG:
    urlpatterns += static(
        settings.MEDIA_URL,
        document_root=settings.MEDIA_ROOT
    )
    # protected media
    urlpatterns += static(
        settings.PROTECTED_MEDIA_URL,
        document_root=settings.PROTECTED_MEDIA_ROOT
    )
else:
    urlpatterns += [
        re_path(
            r'^{}/(?P<path>.*)$'.format(settings.PROTECTED_MEDIA_URL),
            protected_view
        )
    ]


if 'rosetta' in settings.INSTALLED_APPS:
    urlpatterns += [
        path('rosetta/', include('rosetta.urls'))
    ]
