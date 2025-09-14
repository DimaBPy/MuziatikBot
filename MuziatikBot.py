"""
This is a legacy version of MuziatikBot!
The new version is bot.py


A bot that interacts with users to provide reminders, cat-related media, personalized greetings,
and enables controlled access to a virtual "house". The bot uses the aiogram framework for
Telegram Bot API integration.

Modules included:
- aiogram: Provides bot-building capabilities.
- apscheduler: Schedules background tasks.
- dotenv: Loads environment variables from a .env file.
- asyncio: Handles asynchronous tasks.
- Other supporting modules for threading, randomization, and HTTP requests.

Exported functions:
- process_start_command: Welcomes the user upon issuing the "start" command.
- my_name: Replies with the user's Telegram display name and username.
- cats: Shares randomized cat-related media.
- home: Initiates interaction for controlled house entry/exit with user approval.
- may_go_house: Handles inline keyboard callbacks confirming house entry/exit.
- go_house: Completes the interaction related to guest house entry/exit.

The bot is designed to be conversational and execute tasks based on user interaction.
"""

import asyncio
import datetime
import os
import random
import threading
import time

import requests
from aiogram import Bot, Dispatcher, F
from aiogram.filters import Command
from aiogram.types import Message, ReplyKeyboardMarkup, KeyboardButton, \
    InlineKeyboardButton, InlineKeyboardMarkup, CallbackQuery
from dotenv import load_dotenv
from parser import get_flowers, cats_url
from apscheduler.schedulers.asyncio import AsyncIOScheduler

scheduler = AsyncIOScheduler()
load_dotenv()
button1 = KeyboardButton(text='Поставь напоминание')
button2 = KeyboardButton(text='Котики!')
button3 = KeyboardButton(text='Как меня зовут?')
button4 = KeyboardButton(text='Домик')
button5 = KeyboardButton(text='Отзыв')
keyboard = ReplyKeyboardMarkup(keyboard=[[button1, button2],
                                         [button3, button4],
                                         [button5]],
                               resize_keyboard=True)
inline_dima = InlineKeyboardButton(text='Для Димы', callback_data='Для Димы')
inline_dad = InlineKeyboardButton(text='Для CoРазработчика',
                                  callback_data='Для CoРазработчика')
inline_mom = InlineKeyboardButton(text='Для Алёны', callback_data='Для Алёны')
inline_granny = InlineKeyboardButton(text='Для Наташи',
                                     callback_data='Для Наташи')
yes = InlineKeyboardButton(text='да', callback_data='да')
no = InlineKeyboardButton(text='нет', callback_data='нет')
inline_keyboard = InlineKeyboardMarkup(
    inline_keyboard=[[inline_dima, inline_mom],
                     [inline_dad, inline_granny]])
yes_no = InlineKeyboardMarkup(inline_keyboard=[[yes, no]])
API_TOKEN_muziatikBot = os.getenv('API_TOKEN_muziatikBot')
MY_CHAT_ID = os.getenv('MY_CHAT_ID')
bot = Bot(API_TOKEN_muziatikBot)
dp = Dispatcher()

# bot.send_message(os.getenv('MY_CHAT_ID'),
#                  '_Новости:_\nК сожалению, ставить напоминания сейчас '
#                  'неочень удобно(могут быть ошибки):(. Но вы можете всё '
#                  'равно можете попробовать:)! Если в конце бот не написал '
#                  '"напоминание поставлено", значит кто-то другой, или вы '
#                  'поставили другое напоминание, и новое не поставится.',
#                  parse_mode="Markdown")
# bot.send_message(os.getenv('MOMMY_CHAT_ID'),
#                  '_Новости:_\nК сожалению, ставить напоминания сейчас '
#                  'неочень удобно(могут быть ошибки):(. Но вы можете всё '
#                  'равно можете попробовать:)! Если в конце бот не написал '
#                  '"напоминание поставлено", значит кто-то другой, или вы '
#                  'поставили другое напоминание, и новое не поставится.',
#                  parse_mode="Markdown")
# bot.send_message(os.getenv('DADDY_CHAT_ID'),
#                  '_Новости:_\nК сожалению, ставить напоминания сейчас '
#                  'неочень удобно(могут быть ошибки):(. Но вы можете всё '
#                  'равно можете попробовать:)! Если в конце бот не написал '
#                  '"напоминание поставлено", значит кто-то другой, или вы '
#                  'поставили другое напоминание, и новое не поставится.',
#                  parse_mode="Markdown")
# bot.send_message(os.getenv('GRANNY_CHAT_ID'),
#                  '_Новости:_\nК сожалению, ставить напоминания сейчас '
#                  'неочень удобно(могут быть ошибки):(. Но вы можете всё '
#                  'равно можете попробовать:)! Если в конце бот не написал '
#                  '"напоминание поставлено", значит кто-то другой, или вы '
#                  'поставили другое напоминание, и новое не поставится.',
#                  parse_mode="Markdown")
# bot.send_message(os.getenv('ALYONA_CHAT_ID'),
#                  'Временно не работают напоминания:(', parse_mode="Markdown")

