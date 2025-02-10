import logging
import os
import yt_dlp
from aiogram import Bot, Dispatcher, types
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils import executor

API_TOKEN = "7541428401:AAEE-tQI2qOoHbArMyNDOB--LGGUy4rOeME"

# Initialize bot and dispatcher
bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot)

logging.basicConfig(level=logging.INFO)

def download_video(url, format_id):
    options = {
        'format': format_id,
        'outtmpl': 'downloads/%(title)s.%(ext)s',
    }
    with yt_dlp.YoutubeDL(options) as ydl:
        info = ydl.extract_info(url, download=True)
        return ydl.prepare_filename(info)

@dp.message_handler(commands=['start'])
async def start(message: types.Message):
    await message.reply("🔗 Send me a video link to download.")

@dp.message_handler()
async def fetch_video(message: types.Message):
    url = message.text
    
    try:
        with yt_dlp.YoutubeDL({'quiet': True}) as ydl:
            info = ydl.extract_info(url, download=False)
            formats = info.get('formats', [])
            buttons = []
            
            for fmt in formats:
                if fmt.get('filesize') and fmt.get('format_note'):
                    btn = InlineKeyboardButton(
                        text=f"{fmt['format_note']} ({round(fmt['filesize'] / 1024 / 1024, 2)} MB)",
                        callback_data=f"download|{url}|{fmt['format_id']}"
                    )
                    buttons.append([btn])
            
            markup = InlineKeyboardMarkup(inline_keyboard=buttons)
            await message.reply("📥 Choose the video quality:", reply_markup=markup)
    except Exception as e:
        await message.reply(f"❌ Error: {str(e)}")

@dp.callback_query_handler(lambda c: c.data.startswith('download'))
async def process_download(callback_query: types.CallbackQuery):
    _, url, format_id = callback_query.data.split('|')
    await bot.send_message(callback_query.from_user.id, "📥 Downloading video...")
    
    try:
        file_path = download_video(url, format_id)
        await bot.send_video(callback_query.from_user.id, video=open(file_path, 'rb'))
        os.remove(file_path)
    except Exception as e:
        await bot.send_message(callback_query.from_user.id, f"❌ Download failed: {str(e)}")

if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
