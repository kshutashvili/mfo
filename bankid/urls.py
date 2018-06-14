from django.contrib import admin
from django.urls import path
from django.conf import settings

from .views import (
    bankid_getdata,
    BankidView
)


app_name = 'bankid'  # need for include function in root urls.py

urlpatterns = [
    path('getdata/', bankid_getdata, name='getdata'),
    path('auth/', BankidView.as_view(), name='auth'),
]
