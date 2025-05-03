import os

from pyrogram import Client
from dotenv import load_dotenv

load_dotenv()
ID = os.getenv("ID")
HASH = os.getenv("HASH")
MOMMY_ID = os.getenv("MOMMY_ID")
Muziatik = Client('my account', ID, HASH)
Muziatik.start()
Muziatik.send_message(int(MOMMY_ID), '#ПишетБот')
Muziatik.stop()