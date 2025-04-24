# -*- coding: utf-8 -*-

from aiogram import Dispatcher, Bot
from config import TOKEN
import requests

url = f"https://api.telegram.org/bot{TOKEN}/deleteWebhook"
response = requests.get(url)
print(response.json())  # Должно быть {"ok": True, "result": True}
bot = Bot(token=TOKEN)
dp = Dispatcher()

