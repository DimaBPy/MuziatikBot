import os
import time
from parser import get_flowers
from pprint import pprint

import requests
from telegram import ReplyKeyboardMarkup, Bot
from telegram.ext import Updater, MessageHandler, Filters, CommandHandler
from dotenv import load_dotenv
import random
from bs4 import BeautifulSoup

load_dotenv()
API_TOKEN_muziatikBot = os.getenv('API_TOKEN_muziatikBot')
MY_CHAT_ID = os.getenv('MY_CHAT_ID')

updater = Updater(API_TOKEN_muziatikBot)

button = ReplyKeyboardMarkup([['Поставь напоминание'], ['Котики!'], ['Как меня зовут?'], ['Отзыв']], True, True)
bot = Bot(API_TOKEN_muziatikBot)


# bot.send_message(os.getenv('MY_CHAT_ID'), 'Исправления:\nТеперь можно отправлять отзывы! просто нажмите кнопку "_отзыв_"', parse_mode="Markdown")
# bot.send_message(os.getenv('MOMMY_CHAT_ID'), 'Исправления:\nТеперь можно отправлять отзыв! просто нажмите кнопку "_отзыв_"', parse_mode="Markdown")
# bot.send_message(os.getenv('DADDY_CHAT_ID'), 'Исправления:\nТеперь можно отправлять отзыв просто нажмите кнопку "_отзыв_"', parse_mode="Markdown")
# bot.send_message(os.getenv('GRANNY_CHAT_ID'), 'Исправления:\nТеперь можно отправлять отзыв просто нажмите кнопку "_отзыв_"', parse_mode="Markdown")
# bot.send_message(os.getenv('ALYONA_CHAT_ID'), 'Исправления:\nТеперь можно отправлять отзыв! просто нажмите кнопку "_отзыв_"', parse_mode="Markdown")


def my_name(update, context):
    chat = update.effective_chat
    context.bot.send_message(chat.id, f'Вас зовут {chat.first_name}\nИмя пользователя(username) — {chat.username}',
                             reply_markup=button)


def remember(update, context):
    chat = update.effective_chat
    context.bot.send_message(chat.id, 'Для кого хотите поставить напоминание?', reply_markup=button)


def cats(update, context):
    chat = update.effective_chat
    context.bot.send_photo(chat.id, requests.get('https://api.thecatapi.com/v1/images/search').json()[0].get('url'),
                           reply_markup=button)


def feedback(update, context):
    chat = update.effective_chat
    message = update.effective_message
    context.bot.send_photo(chat.id, random.choice(get_flowers()))
    context.bot.send_message(chat.id,
                             'Напишите отзыв после "…"\n*ВАЖНО* чтобы сообщение начиналось с _Отзыв:_ или _Feedback:_',
                             parse_mode="Markdown",
                             reply_markup=button)
    time.sleep(3)
    context.bot.send_message(chat.id, '…')


def just_text(update, context):
    chat = update.effective_chat
    message = update.effective_message
    print(message)
    if message.text.split()[0] == 'Отзыв' or message.text.split()[0] == 'Отзыв:':
        context.bot.send_message(chat.id, 'Отправляю ваш отзыв…\nPlease wait')
        time.sleep(2)
        context.bot.send_message(MY_CHAT_ID,
                                 f'Feedback:\n'
                                 f'Who?: {chat.first_name}\n'
                                 f'Username: {chat.username}\n'
                                 f'{message.text}')
        time.sleep(2)
        context.bot.send_message(chat.id, 'Ваш отзыв зарегистрирован!')
    else:
        error(update, context)


def error(update, context):
    chat = update.effective_chat
    message = update.effective_message
    print(message)
    context.bot.send_message(chat.id, f'{chat.first_name}, Такой команды ещё нет :(')


# pprint(response.json())
# pprint(response.json()[0])

# updater.dispatcher.add_handler(CommandHandler('my_name', my_name))
# updater.dispatcher.add_handler(CommandHandler('remember', remember))
updater.dispatcher.add_handler(MessageHandler(Filters.text(['Как меня зовут?']), my_name))
updater.dispatcher.add_handler(MessageHandler(Filters.text(['Поставь напоминание']), remember))
updater.dispatcher.add_handler(MessageHandler(Filters.text(['Котики!']), cats))
updater.dispatcher.add_handler(MessageHandler(Filters.text(['Отзыв']), feedback))
updater.dispatcher.add_handler(MessageHandler(Filters.text, just_text))

updater.start_polling(5)
updater.idle()
