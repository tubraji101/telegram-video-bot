import json
import os
import logging
import asyncio
import yt_dlp
from aiogram import Bot, Dispatcher, types
from aiogram.utils import executor
from pydrive.auth import GoogleAuth
from pydrive.drive import GoogleDrive

# Load environment variables
BOT_TOKEN = os.getenv("BOT_TOKEN")
GDRIVE_FOLDER_ID = os.getenv("GDRIVE_FOLDER_ID")
GDRIVE_CREDENTIALS = os.getenv("GDRIVE_CREDENTIALS")

# Setup logging
logging.basicConfig(level=logging.INFO)

# Initialize bot and dispatcher
bot = Bot(token=BOT_TOKEN)
dp = Dispatcher(bot)

logging.info("🚀 Bot Started! Waiting for commands...")

# Google Drive Authentication
logging.info("🔑 Authenticating Google Drive...")
gauth = GoogleAuth()
gauth.LoadCredentialsFile("gdrive_creds.json")
if not gauth.credentials:
    gauth.LocalWebserverAuth()
    gauth.SaveCredentialsFile("gdrive_creds.json")
drive = GoogleDrive(gauth)

# Function to download video
def download_video(url):
    ydl_opts = {
        'format': 'best',
        'outtmpl': 'downloads/%(title)s.%(ext)s',
    }
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=True)
        filename = ydl.prepare_filename(info)
    return filename

# Function to upload to Google Drive
def upload_to_gdrive(file_path):
    file_name = os.path.basename(file_path)
    gfile = drive.CreateFile({'title': file_name, 'parents': [{'id': GDRIVE_FOLDER_ID}]})
    gfile.SetContentFile(file_path)
    gfile.Upload()
    return gfile['id']

# Handle start command
@dp.message_handler(commands=['start'])
async def start_command(message: types.Message):
    logging.info(f"📩 Received /start from {message.chat.id}")
    await message.reply("👋 Welcome! Send me a video link to download and upload to Google Drive.")

# Handle video link input
@dp.message_handler()
async def process_video(message: types.Message):
    url = message.text.strip()
    logging.info(f"🔗 Received video link: {url}")
    await message.reply("⏳ Downloading video...")
    
    try:
        file_path = download_video(url)
        await message.reply("✅ Download complete! Uploading to Google Drive...")
        
        file_id = upload_to_gdrive(file_path)
        gdrive_link = f"https://drive.google.com/file/d/{file_id}/view"
        
        await message.reply(f"✅ Upload successful! Here is your link: {gdrive_link}")
    
    except Exception as e:
        logging.error(f"❌ Error: {e}")
        await message.reply(f"❌ Error: {e}")

# Run bot
if __name__ == '__main__':
    logging.info("🟢 Starting bot polling...")
    executor.start_polling(dp, skip_updates=True)
