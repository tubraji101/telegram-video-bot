import os
from aiogram import bot, Dispatcher, typs
from aiogram.utils import executcher

token = os.getenv("7541428401:AAEE-tQI2qOoHbArMyNDOB--LGGUy4rOeME")
bot = bot(loken=TOKEN)
dp = Dispatcher(bot)

@dp.message_handler(commands=['start'])
async def start(message: types.Message):
   await message.replay("hello! Send me a video link to download.")

if __name__=="_main_":
  executor.start_polling(dp)
