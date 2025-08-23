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

try:
    MY_CHAT_ID = int(os.getenv('MY_CHAT_ID'))
except TypeError as e:
    print(f'Ключа та нет... :\n{e}')

router = Router()
keyboard_input = {}


# ======== Helper ========

async def send_typing_indicator(chat_id, bot, wait=1):
    """
    Send a short "typing" indicator by posting "..." then deleting it after a delay.
    
    Parameters:
        chat_id (int|str): Target chat identifier where the indicator will be shown.
        wait (float): Seconds to wait before deleting the indicator (default: 1).
    
    Notes:
        - The function sends a message ("...") and deletes it after `wait` seconds to simulate typing.
        - Uses the provided Bot instance to perform messaging operations.
    """
    dots = await bot.send_message(chat_id, "...")
    await asyncio.sleep(wait)
    await bot.delete_message(chat_id, dots.message_id)


# ======== Handlers ========

@router.message(Command('start'))
async def start_bot(message: Message):
    """
    Send the startup greeting and prompt the user to interact with the bot.
    
    Checks persistent storage for a saved name and greets the user accordingly, then sends a prompt with an "info" reply button. Side effects: sends multiple messages to the chat and reads the stored "name" via get_data.
    """
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
    """
    Send the bot's information as a sticker followed by a short informational message and the main reply keyboard.
    
    Sends a sticker, pauses briefly, then replies with the bot version, feature availability notes, and a notice about the new feedback feature. The reply includes the global `keyboard` reply_markup.
    """
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
    """
    Show a prompt asking the user how they prefer to be addressed and replace the settings message with an inline keyboard to choose a name source.
    
    Edits the stored settings message text to "Как вас называть?" then, after a short pause, updates its inline keyboard with three options:
    - "ФИ" (use the user's full name),
    - "имя пользователя" (use the Telegram username),
    - "Ввести вручную" (enter a name manually).
    """
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
    """
    Handle a name-selection callback: save a chosen name or enter manual name-input mode and notify the user.
    
    This function processes a CallbackQuery whose data indicates the user's choice:
    - 'full_name' — saves the user's full name (from `callback_query.from_user.full_name`) to persistent storage.
    - 'username' — saves the user's Telegram username (from `callback_query.from_user.username`) to persistent storage.
    - any other value (manual entry path) — sets the per-user input state so the next text message will be recorded as the user's name.
    
    Side effects:
    - Persists the selected name using save_data(user_id, "name", name).
    - Updates the global keyboard_input state for manual entry.
    - Sends a short typing indicator and a confirmation message to the user.
    
    Parameters:
        callback_query (types.CallbackQuery): callback query containing the user's selection and user metadata.
    """
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
    """
    Check whether the sender is a developer and reply with the developer keyboard when authorized.
    
    If the sender's user ID matches the configured MY_CHAT_ID or the DADDY_CHAT_ID environment variable, replies with "Okei-dokei" and the developer reply keyboard; otherwise replies "Вы не разработчик". Sends short typing indicators and an intermediate "Проверяю" message as part of the interaction.
    
    Parameters:
        message (aiogram.types.Message): Incoming Telegram message whose sender is checked for developer access.
    """
    await send_typing_indicator(message.chat.id, message.bot, wait=2)
    await message.reply('Проверяю')
    await send_typing_indicator(message.chat.id, message.bot, wait=3)
    if message.from_user.id == MY_CHAT_ID or message.from_user.id == os.getenv('DADDY_CHAT_ID'):
        await message.reply('Okei-dokei', reply_markup=dev_keyboard)
    else:
        await message.reply('Вы не разработчик')


@router.message(lambda msg: msg.text == 'Отзыв' or msg.text == 'Feedback')
async def feedback(message: Message):
    """
    Mark the user as entering feedback mode and prompt them to submit their feedback.
    
    Sets keyboard_input[<user_id>] = 'feedback' so the next message from this user is handled as feedback, sends a short typing indicator, and replies with a prompt asking the user to write their feedback.
    
    Parameters:
        message (aiogram.types.Message): Incoming message object; used to identify the user and reply in the same chat.
    """
    global keyboard_input
    keyboard_input[message.from_user.id] = 'feedback'
    await send_typing_indicator(message.chat.id, message.bot)
    await message.reply('_Напишите_ Ваш отзыв (бета версия)', parse_mode="Markdown")


@router.message()
async def everything(message: Message, bot: Bot):
    """
    Handle free-form incoming messages according to the user's current input state.
    
    If the user is in 'name' mode, saves the message text as the user's name and clears the state.
    If the user is in 'feedback' mode, forwards the message text to MY_CHAT_ID, notifies the user, and clears the state.
    If the user has no active input mode, sends a short help hint directing them to use the on-screen buttons.
    
    Parameters:
        message (aiogram.types.Message): Incoming message from the user (used for content and sender id).
    
    Side effects:
        - Persists a name via save_data(user_id, "name", ...).
        - Sends messages to the user.
        - Forwards feedback messages to the configured MY_CHAT_ID.
        - Mutates the global keyboard_input state by removing the entry for the user after handling.
    """
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
