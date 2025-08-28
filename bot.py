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
    [InlineKeyboardButton(text='Выбрать имя', callback_data='name')],
    [InlineKeyboardButton(text='Запомнить', callback_data='remember')],
    [InlineKeyboardButton(text='Вспомнить', callback_data='recall')],
    [InlineKeyboardButton(text='Забыть', callback_data='forget')]
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
    [KeyboardButton(text='Настройки')],
], resize_keyboard=True)

# ======== Config ========

api_token_muziatikbot = os.getenv("API_TOKEN_muziatikBot")

try:
    MY_CHAT_ID = int(os.getenv('MY_CHAT_ID'))
except TypeError as e:
    print(f'Ключа та нет... :\n{e}')

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
        f'Вот информация о MuziatikBot, {get_data(message.from_user.id, 'name')}:\n'
        'Версия — 2.0🆕🎉😎\n'
        'Доступность функций: Выбрать имя — Полная функциональность,\n'
        'Кубик — полная функциональность.\n'
        'Отзыв🆕: Теперь вы можете оставить отзыв про бота!'
        'Память🧠: Публичный предпросмотр',
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
    await asyncio.sleep(4)
    await callback_query.answer()


@router.callback_query(lambda c: c.data == "text_dice")
async def text_dice(callback_query: types.CallbackQuery, bot: Bot):
    dice_result = random.randint(1, 6)
    await send_typing_indicator(callback_query.from_user.id, bot)
    await bot.send_message(callback_query.from_user.id, f"Выпало: {dice_result}")
    await callback_query.answer(f"Выпало: {dice_result}", show_alert=True)


@router.message(lambda msg: msg.text in ['Настройки', 'Settings'])
async def settings(message: Message):
    global sett
    sett = await message.reply('Вот настройки', reply_markup=settings_keyboard,
                               parse_mode="Markdown")


@router.callback_query(lambda c: c.data == 'name')
async def choose_name(callback_query: types.CallbackQuery, bot: Bot):
    await sett.edit_text('Как вас называть?')
    await callback_query.answer()
    await asyncio.sleep(1)
    await bot.edit_message_reply_markup(
        chat_id=sett.chat.id,
        message_id=sett.message_id,
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
        await callback_query.answer(f'Хорошо, {name}')
        # await bot.send_message(callback_query.message.chat.id, f'Хорошо, {name}')
    elif callback_query.data == 'username':
        name = callback_query.from_user.username
        save_data(callback_query.from_user.id, "name", name)
        await callback_query.answer(f'Хорошо, {name}')
        # await bot.send_message(callback_query.message.chat.id, f'Хорошо, {name}')
    else:
        await send_typing_indicator(callback_query.message.chat.id, bot)
        keyboard_input[callback_query.from_user.id] = 'name'
        await callback_query.answer('Хорошо, пишите', show_alert=True)
        # await bot.send_message(callback_query.message.chat.id, 'Хорошо, пишите')


@router.callback_query(lambda c: c.data == 'remember' or c.data == 'recall' or c.data == 'forget')
async def memory(callback_query: types.CallbackQuery):
    if callback_query.data == 'remember':
        await callback_query.answer('Правила: Ключ писать без пробелов, затем пробел и значение без пробелов',
                                    show_alert=True)
        keyboard_input[callback_query.from_user.id] = 'remember'
        await callback_query.message.answer('Пример:\nцвет голубой'
                                            '\nпокупки голубика_клубника_помидоры')

    elif callback_query.data == 'recall':
        await callback_query.answer('Вспоминаю...')
        asyncio.create_task(send_typing_indicator(callback_query.message.chat.id, callback_query.bot))
        await callback_query.message.answer(
            '\n'.join(f'{"Имя" if key == "name" else key}: {value}' for key, value in
                      get_data(callback_query.from_user.id).items()))

    else:
        keyboard_input[callback_query.from_user.id] = 'forget'
        await callback_query.answer('Хорошо')
        await callback_query.message.answer('Напишите ключ объекта, который хотите удалить')
        await callback_query.message.answer('Или напишите "Всё"')
        await send_typing_indicator(callback_query.message.chat.id, callback_query.bot, wait=3)
        await callback_query.message.answer('А если вы забыли ключ, нажмите на кнопку "Вспомнить"')


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
    elif keyboard_input.get(message.from_user.id) == 'remember':
        asyncio.create_task(send_typing_indicator(message.chat.id, bot, wait=3))
        if len(message.text.split()) == 2:
            save_data(message.from_user.id, message.text.split()[0], message.text.split()[1])
            await message.answer(f'Запомнил!\n'
                                 f'{message.text.split()[0]} — {message.text.split()[1]}')
        else:
            await message.answer('Пожалуйста, введите ровно два слова через пробел')
        del keyboard_input[message.from_user.id]
    elif keyboard_input.get(message.from_user.id) == 'forget':
        asyncio.create_task(send_typing_indicator(message.chat.id, bot, wait=2))
        del keyboard_input[message.from_user.id]
        if message.text.lower() == 'всё' or message.text.lower() == 'все':
            delete_data(message.from_user.id)
            await message.reply('Удалил вас из базы🥸')
            return
        if message.text.lower() not in get_data(message.from_user.id):
            await message.answer('Такого ключа нет')
            return
        delete_data(message.from_user.id, message.text)
        await message.answer(f'Удалил ключ {message.text} и его значение')

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
