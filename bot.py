import asyncio
import os
import random
import time

from memory import get_data, save_data, delete_data
from aiogram import Bot, Dispatcher, Router, types, F
from aiogram.filters import Command
from aiogram.types import Message, ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton, \
    InlineQueryResultArticle, InputTextMessageContent, LabeledPrice
from dotenv import load_dotenv
from pydub import AudioSegment
import speech_recognition as sr


def _transcribe_wav(path: str, language: str = 'ru-RU') -> str:
    r = sr.Recognizer()
    with sr.AudioFile(path) as source:
        audio_data = r.record(source)
    return r.recognize_google(audio_data, language=language)


load_dotenv()

# ======== Keyboards ========

settings_keyboard = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text='Выбрать имя', callback_data='name')],
    [InlineKeyboardButton(text='Донат', callback_data='donate')]
])
memory_keyboard = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text='Запомнить', callback_data='remember')],
    [InlineKeyboardButton(text='Вспомнить', callback_data='recall')],
    [InlineKeyboardButton(text='Забыть', callback_data='forget')]
])
dev_keyboard = ReplyKeyboardMarkup(keyboard=[
    [KeyboardButton(text='Roll a die')],
    [KeyboardButton(text='info')],
    [KeyboardButton(text='Settings')],
    [KeyboardButton(text='Memory')],
    [KeyboardButton(text='Feedback')],
    [KeyboardButton(text='Reminder (no)'), KeyboardButton(text='Cats! (later)')],
    [KeyboardButton(text='What is my name? (changed)'), KeyboardButton(text='Домик (was good)')]
], resize_keyboard=True)

