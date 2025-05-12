import asyncio
import os
import random

from aiogram import Bot, Dispatcher, Router, types
from aiogram.filters import Command
from aiogram.types import Message, ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton
from dotenv import load_dotenv

load_dotenv()

settings_keyboard = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text='Выбрать имя', callback_data='name')]
])

dev_keyboard = ReplyKeyboardMarkup(keyboard=[
    [KeyboardButton(text='Roll a die')],
    [KeyboardButton(text='info')],
    [KeyboardButton(text='Settings')],
    [KeyboardButton(text='Reminder (no)'),
     KeyboardButton(text='Cats! (later)')],
    [KeyboardButton(text='What is my name? (changed)'),
     KeyboardButton(text='Домик (was good)')],
    [KeyboardButton(text='Feedback (need it)')]
],
    resize_keyboard=True)

keyboard = ReplyKeyboardMarkup(keyboard=[
    [KeyboardButton(text='Кубик')],
    [KeyboardButton(text="Info", )],
    [KeyboardButton(text='Настройки (beta)')],
], resize_keyboard=True)

api_token_muziatikbot = os.getenv("API_TOKEN_muziatikBot")
my_chat_id = os.getenv("MY_CHAT_ID")
mommy_chat_id = os.getenv("MOMMY_CHAT_ID")

router = Router()


@router.message(Command('start'))
async def start_bot(message: Message):
    await message.answer("Здравствуйте, я **MuziatikBot**. Нажмите на _кнопку_ внизу, чтобы узнать больше обо мне.",
                         parse_mode="Markdown",
                         reply_markup=ReplyKeyboardMarkup(keyboard=[[KeyboardButton(text='Info')]],
                                                          resize_keyboard=True))


@router.message(lambda msg: msg.text == 'Info')
async def info(message: Message, bot: Bot):
    await message.reply_sticker('CAACAgIAAxkBAAEz-itoBW_hmrk-'
                                '933qZ43mWlN1MK_QjAACsQ8AAldGSEutS54Fv2EAAe42BA')
    await asyncio.sleep(3)
    await message.reply('Вот infoрмаация о MuziatikBot:\n'
                        'Версия — 1.6\nДоступность фнкций: Выбрать имя — предпросмотр, Возможности Bot_v1 — начальная стадия,\n Кубик — публичный предпросмотр.',
                        reply_markup=keyboard)


@router.message(lambda msg: "Кубик" in msg.text)
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
    await bot.send_message(callback_query.from_user.id, f"Выпало: {dice_result}")


@router.message(lambda msg: msg.text == 'Настройки (beta)')
async def settings(message: Message):
    global set
    set = await message.reply('Вот _beta_ настройки', reply_markup=settings_keyboard,
                              parse_mode="Markdown")


@router.callback_query(lambda c: c.data == 'name')
async def name(callback_query: types.CallbackQuery, bot: Bot):
    await set.edit_text('Как вас называть?')
    await asyncio.sleep(1)
    await bot.edit_message_reply_markup(chat_id=set.chat.id,
                                        message_id=set.message_id, reply_markup=InlineKeyboardMarkup(
            inline_keyboard=[
                [InlineKeyboardButton(text='ФИ', callback_data='full_name'),
                 InlineKeyboardButton(text='имя пользователя', callback_data='username')],
            ]
        ))


@router.callback_query(lambda c: c.data == 'full_name')
async def full_name(callback_query: types.CallbackQuery, bot: Bot):
    name = callback_query.from_user.full_name
    await bot.send_message(callback_query.message.chat.id, f'Хорошо, {name}')


@router.callback_query(lambda c: c.data == 'username')
async def username(callback_query: types.CallbackQuery, bot: Bot):
    name = callback_query.from_user.username
    await bot.send_message(callback_query.message.chat.id, f'Хорошо, {name}')


@router.message(lambda msg: msg.text == 'dev')
async def dev(message: Message):
    await message.reply('Okei-dokei', reply_markup=dev_keyboard)


@router.message(lambda msg: msg.text == 'Отзыв')
async def feedback(message: Message):
    await message.reply(
        '_Напишите_ Ваш отзыв (функция неработает)',
        parse_mode="Markdown",
        reply_markup=keyboard)


async def main():
    bot = Bot(api_token_muziatikbot)
    dp = Dispatcher()
    dp.include_router(router)
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
