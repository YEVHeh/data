import os
import re
import aiohttp
from aiohttp import web
from dotenv import load_dotenv
from aiogram import Bot, Dispatcher, types, F
from aiogram.webhook.aiohttp_server import SimpleRequestHandler, setup_application

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")
HIBP_API_KEY = os.getenv("HIBP_API_KEY")
WEBHOOK_URL = os.getenv("WEBHOOK_URL")  # твоя URL Render

WEBHOOK_PATH = f"/webhook/{BOT_TOKEN}"
WEBHOOK_FULL_URL = f"{WEBHOOK_URL}{WEBHOOK_PATH}"
WEBAPP_HOST = "0.0.0.0"
WEBAPP_PORT = int(os.getenv("PORT", 8000))

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

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

@dp.message(commands=["start"])
async def send_welcome(message: types.Message):
    await message.answer("Привіт! Надішли свою електронну адресу, і я перевірю, чи була вона скомпрометована.")

@dp.message(F.text)
async def handle_email(message: types.Message):
    email = message.text.strip()
    await message.answer("🔍 Перевіряю...")

    if not is_valid_email(email):
        await message.answer("❌ Невірна електронна адреса.")
        return

    try:
        result = await check_leaks(email)

        with open("emails.txt", "a") as f:
            f.write(f"{email}\n")

        if result:
            await message.answer(
                f"⚠️ Ця електронна адреса була знайдена в {len(result)} порушеннях безпеки.\nЗахисти себе 👉 https://CPA-link.com"
            )
        else:
            await message.answer("✅ Все гаразд! Порушень не виявлено.")
    except Exception as e:
        await message.answer(f"❗ Помилка: {str(e)}")

# ===== WEBHOOK INTEGRATION =====

async def on_startup(app):
    await bot.set_webhook(WEBHOOK_FULL_URL)

async def on_shutdown(app):
    await bot.delete_webhook()

app = web.Application()
app.on_startup.append(on_startup)
app.on_shutdown.append(on_shutdown)

SimpleRequestHandler(dispatcher=dp, bot=bot).register(app, path=WEBHOOK_PATH)
setup_application(app, dp, bot=bot)

if __name__ == "__main__":
    web.run_app(app, host=WEBAPP_HOST, port=WEBAPP_PORT)