keyboard = ReplyKeyboardMarkup(keyboard=[
    [KeyboardButton(text='Кубик')],
    [KeyboardButton(text='info'), KeyboardButton(text='Отзыв')],
    [KeyboardButton(text='Память')],
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
    # Prefetch the user's name off the event loop, with a fallback
    name = await asyncio.to_thread(get_data, message.from_user.id, "name") or "гость"
    await message.reply(
        f"Вот информация о MuziatikBot, {name}:\n"
        "Версия — 2.6.4\n"
        "Описание: Начиная с версии 2.0, бот стал полезным в повседневной жизни.\n"
        "Вот мои функции:\n"
        "Выбрать имя — Полная функциональность.\n"
        "Кубик — полная функциональность.\n"
        "Отзыв🆕: Теперь вы можете оставить отзыв про бота!\n"
        "*Память*🧠: *Полная функциональность*.\n"
        "*Расшифровка голосовых сообщений в текст*:\n"
        "Просто отправьте или перешлите голосовое сообщение и я его расшифрую\n"
        "Бесплатно 10 голосовых сообщений в неделю, "
        "далее 5 звёзд за сообщение\n"
        "Настройки > Донат: *Не даёт привилегия*: заплатите 10 звёзд чтобы поддержать разработчика\n\n"
        "Напишите @muziatikBot в любом другом чате чтобы отправить интерактивный эмодзи",
        parse_mode='Markdown', reply_markup=keyboard
    )


@router.message(lambda msg: msg.text == "Кубик" or msg.text == 'Roll a die')
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


@router.message(lambda msg: msg.text == 'Memory' or msg.text == 'Память')
async def memory_menu(message: Message):
    await message.reply('Выберите действие с памятью', reply_markup=memory_keyboard)


@router.message(lambda msg: msg.text in ['Настройки', 'Settings'])
async def settings(message: Message):
    await message.reply('Вот настройки', reply_markup=settings_keyboard,
                        parse_mode="Markdown")


@router.callback_query(lambda c: c.data == 'name')
async def choose_name(callback_query: types.CallbackQuery, bot: Bot):
    await callback_query.message.edit_text('Как вас называть?')
    await callback_query.answer()
    await asyncio.sleep(1)
    await bot.edit_message_reply_markup(
        chat_id=callback_query.from_user.id,
        message_id=callback_query.message.message_id,
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


@router.callback_query(F.data == 'donate')
async def donate(callback_query: types.CallbackQuery):
    await callback_query.answer('Отправил кнопку доната')
    await callback_query.message.edit_text('Выбрано: Донат на 10 звезд')
    await callback_query.message.reply_invoice('Донат', '10 звёзд за раз', 'donate',
                                               'XTR', [LabeledPrice(label='Донат', amount=10)])


@router.message(lambda msg: msg.text == 'Отзыв' or msg.text == 'Feedback')
async def feedback(message: Message):
    global keyboard_input
    keyboard_input[message.from_user.id] = 'feedback'
    await send_typing_indicator(message.chat.id, message.bot)
    await message.reply('_Напишите_ Ваш отзыв', parse_mode="Markdown")


@router.message(F.voice)
async def voice_to_text(message: types.Message, bot: Bot):
    """
    Обрабатывает голосовые сообщения, расшифровывает их и отправляет текст обратно.
    Добавлен недельный лимит: 10 бесплатных расшифровок на пользователя.
    При превышении отправляется счёт на 5 Stars.
    """
    download = None
    transcribe = None
    ogg_path = None
    wav_path = None
    try:
        # Проверяем и обновляем недельный лимит
        user_id = message.from_user.id
        now = int(time.time())
        week_seconds = 7 * 24 * 60 * 60

        # Инициализация недели, если не задана
        start_ts = get_data(user_id, "voice_week_start_ts")
        if not isinstance(start_ts, int):
            start_ts = now
            save_data(user_id, "voice_week_start_ts", start_ts)

        # Сброс счётчика, если прошла неделя
        if now - start_ts >= week_seconds:
            save_data(user_id, "voice_counter", 0)
            start_ts = now
            save_data(user_id, "voice_week_start_ts", start_ts)

        counter = get_data(user_id, "voice_counter")
        if not isinstance(counter, int):
            counter = 0
            save_data(user_id, "voice_counter", counter)

        # Если лимит исчерпан — отправляем счёт и выходим
        if counter >= 10:
            await message.reply_invoice(
                title="Лимит расшифровок",
                description="Вы использовали 10 бесплатных расшифровок на этой неделе. Купите доступ за 5 Звёзд.",
                payload=f"voice_limit_5_stars:{message.voice.file_id}",
                currency="XTR",
                prices=[LabeledPrice(label="Voice transcription", amount=5 if message.from_user.id != MY_CHAT_ID else 1)]
            )
            return

        # Скачиваем голосовое сообщение
        voice_file = await bot.get_file(message.voice.file_id)
        ogg_path = f"voice_{voice_file.file_id}.ogg"
        download = await message.reply('Скачиваю сообщение')
        await bot.download_file(voice_file.file_path, ogg_path)
        # Конвертируем из OGG в WAV, так как SpeechRecognition лучше работает с WAV
        wav_path = ogg_path.replace('.ogg', '.wav')
        segment = await asyncio.to_thread(AudioSegment.from_file, ogg_path)
        await asyncio.to_thread(segment.export, wav_path, format="wav")
        asyncio.create_task(send_typing_indicator(message.chat.id, bot, wait=5))
        transcribe = await message.answer('Расшифровываю...')
        # Расшифровываем аудио
        text = await asyncio.to_thread(_transcribe_wav, wav_path)
        # Отправляем расшифрованный текст
        await message.reply(f"Расшифрованный текст: {text}")
        # Увеличиваем счётчик после успешной расшифровки
        save_data(user_id, "voice_counter", counter + 1)

    except sr.UnknownValueError:
        await message.reply("Не удалось распознать речь.")
    except Exception as e:
        await message.reply(f"Произошла ошибка: {e}")
    finally:
        try:
            if download:
                await download.delete()
        except Exception:
            pass
        try:
            if transcribe:
                await transcribe.delete()
        except Exception:
            pass
        # Удаляем временные файлы
        if ogg_path and os.path.exists(ogg_path):
            os.remove(ogg_path)
        if wav_path and os.path.exists(wav_path):
            os.remove(wav_path)


@router.inline_query()
async def inline_emojis(inline_query: types.InlineQuery):
    # Создаём список всех интерактивных эмодзи
    results = [
        InlineQueryResultArticle(
            id='1',
            title='🎲 Кубик',
            input_message_content=InputTextMessageContent(message_text='🎲')
        ),
        InlineQueryResultArticle(
            id='2',
            title='🎯 Дартс',
            input_message_content=InputTextMessageContent(message_text='🎯')
        ),
        InlineQueryResultArticle(
            id='3',
            title='🏀 Баскетбол',
            input_message_content=InputTextMessageContent(message_text='🏀')
        ),
        InlineQueryResultArticle(
            id='4',
            title='🎳 Боулинг',
            input_message_content=InputTextMessageContent(message_text='🎳')
        ),
        InlineQueryResultArticle(
            id='5',
            title='⚽ Футбол',
            input_message_content=InputTextMessageContent(message_text='⚽')
        ),
        InlineQueryResultArticle(
            id='6',
            title='🎰 Слоты',
            input_message_content=InputTextMessageContent(message_text='🎰')
        )
    ]
    # Отправляем результаты пользователю
    await inline_query.answer(results)


# ======== Main ========

async def main():
    bot = Bot(api_token_muziatikbot)
    dp = Dispatcher()
    dp.include_router(router)
    await dp.start_polling(bot)


# ======== Payments Handlers ========

@router.pre_checkout_query()
async def pre_checkout_handler(pre_checkout_query: types.PreCheckoutQuery, bot: Bot):
    try:
        await bot.answer_pre_checkout_query(pre_checkout_query.id, ok=True)
    except Exception:
        try:
            await bot.answer_pre_checkout_query(
                pre_checkout_query.id,
                ok=False,
                error_message="Не удалось обработать оплату. Попробуйте позже.")
        except Exception:
            pass


@router.message(F.successful_payment)
async def successful_payment_handler(message: types.Message, bot: Bot):
    payload = (message.successful_payment.invoice_payload or "")

    async def refund_and_notify(reason: str):
        # Try to refund Stars and notify the user
        charge_id = None
        try:
            charge_id = message.successful_payment.telegram_payment_charge_id
        except Exception:
            pass
        if charge_id:
            try:
                await bot.refund_star_payment(
                    user_id=message.from_user.id,
                    telegram_payment_charge_id=charge_id
                )
                await message.answer(f"{reason}\nСредства возвращены.")
            except Exception as e:
                await message.answer(
                    f"{reason}\nНе удалось автоматически вернуть средства. Свяжитесь с поддержкой. Ошибка: {e}")
        else:
            await message.answer(
                f"{reason}\nНе найден идентификатор платежа для возврата. Свяжитесь с поддержкой.")

    if not payload.startswith("voice_limit_5_stars:"):
        if payload == "donate":
            await message.reply(
                'Спасибо! Если хотите отправить больше 10 звёзд, повторите процедуру оплаты несколько раз.')
        return
    voice_file_id = payload.split(":", 1)[1].strip() if ":" in payload else ""
    if not voice_file_id:
        await refund_and_notify("Не удалось определить, какое сообщение расшифровать после оплаты.")
        return

    download = None
    transcribe_msg = None
    ogg_path = None
    wav_path = None
    try:
        # Скачиваем голосовое сообщение по file_id из payload
        voice_file = await bot.get_file(voice_file_id)
        ogg_path = f"voice_{voice_file.file_id}.ogg"
        download = await message.reply('Скачиваю оплаченный голос')
        await bot.download_file(voice_file.file_path, ogg_path)

        # Конвертируем OGG в WAV
        wav_path = ogg_path.replace('.ogg', '.wav')
        segment = await asyncio.to_thread(AudioSegment.from_file, ogg_path)
        await asyncio.to_thread(segment.export, wav_path, format="wav")

        asyncio.create_task(send_typing_indicator(message.chat.id, bot, wait=5))
        transcribe_msg = await message.answer('Расшифровываю (оплачено)...')

        # Расшифровываем
        text = await asyncio.to_thread(_transcribe_wav, wav_path)
        await message.reply(f"Расшифрованный текст (оплачено): {text}")

        # Платная расшифровка — счётчик не изменяем
    except sr.UnknownValueError:
        await refund_and_notify("Не удалось распознать речь по оплаченному сообщению.")
    except Exception as e:
        await refund_and_notify(f"Произошла ошибка при обработке оплаченного сообщения: {e}")
    finally:
        try:
            if download:
                await download.delete()
        except Exception:
            pass
        try:
            if transcribe_msg:
                await transcribe_msg.delete()
        except Exception:
            pass
        if ogg_path and os.path.exists(ogg_path):
            os.remove(ogg_path)
        if wav_path and os.path.exists(wav_path):
            os.remove(wav_path)


@router.message()
async def everything(message: Message, bot: Bot):
    if keyboard_input.get(message.from_user.id) == 'name':
        save_data(message.from_user.id, "name", message.text)
        del keyboard_input[message.from_user.id]
        await message.answer(f'Запомнил! Теперь вы — {message.text}')
    elif keyboard_input.get(message.from_user.id) == 'feedback':
        await message.answer('Пишу моему создателю')
        await send_typing_indicator(message.from_user.id, bot)
        await bot.send_message(MY_CHAT_ID, f'Хозяин, у тебя отзыв.\n{message.text}')
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


if __name__ == "__main__":
    asyncio.run(main())
