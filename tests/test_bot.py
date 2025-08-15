import asyncio
import types
import inspect
from unittest.mock import AsyncMock, MagicMock

import pytest

# We attempt to import the module under test as 'bot'.
# If your file is named differently (e.g., src/bot.py or app/bot.py),
# adjust this import accordingly to point to the module containing:
# - send_typing_indicator
# - router and handlers: start_bot, info, dice, roll_dice, text_dice, settings, name, full_name, username, dev, feedback
# - keyboards: keyboard, dev_keyboard, settings_keyboard
# - main function
try:
    import bot  # noqa: F401
except Exception as e:
    # As a fallback, try common alternative locations; comment/uncomment as needed.
    try:
        import src.bot as bot  # type: ignore
    except Exception:
        try:
            import app.bot as bot  # type: ignore
        except Exception:
            # Re-raise original to surface import issues clearly
            raise e from None

pytestmark = pytest.mark.asyncio

class DummyChat:
    def __init__(self, id):
        self.id = id

class DummyFromUser:
    def __init__(self, user_id=1, username="userx", full_name="User X"):
        self.id = user_id
        self.username = username
        self.full_name = full_name

class DummyMessage:
    def __init__(self, chat_id=123, bot_obj=None, text=""):
        self.chat = DummyChat(chat_id)
        self.text = text
        # aiogram Message has .bot set internally; for direct handler calls we provide it
        self.bot = bot_obj if bot_obj is not None else MagicMock(name="BotMock")
        # frequently used methods in handlers
        self._answers = []
        self._replies = []
        self._reply_stickers = []

    async def answer(self, text, **kwargs):
        self._answers.append((text, kwargs))
        return MagicMock(message_id=999, chat=self.chat)

    async def reply(self, text, **kwargs):
        self._replies.append((text, kwargs))
        return MagicMock(message_id=1000, chat=self.chat)

    async def reply_sticker(self, sticker, **kwargs):
        self._reply_stickers.append((sticker, kwargs))
        return MagicMock(message_id=1001, chat=self.chat)

class DummyCallbackQuery:
    def __init__(self, from_user=None, message=None, data=""):
        self.from_user = from_user or DummyFromUser()
        # In handlers we access callback_query.message.chat.id
        self.message = message or DummyMessage(chat_id=321)
        self.data = data

@pytest.fixture
def bot_mock():
    m = MagicMock(name="BotMock")
    # Async aiogram methods mocked as AsyncMock
    m.send_message = AsyncMock(name="send_message")
    m.delete_message = AsyncMock(name="delete_message")
    m.send_dice = AsyncMock(name="send_dice")
    m.edit_message_reply_markup = AsyncMock(name="edit_message_reply_markup")
    return m

@pytest.fixture(autouse=True)
def fast_sleep(monkeypatch):
    # Avoid real delays in tests
    async def _noop_sleep(seconds):
        return
    monkeypatch.setattr(asyncio, "sleep", _noop_sleep)
    yield

async def test_send_typing_indicator_sends_and_deletes(bot_mock):
    # Arrange
    # send_message should return an object with message_id
    message_obj = types.SimpleNamespace(message_id=555)
    bot_mock.send_message.return_value = message_obj

    # Act
    await bot.send_typing_indicator(chat_id=42, bot=bot_mock)

    # Assert
    bot_mock.send_message.assert_awaited_once_with(42, "...")
    bot_mock.delete_message.assert_awaited_once_with(42, 555)

async def test_start_bot_sends_typing_and_welcome(monkeypatch, bot_mock):
    # Arrange
    dummy_message = DummyMessage(chat_id=77, bot_obj=bot_mock, text="/start")

    sti_called = {}

    async def fake_indicator(chat_id, bot):
        sti_called["called"] = True
        sti_called["chat_id"] = chat_id
        sti_called["bot"] = bot

    # Patch helper to avoid relying on its internals here
    monkeypatch.setattr(bot, "send_typing_indicator", fake_indicator)

    # Act
    await bot.start_bot(dummy_message)

    # Assert
    assert sti_called.get("called") is True
    assert sti_called.get("chat_id") == 77
    assert sti_called.get("bot") is bot_mock

    # Validate that a welcome answer was sent with Markdown and a keyboard containing 'info'
    assert len(dummy_message._answers) == 1
    text, kwargs = dummy_message._answers[0]
    assert "MuziatikBot" in text
    assert kwargs.get("parse_mode") == "Markdown"
    rk = kwargs.get("reply_markup")
    # Expect a ReplyKeyboardMarkup; structure contains 'info' button
    # We cannot import aiogram types reliably here, but we can check nested structure existence via duck-typing
    # Aiogram v3 stores keyboard as list of rows under .keyboard
    has_info = False
    if rk and hasattr(rk, "keyboard"):
        for row in rk.keyboard:
            for btn in row:
                if getattr(btn, "text", "") == "info":
                    has_info = True
    assert has_info, "Expected ReplyKeyboardMarkup with an 'info' button"