is_ = None


@dp.message(Command(commands=["start"]))
async def process_start_command(message: Message):
    await message.answer('Здравствуйте!')


@dp.message(lambda msg: msg.text == 'Как меня зовут?')
async def my_name(message: Message):
    await message.reply(
        f'Вас зовут _{message.chat.first_name}_\nИмя пользователя(username) '
        f'— __{message.chat.username}__',
        reply_markup=keyboard, parse_mode='Markdown')


@dp.message(lambda msg: msg.text == 'Котики!')
async def cats(message: Message):
    await message.reply_photo(cats_url(),
                              reply_markup=keyboard)


who_will_go_house = None


@dp.message(lambda msg: msg.text == 'Домик')
async def home(message: Message):
    global who_will_go_house
    who_will_go_house = message.chat.id
    await message.reply(
        'Вы хотите _войти/выйти_ _в/из_ домик_(а)_ *Музятика*?',
        parse_mode='Markdown',
        reply_markup=yes_no)


@dp.callback_query(F.data.in_(['да']))
async def may_go_house(callback: CallbackQuery):
    await callback.answer(text='Ок! Сейчас!')
    await bot.send_message(callback.message.chat.id,
                           'Пожалуйста, подождите…'
                           '\n'
                           '\n'
                           'Если Дима нажмёт *нет* — Я ничего вам не отвечу, '
                           'а если Дима нажмёт *да* — то-о-о…\n'
                           'Сами увидите😁️', parse_mode='Markdown')
    await bot.send_message(MY_CHAT_ID,
                           'Хочешь ли ты, '
                           'чтобы кто-то вошел в твой домик?')
    await bot.send_message(os.getenv('MY_CHAT_ID'), 'Напиши _да_ или _нет_',
                           parse_mode='Markdown')


guest = False


@dp.message(F.text.regexp(r'[дД][Аа]'))
async def go_house(message: Message):
    global guest
    await message.reply('Гости!')
    guest = True if not guest else False
    print(guest)
    await bot.send_message(who_will_go_house, 'Открытие Домика…')
    await bot.send_message(MY_CHAT_ID, 'Открытие Домика…')
    await asyncio.sleep(5)
    await bot.send_message(who_will_go_house,
                           'Можете _заходить_ в __Домик__' if guest is True
                           else 'Можете _выходить_ из _Домика_',
                           parse_mode='Markdown')
    await bot.send_message(MY_CHAT_ID,
                           'Можете _заходить_ в __Домик__' if guest is True
                           else 'Можете _выходить_ из _Домика_',
                           parse_mode='Markdown')
    await asyncio.sleep(3)
    close = await bot.send_message(who_will_go_house,
                                   'Двери Домика закроются через 10 секунд')
    close_my = await bot.send_message(MY_CHAT_ID,
                                      'Двери Домика закроются через 10 секунд')
    for i in range(10, 0, -1):
        await asyncio.sleep(1)
        await bot.edit_message_text(text=f'Двери Домика закроются через {i} '
                                         f'секунд',
                                    chat_id=who_will_go_house,
                                    message_id=close.message_id)
        await bot.edit_message_text(text=f'Двери Домика закроются через {i} '
                                         f'секунд',
                                    chat_id=MY_CHAT_ID,
                                    message_id=close_my.message_id)
    await bot.send_message(who_will_go_house, 'Закрытие домика…')
    await bot.send_message(MY_CHAT_ID, 'Закрытие домика…')
    await asyncio.sleep(5)
    await bot.send_message(who_will_go_house, 'Домик закрыт!')
    await bot.send_message(MY_CHAT_ID, 'Домик закрыт!')


@dp.message(lambda msg: msg.text == 'Отзыв')
async def feedback(message: Message):
    global is_
    is_ = 'feedback'
    await message.reply_photo(random.choice(get_flowers()))
    await message.reply(
        '_Напишите отзыв_ после того как я напишу "…"\n',
        parse_mode="Markdown",
        reply_markup=keyboard)
    await asyncio.sleep(3)
    await bot.send_message(message.chat.id, '…')


