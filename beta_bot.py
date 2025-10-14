import asyncio
import os
import speech_recognition as sr
import time
from aiogram import Bot
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton, \
    InlineQueryResultArticle, LabeledPrice, CallbackQuery, InlineQuery, PreCheckoutQuery, InputTextMessageContent
from dotenv import load_dotenv
from pydub import AudioSegment

from db import remember, recall, forget


def _transcribe_wav(path: str, language: str = 'ru-RU') -> str:
    r = sr.Recognizer()
    with sr.AudioFile(path) as source:
        audio_data = r.record(source)
    return r.recognize_google(audio_data, language=language)


load_dotenv()

# ======== Keyboards ========

menu_keyboard = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text='Выбрать имя', callback_data='name')],
    [InlineKeyboardButton(text='Донат', callback_data='donate')],
    [InlineKeyboardButton(text='Версия', callback_data='chanel')]
])
memory_keyboard = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text='Запомнить', callback_data='remember')],
    [InlineKeyboardButton(text='Вспомнить', callback_data='recall')],
    [InlineKeyboardButton(text='Забыть', callback_data='forget')]
])
dev_keyboard = ReplyKeyboardMarkup(keyboard=[
    [KeyboardButton(text='Roll a die')],
    [KeyboardButton(text='info')],
    [KeyboardButton(text='Menu')],
    [KeyboardButton(text='Memory')],
    [KeyboardButton(text='Feedback')],
    [KeyboardButton(text='Reminder (no)'), KeyboardButton(text='Cats! (later)')],
    [KeyboardButton(text='What is my name? (changed)'), KeyboardButton(text='Домик (was good)')]
], resize_keyboard=True)

keyboard = ReplyKeyboardMarkup(keyboard=[
    [KeyboardButton(text='Кубик')],
    [KeyboardButton(text='info'), KeyboardButton(text='Отзыв')],
    [KeyboardButton(text='Память')],
    [KeyboardButton(text='Меню')],
], resize_keyboard=True)

# ======== Config ========

api_token_muziatikbot = os.getenv("API_TOKEN_muziatikBot")

try:
    MY_CHAT_ID = int(os.getenv('MY_CHAT_ID'))
except TypeError as e:
    print(f'Ключа та нет... :\n{e}')

keyboard_input = {}


# ======== Helper ========

async def send_typing_indicator(chat_id, bot, wait=1, action='typing'):
    dots = await bot.send_message(chat_id, "...")
    await bot.send_chat_action(chat_id, action)
    await asyncio.sleep(wait)
    await bot.delete_message(chat_id, dots.message_id)


async def start_bot(message):
    await send_typing_indicator(message.chat.id, message.bot)
    await message.answer("Здравствуйте, я **MuziatikBot**.", parse_mode="Markdown")
    await asyncio.sleep(1)
    if name := await asyncio.to_thread(recall, message.from_user.id, "user_name"):
        name = name if name != "Нет элементов в памяти😔" else "гость"
    if not name:
        await message.answer('Давайте познакомимся!')
    else:
        await message.answer(f'О! Я вас помню! Вы {name}')
    await message.answer(
        "Нажмите на _кнопку_ внизу, чтобы узнать больше обо мне.",
        parse_mode="Markdown",
        reply_markup=ReplyKeyboardMarkup(keyboard=[[KeyboardButton(text='info')]], resize_keyboard=True)
    )


async def info(message, bot):
    await message.reply_sticker('CAACAgIAAxkBAAEz-itoBW_hmrk-'
                                '933qZ43mWlN1MK_QjAACsQ8AAldGSEutS54Fv2EAAe42BA', reply_markup=keyboard)
    await asyncio.sleep(3)
    # Prefetch the user's name off the event loop, with a fallback
    if name := await asyncio.to_thread(recall, message.from_user.id, "name"):
        name = name if name != "Нет элементов в памяти😔" else "гость"
    await message.reply(
        f"Вот информация о MuziatikBot, {name}:\n"
        "Версия — 3\\.0 beta\n"
        "Вы можете узнать про доступность функций по кнопке под сообщением\n"
        "Описание: Начиная с версии 2\\.0, бот стал полезным в повседневной жизни\\.\n"
        "Вот мои функции:\n"
        "*Расшифровка голосовых сообщений в текст*:\n"
        "Просто отправьте или перешлите голосовое сообщение и я его расшифрую\n"
        "Бесплатно 10 голосовых сообщений в неделю, "
        "далее 5 звёзд за сообщение\n"
        "Меню \\> Донат: *Не даёт привилегий*: заплатите 10 звёзд, чтобы поддержать разработчика\n\n"
        "Напишите @muziatikBot в любом другом чате чтобы отправить интерактивный эмодзи",
        parse_mode='MarkdownV2', reply_markup=InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text='функции', callback_data='status')],
            [InlineKeyboardButton(text='что нового', callback_data='changelog')]
        ]))


async def status(callback_query):
    await callback_query.message.edit_text(
        "Выбрать имя — ✅\n"
        "Кубик (Обновлено) — ✅\n"
        "Отзыв — ✅\n"
        "*Память*🧠 — Работает✅\n"
        "*Расшифровка голосовых сообщений в текст* — 🔄️Возможны проблемы из-за в памяти\n",
        parse_mode='Markdown')


async def changelog(callback_query):
    await callback_query.message.edit_text(
        "В Версии 2.1: Добавлена расшифровка голосовых сообщений.\n"
        "2.2: Кубик и тд. в чатах с другими людьми\n"
        "2.3: Расшифровка стала платной😈\n"
        "...Скоро тут будет продолжение..."
    )


