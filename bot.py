import asyncio
import os
from aiogram import Bot, Dispatcher, Router, types, F
from aiogram.filters import Command
from aiogram.types import Message
from dotenv import load_dotenv

import beta_bot

load_dotenv()

# ======== Config ========

api_token_muziatikbot = os.getenv("API_TOKEN_muziatikBot")

try:
    MY_CHAT_ID = int(os.getenv('MY_CHAT_ID'))
except TypeError as e:
    print(f'Ключа та нет... :\n{e}')

router = Router()

# ======== Handlers ========

@router.message(Command('start'))
async def start_bot(message: Message):
    await beta_bot.start_bot(message)


@router.message(lambda msg: msg.text == 'info')
async def info(message: Message, bot: Bot):
    await beta_bot.info(message, bot)


@router.callback_query(F.data == 'status')
async def status(callback_query: types.CallbackQuery):
    await beta_bot.status(callback_query)


@router.callback_query(F.data == 'changelog')
async def changelog(callback_query: types.CallbackQuery):
    await beta_bot.changelog(callback_query)

@router.message(lambda msg: msg.text == "Кубик" or msg.text == 'Roll a die')
async def roll_dice(message: Message, bot: Bot):
    await beta_bot.roll_dice(message, bot)

@router.message(lambda msg: msg.text == 'Memory' or msg.text == 'Память')
async def memory_menu(message: Message):
    await beta_bot.memory_menu(message)


@router.message(lambda msg: msg.text in ['Меню', 'Menu'])
async def menu(message: Message):
    await beta_bot.menu(message)


@router.callback_query(lambda c: c.data == 'name')
async def choose_name(callback_query: types.CallbackQuery, bot: Bot):
    await beta_bot.choose_name(callback_query, bot)


@router.callback_query(lambda c: c.data in ['full_name', 'username', 'keyboard_input'])
async def set_name(callback_query: types.CallbackQuery, bot: Bot):
    await beta_bot.set_name(callback_query, bot)


@router.callback_query(lambda c: c.data == 'remember' or c.data == 'recall' or c.data == 'forget')
async def memory(callback_query: types.CallbackQuery):
    await beta_bot.memory(callback_query)


@router.message(lambda msg: msg.text == 'dev')
async def dev(message: Message):
    await beta_bot.dev(message)


@router.callback_query(F.data == 'donate')
async def donate(callback_query: types.CallbackQuery):
    await beta_bot.donate(callback_query)


@router.message(lambda msg: msg.text == 'Отзыв' or msg.text == 'Feedback')
async def feedback(message: Message):
    await beta_bot.feedback(message)


@router.message(F.voice)
async def voice_to_text(message: types.Message, bot: Bot):
    """
    Обрабатывает голосовые сообщения, расшифровывает их и отправляет текст обратно.
    Добавлен недельный лимит: 10 бесплатных расшифровок на пользователя.
    При превышении отправляется счёт на 5 Stars.
    """
    await beta_bot.voice_to_text(message, bot)

@router.inline_query()
async def inline_emojis(inline_query: types.InlineQuery):
    # Создаём список всех интерактивных эмодзи
    await beta_bot.inline_emojis(inline_query)


# ======== Main ========

async def main():
    bot = Bot(api_token_muziatikbot)
    dp = Dispatcher()
    dp.include_router(router)
    await dp.start_polling(bot)


# ======== Payments Handlers ========

@router.pre_checkout_query()
async def pre_checkout_handler(pre_checkout_query: types.PreCheckoutQuery, bot: Bot):
    await beta_bot.pre_checkout_handler(pre_checkout_query, bot)


@router.message(F.successful_payment)
async def successful_payment_handler(message: types.Message, bot: Bot):
    await beta_bot.successful_payment_handler(message, bot)

@router.message()
async def everything(message: Message, bot: Bot):
    await beta_bot.everything(message, bot)


if __name__ == "__main__":
    asyncio.run(main())