async def error(message: Message):
    await message.reply(f'{message.chat.first_name}, Такой команды ещё нет :(')


@dp.message(lambda msg: msg.text == 'Поставь напоминание')
async def reminder(message: Message):
    await message.reply('Для кого хотите поставить напоминание?',
                        reply_markup=inline_keyboard)


who = None


@dp.callback_query(
    F.data.in_(['Для Димы', 'Для Алёны', 'Для CoРазработчика', 'Для Наташи']))
async def what(callback: CallbackQuery):
    global is_
    global who
    is_ = 'reminder'
    inline_button = callback.data
    if callback.data == 'Для Димы':
        await callback.answer(text='Ок. Для Димы')
        who = os.getenv('MY_CHAT_ID')
    elif callback.data == 'Для Алёны':
        who = os.getenv('MOMMY_CHAT_ID')
    elif callback.data == 'Для CoРазработчика':
        who = os.getenv('DADDY_CHAT_ID')
    elif callback.data == 'Для Наташи':
        who = os.getenv('GRANNY_CHAT_ID')
    await callback.message.edit_text('О чём напомнить?')
    await asyncio.sleep(3)
    await callback.message.delete()
    await bot.send_message(callback.message.chat.id, 'О чём напомнить?')
    await callback.answer()


what_remind = None
when_remind = None


@dp.message()
async def just_text(message: Message):
    global is_
    global when_remind
    if is_ == 'feedback':
        await message.reply('Регистрируем отзыв…', reply_markup=keyboard)
        await asyncio.sleep(2)
        await bot.send_message(MY_CHAT_ID,
                               f'Feedback:\n'
                               f'Who?: {message.chat.first_name}\n'
                               f'Username: {message.chat.username}\n'
                               f'{message.text}')
        await asyncio.sleep(2)
        await message.reply('Отзыв зарегистрирован!')
    elif is_ == 'reminder' and not message.text[0].isdigit():
        global what_remind
        what_remind = message.text
        print(f'what remind {what_remind}')
        await message.reply('Когда?')
        await asyncio.sleep(3)
        await bot.send_message(message.chat.id,
                               'В формате:\n'
                               'дд.мм ЧЧ:ММ\n'
                               'Например:\n'
                               '31.08 23:59')
        await asyncio.sleep(3)
        await bot.send_message(message.chat.id,
                               '*Важно*! Символы: ":", "." и пробел '
                               '**нельзя** пропускать или заменять!',
                               parse_mode='Markdown')
        # await message.reply(f'Напоминание _{what_remind}_ зарегистрировано!',
        #                        parse_mode='Markdown')
    elif message.text[0].isdigit():
        await message.reply('Запускаю процесс создания напоминания…')
        await asyncio.sleep(2)
        await bot.send_message(message.chat.id, 'Узнаю текущий год…')
        await asyncio.sleep(3)
        year = int(datetime.datetime.now().strftime('%y'))
        await bot.send_message(message.chat.id, 'Узнаю нужный месяц…')
        await asyncio.sleep(3)
        month = int(message.text[4])
        await bot.send_message(message.chat.id, 'Узнаю нужный день…')
        await asyncio.sleep(3)
        day = int(message.text[:2])
        await bot.send_message(message.chat.id, 'Узнаю нужный час…')
        await asyncio.sleep(3)
        hour = int(message.text[-5:-3])
        await bot.send_message(message.chat.id, 'Узнаю нужную минуту…')
        await asyncio.sleep(3)
        minute = int(message.text[-2:])
        # await scheduler.add_job(send_rm, "date",
        #                         run_date=datetime.datetime(
        #                             year=2024, month=month, day=day, hour=hour,
        #                             minute=minute, second=0), args=(message,))
        when_remind = {'month': month, 'day': day, 'hour': hour,
                       'minute': minute,
                       'message': message}
        await bot.send_message(message.chat.id,
                               f'Напоминание — {what_remind},'
                               f' на __{message.text}__ зарегистрировано!',
                               parse_mode='Markdown')
    else:
        await error(message)


async def send_rm(message):
    await bot.send_message(who, f'Напоминаю: _{what_remind}_',
                           parse_mode='Markdown')
    await scheduler.remove_all_jobs()


if when_remind is not None:
    scheduler.add_job(send_rm, "date",
                      run_date=datetime.datetime(
                          year=2024,
                          month=when_remind['month'],
                          day=when_remind['day'],
                          hour=when_remind['hour'],
                          minute=when_remind['minute'],
                          second=0),
                      args=(when_remind['message'],))
    scheduler.start()
dp.run_polling(bot, polling_timeout=10)