async def roll_dice(message, bot):
    dice_sticker = await bot.send_dice(message.from_user.id)
    await asyncio.create_task(send_typing_indicator(message.chat.id, bot,
                                                    wait=3, action='choose_sticker'))
    await message.answer(f'Выпало {dice_sticker.dice.value}')


async def memory_menu(message):
    await message.reply('Выберите действие с памятью', reply_markup=memory_keyboard)


async def menu(message):
    await message.reply('Вот меню', reply_markup=menu_keyboard,
                        parse_mode="Markdown")


async def choose_name(callback_query, bot):
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


async def set_name(callback_query, bot):
    if callback_query.data == 'full_name':
        name = callback_query.from_user.full_name
        remember(callback_query.from_user.id, name, field='name')
        await callback_query.answer(f'Хорошо, {name}')
    elif callback_query.data == 'username':
        name = callback_query.from_user.username
        remember(callback_query.from_user.id, name, field='name')
        await callback_query.answer(f'Хорошо, {name}')
    else:
        await send_typing_indicator(callback_query.message.chat.id, bot)
        keyboard_input[callback_query.from_user.id] = 'name'
        await callback_query.answer('Хорошо, пишите', show_alert=True)


async def memory(callback_query):
    if callback_query.data == 'remember':
        await callback_query.answer('Пишите. Правила: 🆕как хотите',
                                    show_alert=True)
        keyboard_input[callback_query.from_user.id] = 'remember'

    elif callback_query.data == 'recall':
        await callback_query.answer('Вспоминаю...')
        asyncio.create_task(send_typing_indicator(callback_query.message.chat.id, callback_query.bot))
        await callback_query.message.answer('\n'.join(recall(callback_query.from_user.id)))

    else:
        keyboard_input[callback_query.from_user.id] = 'forget'
        await callback_query.answer('Хорошо')
        await callback_query.message.answer('Напишите номер объекта, который хотите удалить')
        await callback_query.message.answer('Или напишите "Все"')
        await send_typing_indicator(callback_query.message.chat.id, callback_query.bot, wait=5)
        await callback_query.message.answer('\n'.join(recall(callback_query.from_user.id)))


async def dev(message):
    await send_typing_indicator(message.chat.id, message.bot, wait=2)
    await message.reply('Проверяю')
    await send_typing_indicator(message.chat.id, message.bot, wait=3)
    if message.from_user.id == MY_CHAT_ID or message.from_user.id == os.getenv('DADDY_CHAT_ID'):
        await message.reply('Okei-dokei', reply_markup=dev_keyboard)
    else:
        await message.reply('Вы не разработчик')


async def donate(callback_query):
    await callback_query.answer('Отправил кнопку доната')
    await callback_query.message.edit_text('Выбрано: Донат на 10 звезд')
    await callback_query.message.reply_invoice(
        title='Донат',
        description='10 звёзд за раз',
        payload='donate',
        currency='XTR',
        prices=[LabeledPrice(label='Донат', amount=10)]
    )


async def feedback(message):
    global keyboard_input
    keyboard_input[message.from_user.id] = 'feedback'
    await send_typing_indicator(message.chat.id, message.bot)
    await message.reply('_Напишите_ Ваш отзыв', parse_mode="Markdown")


async def voice_to_text(message, bot):
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
        start_ts = recall(user_id, "voice_time")
        if not isinstance(start_ts, int):
            start_ts = now
            remember(user_id, start_ts, "voice_time")

        # Сброс счётчика, если прошла неделя
        if now - start_ts >= week_seconds:
            remember(user_id, 0, "voice_counter")
            start_ts = now
            remember(user_id, start_ts, "voice_time")

        counter = recall(user_id, "voice_counter")
        if not isinstance(counter, int):
            counter = 0
            remember(user_id, counter, "voice_counter")

        # Если лимит исчерпан — отправляем счёт и выходим
        if counter >= 10:
            await message.reply_invoice(
                title="Лимит расшифровок",
                description="Вы использовали 10 бесплатных расшифровок на этой неделе. Купите доступ за 5 Звёзд.",
                payload=f"voice_limit_5_stars:{message.voice.file_id}",
                currency="XTR",
                prices=[
                    LabeledPrice(label="Voice transcription", amount=5 if message.from_user.id != MY_CHAT_ID else 1)]
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
        remember(user_id, counter + 1, 'voice_counter')

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


async def inline_emojis(inline_query):
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


# ======== Payments Handlers ========

async def pre_checkout_handler(pre_checkout_query, bot):
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


async def successful_payment_handler(message, bot):
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


async def everything(message, bot):
    if keyboard_input.get(message.from_user.id) == 'name':
        remember(message.from_user.id, message.text, field=True)
        del keyboard_input[message.from_user.id]
        await message.answer(f'Запомнил! Теперь вы — '
                             f'{recall(message.from_user.id, field='name')}')
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
        remember(message.from_user.id, message.text)
        await message.answer(f'Запомнил!\n'
                             f'{message.text}')
        del keyboard_input[message.from_user.id]
    elif keyboard_input.get(message.from_user.id) == 'forget':
        asyncio.create_task(send_typing_indicator(message.chat.id, bot, wait=2))
        del keyboard_input[message.from_user.id]
        if message.text.lower() in ('все', 'всё'):
            forget(message.from_user.id)
            await message.reply('Удалил все записи')
            return
        if message.text not in recall(message.from_user.id, 'id'):
            await message.answer('Такого ключа нет')
            return
        forget(message.from_user.id, message.text)
        await message.answer(f'Удалил ключ {message.text} и его значение')
    else:
        await message.reply(
            'Используйте кнопки (должны быть снизу экрана), а если их нет: нажмите на 4 квадрата слева от скрепки')
