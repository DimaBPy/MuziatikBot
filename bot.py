import asyncio
import os
import random

from memory import *
from aiogram import Bot, Dispatcher, Router, types
from aiogram.filters import Command
from aiogram.types import Message, ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton
from dotenv import load_dotenv

load_dotenv()

# ======== Keyboards ========

settings_keyboard = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text='Выбрать имя', callback_data='name')]
])

dev_keyboard = ReplyKeyboardMarkup(keyboard=[
    [KeyboardButton(text='Roll a die')],
    [KeyboardButton(text='info')],
    [KeyboardButton(text='Settings')],
    [KeyboardButton(text='Feedback')],
    [KeyboardButton(text='Reminder (no)'), KeyboardButton(text='Cats! (later)')],
    [KeyboardButton(text='What is my name? (changed)'), KeyboardButton(text='Домик (was good)')]
], resize_keyboard=True)

keyboard = ReplyKeyboardMarkup(keyboard=[
    [KeyboardButton(text='Кубик')],
    [KeyboardButton(text='info'), KeyboardButton(text='Отзыв')],
    [KeyboardButton(text='Настройки (beta)')],
], resize_keyboard=True)

# ======== Config ========

api_token_muziatikbot = os.getenv("API_TOKEN_muziatikBot")
MY_CHAT_ID = int(os.getenv('MY_CHAT_ID'))

router = Router()
keyboard_input = {}


# ======== Helper ========

async def send_typing_indicator(chat_id, bot, wait=1):
    dots = await bot.send_message(chat_id, "...")
    await asyncio.sleep(wait)
    await bot.delete_message(chat_id, dots.message_id)


# ======== Handlers ========

@router.message(Command('start'))
async def start_bot(message: Message):
    await send_typing_indicator(message.chat.id, message.bot)
    await message.answer("Здравствуйте, я **MuziatikBot**.", parse_mode="Markdown")
    await asyncio.sleep(1)
    user_name = get_data(message.from_user.id, "name")
    if not user_name:
        await message.answer('Давайте познакомимся!')
    else:
        await message.answer(f'О! Я вас помню! Вы {user_name}')
    await message.answer(
        "Нажмите на _кнопку_ внизу, чтобы узнать больше обо мне.",
        parse_mode="Markdown",
        reply_markup=ReplyKeyboardMarkup(keyboard=[[KeyboardButton(text='info')]], resize_keyboard=True)
    )


@router.message(lambda msg: msg.text == 'info')
async def info(message: Message, bot: Bot):
    await message.reply_sticker('CAACAgIAAxkBAAEz-itoBW_hmrk-'
                                '933qZ43mWlN1MK_QjAACsQ8AAldGSEutS54Fv2EAAe42BA')
    await asyncio.sleep(3)
    await message.reply(
        'Вот информация о MuziatikBot:\n'
        'Версия — 1.7.2\n'
        'Доступность функций: Выбрать имя — предпросмотр,\n'
        'Возможности Bot_v1 — добавление,\n'
        'Кубик — полная функциональность.\n'
        'Отзыв🆕: добавлено🎉 теперь вы можете оставить отзыв про бота',
        reply_markup=keyboard
    )


@router.message(lambda msg: "Кубик" in msg.text or 'die' in msg.text)
async def dice(message: Message, bot: Bot):
    inline_keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(
            text="Брось кубик (стикер)", callback_data="roll_dice")],
        [InlineKeyboardButton(
            text='Случайное число (текст)', callback_data='text_dice')]
    ])
    await message.answer("Выберите вариант:", reply_markup=inline_keyboard)


@router.callback_query(lambda c: c.data == 'roll_dice')
async def roll_dice(callback_query: types.CallbackQuery, bot: Bot):
    await bot.send_dice(callback_query.from_user.id)


