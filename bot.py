import random
import os
import asyncio
import telegram
from aiogram import Bot, Dispatcher, F, Router, types
from aiogram.types import Message, ReplyKeyboardMarkup, KeyboardButton
from aiogram.filters import Command
from dotenv import load_dotenv

load_dotenv()
beta_keyboard = ReplyKeyboardMarkup(keyboard=[
    [KeyboardButton(text='Поставь напоминание'),
     KeyboardButton(text='Котики!')],
    [KeyboardButton(text='Как меня зовут?'),
     KeyboardButton(text='Домик')],
    [KeyboardButton(text='Отзыв')]
],
    resize_keyboard=True)

keyboard = ReplyKeyboardMarkup(keyboard=[
    [KeyboardButton(text='Кубик')],
    [KeyboardButton(text="Info", )]
], resize_keyboard=True)

api_token_muziatikbot = os.getenv("API_TOKEN_muziatikBot")
my_chat_id = os.getenv("MY_CHAT_ID")
mommy_chat_id = os.getenv("MOMMY_CHAT_ID")

router = Router()


@router.message(Command('start'))
async def start_bot(message: Message):
    await message.answer("Здравствуйте, я **MuziatikBot**. Нажмите на _кнопку_ внизу, чтобы узнать больше о мне.",
                         parse_mode="Markdown", reply_markup=ReplyKeyboardMarkup(keyboard=[[KeyboardButton(text='Info')]], resize_keyboard=True))


@router.message(lambda msg: msg.text == 'Info')
async def info(message: Message, bot: Bot):
    dice = await message.reply_sticker('CAACAgIAAxkBAAEz-itoBW_hmrk-'
                                       '933qZ43mWlN1MK_QjAACsQ8AAldGSEutS54Fv2EAAe42BA')
    await asyncio.sleep(3)
    await message.reply('Вот infoрмаация о MuziatikBot:\n'
                        'Версия — 1.3\nДоступность фнкций: Возможности Bot_v1 — недоступно,\n Кубик: Брось кубик — можно пробовать.',
                        reply_markup=keyboard)


@router.message(lambda msg: msg.text == 'Отзыв')
async def feedback(message: Message):
    await message.reply(
        '_Напишите_ Ваш отзыв (функция неработает)',
        parse_mode="Markdown",
        reply_markup=keyboard)


@router.message(lambda msg: "Кубик" in msg.text)
async def dice(message: Message, bot: Bot):
    inline_keyboard = types.InlineKeyboardMarkup(inline_keyboard=[
        [types.InlineKeyboardButton(
            text="Брось кубик (стикер)", callback_data="roll_dice")],
        [types.InlineKeyboardButton(
            text='Рандомное число (текст)', callback_data='text_dice')]
    ])
    await message.answer("Выберите вариант:", reply_markup=inline_keyboard)


@router.callback_query(lambda c: c.data == 'roll_dice')
async def roll_dice(callback_query: types.CallbackQuery, bot: Bot):
    await bot.send_dice(callback_query.from_user.id)


@router.callback_query(lambda c: c.data == "text_dice")
async def text_dice(callback_query: types.CallbackQuery, bot: Bot):
    dice_result = random.randint(1, 6)
    await bot.send_message(callback_query.from_user.id, f"Выпало: {dice_result}")


async def main():
    bot = Bot(api_token_muziatikbot)
    dp = Dispatcher()
    dp.include_router(router)
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
