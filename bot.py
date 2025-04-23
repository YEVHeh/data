import os
from aiogram import Bot, Dispatcher, types
from aiogram.utils.executor import start_webhook

from dotenv import load_dotenv
load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")
WEBHOOK_HOST = os.getenv("WEBHOOK_HOST")

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher(bot)

WEBHOOK_PATH = f"/webhook/{BOT_TOKEN}"
WEBHOOK_URL = f"{WEBHOOK_HOST}{WEBHOOK_PATH}"

@dp.message_handler(commands=['start'])
async def send_welcome(message: types.Message):
    await message.reply("Welcome! Send me your email to check for leaks.")

async def on_startup(dispatcher):
    print("Bot started")
    await bot.set_webhook(WEBHOOK_URL)

async def on_shutdown(dispatcher):
    print("Bot shutting down")

WEBAPP_HOST = "0.0.0.0"
WEBAPP_PORT = int(os.getenv("PORT", 3000))

if __name__ == "__main__":
    start_webhook(
        dispatcher=dp,
        webhook_path=WEBHOOK_PATH,
        on_startup=on_startup,
        on_shutdown=on_shutdown,
        skip_updates=True,
        host="0.0.0.0",  # or use your actual host
        port=int(os.environ.get("PORT", 5000)),
    )

