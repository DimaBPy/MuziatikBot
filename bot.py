import asyncio
import os

from aiogram import Bot, Dispatcher, Router, types, F
from aiogram.client.session.aiohttp import AiohttpSession
from aiogram.filters import Command
from aiogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
from aiohttp import ClientSession, TCPConnector
from aiohttp.resolver import AsyncResolver
from dotenv import load_dotenv
import ssl

import beta_bot
import stable_bot
from db import recall, remember


def _select_module(user_id: int):
    try:
        return beta_bot if recall(user_id, field='beta') == 'True' else stable_bot
    except Exception:
        # Fallback to stable on any recall issues
        return stable_bot


def _dispatch(func_name: str, user_id: int):
    mod = _select_module(user_id)
    # If function not present in selected module, fallback to beta version if available
    if hasattr(mod, func_name):
        return getattr(mod, func_name)
    # Prefer beta implementation as a universal fallback for missing handlers
    if hasattr(beta_bot, func_name):
        return getattr(beta_bot, func_name)
    # As a last resort, try stable
    return getattr(stable_bot, func_name)


load_dotenv()

# ======== Config ========

api_token_muziatikbot = os.getenv("API_TOKEN_muziatikBot")
if not api_token_muziatikbot:
    raise RuntimeError("Missing env var API_TOKEN_muziatikBot")

try:
    MY_CHAT_ID = int(os.getenv('MY_CHAT_ID'))
except (TypeError, ValueError) as e:
    print(f'Ключа та нет... :\n{e}')

router = Router()


# ======== Handlers ========

@router.message(Command('start'))
async def start_bot(message: Message):
    await _dispatch('start_bot', message.from_user.id)(message)


@router.message(lambda msg: msg.text == 'info')
async def info(message: Message):
    await _dispatch('info', message.from_user.id)(message)


@router.callback_query(F.data == 'status')
async def status(callback_query: types.CallbackQuery):
    await _dispatch('status', callback_query.from_user.id)(callback_query)


@router.callback_query(F.data == 'changelog')
async def changelog(callback_query: types.CallbackQuery):
    await _dispatch('changelog', callback_query.from_user.id)(callback_query)


@router.message(lambda msg: msg.text in ["Кубик", 'Roll a die'])
async def roll_dice(message: Message, bot: Bot):
    await _dispatch('roll_dice', message.from_user.id)(message, bot)


@router.message(lambda msg: msg.text in ['Memory', 'Память'])
async def memory_menu(message: Message):
    await _dispatch('memory_menu', message.from_user.id)(message)


@router.message(lambda msg: msg.text in ['Меню', 'Menu'])
async def menu(message: Message):
    await _dispatch('menu', message.from_user.id)(message)


@router.callback_query(F.data == 'name')
async def choose_name(callback_query: types.CallbackQuery, bot: Bot):
    await _dispatch('choose_name', callback_query.from_user.id)(callback_query, bot)


@router.callback_query(F.data.in_(['full_name', 'username', 'keyboard_input', 'no-name']))
async def set_name(callback_query: types.CallbackQuery, bot: Bot):
    await _dispatch('set_name', callback_query.from_user.id)(callback_query, bot)


@router.callback_query(F.data.in_(['remember', 'recall', 'forget']))
async def memory(callback_query: types.CallbackQuery):
    await _dispatch('memory', callback_query.from_user.id)(callback_query)


@router.message(F.text == 'dev')
async def dev(message: Message):
    await _dispatch('dev', message.from_user.id)(message)


@router.callback_query(F.data == 'donate')
async def donate(callback_query: types.CallbackQuery):
    await _dispatch('donate', callback_query.from_user.id)(callback_query)


@router.message(lambda msg: msg.text in ['Вопрос/Отзыв', 'Feedback'])
async def feedback(message: Message):
    await _dispatch('feedback', message.from_user.id)(message)


@router.message(F.voice)
async def voice_to_text(message: Message, bot: Bot):
    """
    Обрабатывает голосовые сообщения, расшифровывает их и отправляет текст обратно.
    Добавлен недельный лимит: 10 бесплатных расшифровок на пользователя.
    При превышении отправляется счёт на 5 Stars.
    """
    await _dispatch('voice_to_text', message.from_user.id)(message, bot)


@router.inline_query()
async def inline_emojis(inline_query: types.InlineQuery):
    await _dispatch('inline_emojis', inline_query.from_user.id)(inline_query)


@router.callback_query(F.data == 'chanel')
async def chanel(callback_query: types.CallbackQuery):
    await callback_query.message.edit_text(
        'Выберете версию:',
        reply_markup=InlineKeyboardMarkup(
            inline_keyboard=[
                [InlineKeyboardButton(text='beta', callback_data='beta')],
                [InlineKeyboardButton(text='стабильная', callback_data='stable')]
            ]
        )
    )


@router.callback_query(F.data == 'beta')
async def beta(callback_query: types.CallbackQuery):
    remember(callback_query.from_user.id, 'True', 'beta')
    await callback_query.message.edit_text(text='Готово, теперь вы будете использовать beta-версию')


@router.callback_query(F.data == 'stable')
async def stable(callback_query: types.CallbackQuery):
    remember(callback_query.from_user.id, 'False', 'beta')
    await callback_query.message.edit_text(text='Готово, теперь вы будете использовать стабильную версию')


@router.pre_checkout_query()
async def pre_checkout_handler(pre_checkout_query: types.PreCheckoutQuery, bot: Bot):
    await _dispatch('pre_checkout_handler', pre_checkout_query.from_user.id)(pre_checkout_query, bot)


@router.message(F.successful_payment)
async def successful_payment_handler(message: types.Message, bot: Bot):
    await _dispatch('successful_payment_handler', message.from_user.id)(message, bot)


@router.message()
async def everything(message: Message, bot: Bot):
    await _dispatch('everything', message.from_user.id)(message, bot)


async def main():
    loop = asyncio.get_event_loop()
    resolver = AsyncResolver(loop=loop)

    # Create a 'do-nothing' SSL context
    ssl_context = ssl.create_default_context()
    ssl_context.check_hostname = False
    ssl_context.verify_mode = ssl.CERT_NONE

    # Pass the context directly to the connector
    connector = TCPConnector(resolver=resolver, ssl=ssl_context)

    async with ClientSession(connector=connector) as aio_session:
        session_wrapper = AiohttpSession()
        session_wrapper._session = aio_session
        session_wrapper._should_reset_connector = False

        bot = Bot(token=api_token_muziatikbot, session=session_wrapper)
        dp = Dispatcher()
        dp.include_router(router)

        print("Bot is live")

        try:
            await dp.start_polling(bot)
        finally:
            await bot.session.close()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("Stopping the bot...")
