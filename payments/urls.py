from django.contrib import admin
from django.urls import path
from django.conf import settings

from .views import (create_payment,
                    success_payment,
                    fail_payment,
                    callback_payment)


app_name = 'payments'  # need for include function in root urls.py

urlpatterns = [
    path('<int:payment_id>/success/', success_payment, name='success'),
    path('<int:payment_id>/fail/', fail_payment, name='fail'),
    path('<int:payment_id>/callback/', callback_payment, name='callback'),
    path('create/', create_payment, name='create'),
]
