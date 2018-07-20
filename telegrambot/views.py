from pprint import pprint

import telepot
from telepot.loop import MessageLoop

from django.shortcuts import render
from django.http import HttpResponse, JsonResponse


bot = telepot.Bot('684168816:AAHSrBnlrRRnVayoU-VH91FA233fKrD-cdQ')
bot.setWebhook('https://expressfinance.com.ua/tele/text/')


def test_bot(request):
    # print(bot.getMe())
    # req = bot.getUpdates()

    # content_type, chat_type, chat_id = telepot.glance(req[0]['message'])
    # print(content_type, chat_type, chat_id)
    # MessageLoop(bot, handle).run_as_thread()

    bot.sendMessage('87982276', 'Привіт')
    bot.sendMessage('87982276', request.body.decode('UTF8'))

    return JsonResponse({}, status=200)
