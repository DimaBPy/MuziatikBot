import os
from pprint import pprint

from telegram import Bot, ReplyKeyboardMarkup
from telegram.ext import MessageHandler, Updater, Filters
from dotenv import load_dotenv
import requests

load_dotenv()
API_TOKEN_muziatikBot = os.getenv('API_TOKEN_muziatikBot')
CATS = 'https://api.thecatapi.com/v1/images/search'
response = requests.get(CATS)
bot = Bot(API_TOKEN_muziatikBot)
button = ReplyKeyboardMarkup([['Котики!']])

updater = Updater(API_TOKEN_muziatikBot)
bot.send_message(os.getenv('MY_CHAT_ID'), )
bot.send_message(os.getenv('MOMMY_CHAT_ID'), )
bot.send_message(os.getenv('DADDY_CHAT_ID'), )
bot.send_message(os.getenv('GRANNY_CHAT_ID'), )


def cats(update, context):
    chat = update.effective_chat
    context.bot.send_photo(chat.id, response.json()[0].get('url'), reply_markup=button)



updater.start_polling()
updater.idle()

# bot.send_photo(os.getenv('MOMMY_CHAT_ID'), )