async def test_info_sends_sticker_then_info_reply(monkeypatch):
    # Arrange
    dummy_message = DummyMessage(text="info")

    # Act
    await bot.info(dummy_message, bot=dummy_message.bot)

    # Assert
    # Sticker was sent
    assert len(dummy_message._reply_stickers) == 1
    sticker_id, _ = dummy_message._reply_stickers[0]
    assert isinstance(sticker_id, str) and len(sticker_id) > 10

    # Info reply was sent with expected content and keyboard
    assert len(dummy_message._replies) >= 1
    text, kwargs = dummy_message._replies[-1]
    assert "MuziatikBot" in text
    rk = kwargs.get("reply_markup")
    has_kubik = False
    has_info = False
    if rk and hasattr(rk, "keyboard"):
        for row in rk.keyboard:
            for btn in row:
                if getattr(btn, "text", "") == "Кубик":
                    has_kubik = True
                if getattr(btn, "text", "") == "info":
                    has_info = True
    # The provided keyboard in the source contains both "Кубик" and "info"
    assert has_kubik and has_info

async def test_dice_shows_inline_keyboard_options():
    # Arrange
    dummy_message = DummyMessage(text="Кубик")

    # Act
    await bot.dice(dummy_message, bot=dummy_message.bot)

    # Assert
    assert len(dummy_message._answers) == 1
    text, kwargs = dummy_message._answers[0]
    assert "Выберите вариант" in text
    ik = kwargs.get("reply_markup")
    # Expect inline keyboard with 'roll_dice' and 'text_dice'
    has_roll = False
    has_text = False
    if ik and hasattr(ik, "inline_keyboard"):
        for row in ik.inline_keyboard:
            for btn in row:
                if getattr(btn, "callback_data", "") == "roll_dice":
                    has_roll = True
                if getattr(btn, "callback_data", "") == "text_dice":
                    has_text = True
    assert has_roll and has_text

async def test_roll_dice_triggers_bot_send_dice(bot_mock):
    # Arrange
    cb = DummyCallbackQuery(from_user=DummyFromUser(user_id=999))

    # Act
    await bot.roll_dice(cb, bot=bot_mock)

    # Assert
    bot_mock.send_dice.assert_awaited_once_with(999)

async def test_text_dice_sends_random_result_in_bounds(monkeypatch, bot_mock):
    # Arrange: fix random for predictability
    monkeypatch.setattr(bot.random, "randint", lambda a, b: 4)
    cb = DummyCallbackQuery(from_user=DummyFromUser(user_id=888))

    # We'll intercept send_message to capture text
    sent = {}
    async def _send_message(uid, text):
        sent["uid"] = uid
        sent["text"] = text
    bot_mock.send_message = AsyncMock(side_effect=_send_message)

    # Act
    await bot.text_dice(cb, bot=bot_mock)

    # Assert
    # Should call send_typing_indicator internally; we don't assert that here,
    # but we assert final message content
    assert sent.get("uid") == 888
    assert "Выпало: 4" in sent.get("text", "")

async def test_settings_sends_beta_settings_message():
    # Arrange
    dummy_message = DummyMessage(text="Settings")

    # Act
    await bot.settings(dummy_message)

    # Assert
    # The handler should reply with text and inline settings keyboard
    assert len(dummy_message._replies) == 1
    text, kwargs = dummy_message._replies[0]
    assert "beta" in text.lower()
    ik = kwargs.get("reply_markup")
    # Expect an inline keyboard with callback_data 'name'
    has_name = False
    if ik and hasattr(ik, "inline_keyboard"):
        for row in ik.inline_keyboard:
            for btn in row:
                if getattr(btn, "callback_data", "") == "name":
                    has_name = True
    assert has_name