@router.callback_query(lambda c: c.data == "text_dice")
async def text_dice(callback_query: types.CallbackQuery, bot: Bot):
    dice_result = random.randint(1, 6)
    await send_typing_indicator(callback_query.from_user.id, bot)
    await bot.send_message(callback_query.from_user.id, f"Выпало: {dice_result}")


@router.message(lambda msg: msg.text in ['Настройки (beta)', 'Settings'])
async def settings(message: Message):
    global set
    set = await message.reply('Вот _beta_ настройки', reply_markup=settings_keyboard,
                              parse_mode="Markdown")


@router.callback_query(lambda c: c.data == 'name')
async def choose_name(callback_query: types.CallbackQuery, bot: Bot):
    await set.edit_text('Как вас называть?')
    await asyncio.sleep(1)
    await bot.edit_message_reply_markup(
        chat_id=set.chat.id,
        message_id=set.message_id,
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text='ФИ', callback_data='full_name'),
             InlineKeyboardButton(text='имя пользователя', callback_data='username')],
            [InlineKeyboardButton(text='Ввести вручную', callback_data='keyboard_input')],
        ])
    )


@router.callback_query(lambda c: c.data in ['full_name', 'username', 'keyboard_input'])
async def set_name(callback_query: types.CallbackQuery, bot: Bot):
    if callback_query.data == 'full_name':
        name = callback_query.from_user.full_name
        save_data(callback_query.from_user.id, "name", name)
        await send_typing_indicator(callback_query.message.chat.id, bot)
        await bot.send_message(callback_query.message.chat.id, f'Хорошо, {name}')
    elif callback_query.data == 'username':
        name = callback_query.from_user.username
        save_data(callback_query.from_user.id, "name", name)
        await send_typing_indicator(callback_query.message.chat.id, bot)
        await bot.send_message(callback_query.message.chat.id, f'Хорошо, {name}')
    else:
        await send_typing_indicator(callback_query.message.chat.id, bot)
        keyboard_input[callback_query.from_user.id] = 'name'
        await bot.send_message(callback_query.message.chat.id, f'Хорошо, пишите')


@router.message(lambda msg: msg.text == 'dev')
async def dev(message: Message):
    await send_typing_indicator(message.chat.id, message.bot, wait=2)
    await message.reply('Проверяю')
    await send_typing_indicator(message.chat.id, message.bot, wait=3)
    if message.from_user.id == MY_CHAT_ID or message.from_user.id == os.getenv('DADDY_CHAT_ID'):
        await message.reply('Okei-dokei', reply_markup=dev_keyboard)
    else:
        await message.reply('Вы не разработчик')


@router.message(lambda msg: msg.text == 'Отзыв' or msg.text == 'Feedback')
async def feedback(message: Message):
    global keyboard_input
    keyboard_input[message.from_user.id] = 'feedback'
    await send_typing_indicator(message.chat.id, message.bot)
    await message.reply('_Напишите_ Ваш отзыв (бета версия)', parse_mode="Markdown")


@router.message()
async def everything(message: Message, bot: Bot):
    if keyboard_input.get(message.from_user.id) == 'name':
        save_data(message.from_user.id, "name", message.text)
        del keyboard_input[message.from_user.id]
        await message.answer(f'Запомнил! Теперь вы — {message.text}')
    elif keyboard_input.get(message.from_user.id) == 'feedback':
        await message.answer('Пишу моему создателю')
        await send_typing_indicator(message.from_user.id, bot)
        await bot.send_message(MY_CHAT_ID, f'Эй, бро у тебя отзыв.\n{message.text}')
        await message.reply('Написал')
        await send_typing_indicator(message.from_user.id, bot)
        await message.answer('Кстати, скоро у отзывов будут свои идентификаторы🔜')
        del keyboard_input[message.from_user.id]
    else:
        await message.reply(
            'Используйте кнопки (должны быть снизу экрана), а если их нет: нажмите 4 квадрата слева от скрепки')


# ======== Main ========

async def main():
    bot = Bot(api_token_muziatikbot)
    dp = Dispatcher()
    dp.include_router(router)
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
