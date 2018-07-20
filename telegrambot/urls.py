from django.contrib import admin
from django.urls import path
from django.conf import settings

from .views import (
    test_bot
)


app_name = 'telegrambot'  # need for include function in root urls.py

urlpatterns = [
    path('text/', test_bot, name='text'),
]
