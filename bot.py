import os
import re
import aiohttp
from aiogram import Bot, Dispatcher, types
from aiogram.utils.executor import start_webhook
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")
HIBP_API_KEY = os.getenv("HIBP_API_KEY")
WEBHOOK_URL = os.getenv("WEBHOOK_URL")  # твоя URL Render

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher(bot)

WEBHOOK_PATH = f"/webhook/{BOT_TOKEN}"
WEBHOOK_FULL_URL = f"{WEBHOOK_URL}{WEBHOOK_PATH}"
WEBAPP_HOST = "0.0.0.0"
WEBAPP_PORT = int(os.getenv("PORT", 8000))

def is_valid_email(email):
    return re.match(r"[^@]+@[^@]+\.[^@]+", email)

async def check_leaks(email):
    url = f"https://haveibeenpwned.com/api/v3/breachedaccount/{email}"
    headers = {
        "hibp-api-key": HIBP_API_KEY,
        "user-agent": "LeakBot"
    }
    async with aiohttp.ClientSession() as session:
        async with session.get(url, headers=headers) as resp:
            if resp.status == 200:
                return await resp.json()
            elif resp.status == 404:
                return None
            else:
                raise Exception(f"API error: {resp.status}")

@dp.message_handler(commands=["start"])
async def send_welcome(message: types.Message):
    await message.reply("Привіт! Надішли свій email, перевірю його на зливи.")

@dp.message_handler()
async def handle_email(message: types.Message):
    email = message.text.strip()
    
    if not is_valid_email(email):
        await message.reply("❌ Неправильна email-адреса.")
        return

    await message.reply("🔍 Перевіряю...")
    try:
        result = await check_leaks(email)

        with open("emails.txt", "a") as f:
            f.write(f"{email}\n")

        if result:
            await message.reply(
                f"⚠️ Email знайдено в {len(result)} зливах.\nЗахисти себе 👉 https://CPA-link.com"
            )
        else:
            await message.reply("✅ Усе чисто! Зливів не знайдено.")
    except Exception as e:
        await message.reply(f"❗ Помилка: {str(e)}")

# ============ WEBHOOK ============

async def on_startup(dp):
    await bot.set_webhook(WEBHOOK_FULL_URL)

async def on_shutdown(dp):
    await bot.delete_webhook()

if __name__ == '__main__':
    start_webhook(
        dispatcher=dp,
        webhook_path=WEBHOOK_PATH,
        on_startup=on_startup,
        on_shutdown=on_shutdown,
        skip_updates=True,
        host=WEBAPP_HOST,
        port=WEBAPP_PORT,
    )