async def test_name_edits_text_and_shows_name_choice(monkeypatch, bot_mock):
    # Arrange: The handler uses global variable 'set' set in settings()
    dummy_message = DummyMessage(text="Settings", bot_obj=bot_mock)
    await bot.settings(dummy_message)

    # Ensure bot.edit_message_reply_markup is AsyncMock on our bot
    # Already set in bot_mock fixture
    cb = DummyCallbackQuery(from_user=DummyFromUser(), message=dummy_message, data="name")

    # Act
    await bot.name(cb, bot=bot_mock)

    # Assert: should prompt "Как вас называть?" via editing the message text,
    # then edit reply markup with options 'full_name' and 'username'
    # We can't easily assert edit_text as it's on the Message returned by reply in settings();
    # but we can assert edit_message_reply_markup was called with proper inline keyboard
    assert bot_mock.edit_message_reply_markup.await_count == 1
    args, kwargs = bot_mock.edit_message_reply_markup.await_args
    ik = kwargs.get("reply_markup")
    cbs = []
    if ik and hasattr(ik, "inline_keyboard"):
        for row in ik.inline_keyboard:
            for btn in row:
                cbs.append(getattr(btn, "callback_data", ""))
    assert "full_name" in cbs and "username" in cbs

async def test_full_name_sends_acknowledgement(bot_mock):
    # Arrange
    from_user = DummyFromUser(full_name="Alice Doe")
    cb = DummyCallbackQuery(from_user=from_user)

    # Capture message text
    sent = {}
    async def _send_message(chat_id, text):
        sent["chat_id"] = chat_id
        sent["text"] = text
    bot_mock.send_message = AsyncMock(side_effect=_send_message)

    # Act
    await bot.full_name(cb, bot=bot_mock)

    # Assert
    assert sent.get("chat_id") == cb.message.chat.id
    assert "Alice Doe" in sent.get("text", "")

async def test_username_sends_acknowledgement(bot_mock):
    # Arrange
    from_user = DummyFromUser(username="alice")
    cb = DummyCallbackQuery(from_user=from_user)

    # Capture message text
    sent = {}
    async def _send_message(chat_id, text):
        sent["chat_id"] = chat_id
        sent["text"] = text
    bot_mock.send_message = AsyncMock(side_effect=_send_message)

    # Act
    await bot.username(cb, bot=bot_mock)

    # Assert
    assert sent.get("chat_id") == cb.message.chat.id
    assert "alice" in sent.get("text", "")

async def test_dev_replies_with_dev_keyboard(bot_mock):
    # Arrange
    dummy = DummyMessage(text="dev", bot_obj=bot_mock)

    # Act
    await bot.dev(dummy)

    # Assert
    assert len(dummy._replies) == 1
    text, kwargs = dummy._replies[0]
    assert "Okei" in text or "Okei-dokei" in text
    rk = kwargs.get("reply_markup")
    # Expect a ReplyKeyboardMarkup that has 'Roll a die' and 'info' among others
    has_roll = False
    has_info = False
    if rk and hasattr(rk, "keyboard"):
        for row in rk.keyboard:
            for btn in row:
                if getattr(btn, "text", "") == "Roll a die":
                    has_roll = True
                if getattr(btn, "text", "") == "info":
                    has_info = True
    assert has_roll and has_info

async def test_feedback_replies_with_markdown_prompt():
    # Arrange
    dummy = DummyMessage(text="Feedback: hello")

    # Act
    await bot.feedback(dummy)

    # Assert
    assert len(dummy._replies) == 1
    text, kwargs = dummy._replies[0]
    assert "Отзыв" in text or "отзыв" in text or "feedback" in text.lower()
    assert kwargs.get("parse_mode") == "Markdown"

def test_main_is_async_and_defined():
    # Validate public interface existence without running the bot
    assert hasattr(bot, "main") and inspect.iscoroutinefunction(bot.main)

# Edge Case Tests

async def test_text_dice_random_bounds(monkeypatch, bot_mock):
    # Ensure when randint returns min/max, message is formatted correctly
    results = []
    async def capture(chat_id, text):
        results.append(text)
    bot_mock.send_message = AsyncMock(side_effect=capture)

    # min
    monkeypatch.setattr(bot.random, "randint", lambda a, b: 1)
    await bot.text_dice(DummyCallbackQuery(from_user=DummyFromUser(user_id=1)), bot=bot_mock)
    # max
    monkeypatch.setattr(bot.random, "randint", lambda a, b: 6)
    await bot.text_dice(DummyCallbackQuery(from_user=DummyFromUser(user_id=1)), bot=bot_mock)

    assert "Выпало: 1" in results[0]
    assert "Выпало: 6" in results[1]

async def test_send_typing_indicator_handles_bot_message_object(monkeypatch):
    # Validate that send_typing_indicator uses returned message_id
    class B:
        def __init__(self):
            self.send_message = AsyncMock()
            self.delete_message = AsyncMock()

    b = B()
    b.send_message.return_value = types.SimpleNamespace(message_id=777)
    await bot.send_typing_indicator(555, b)
    b.send_message.assert_awaited_once()
    b.delete_message.assert_awaited_once_with(555, 777)