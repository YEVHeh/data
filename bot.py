import os
import re
import aiohttp
import asyncio
from aiogram import Bot, Dispatcher, Router, types
from aiogram.filters import CommandStart
from aiogram.webhook.aiohttp_server import SimpleRequestHandler, setup_application
from aiohttp import web
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")
HIBP_API_KEY = os.getenv("HIBP_API_KEY")
WEBHOOK_URL = os.getenv("WEBHOOK_URL")  # ваша URL-адреса для вебхука

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()
router = Router()
dp.include_router(router)

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

@router.message(CommandStart())
async def send_welcome(message: types.Message):
    await message.reply("Привіт! Надішли свою електронну адресу, і я перевірю, чи була вона скомпрометована.")

@router.message()
async def handle_email(message: types.Message):
    email = message.text.strip()
    await message.reply("🔍 Перевіряю...")

    if not is_valid_email(email):
        await message.reply("❌ Невірна електронна адреса.")
        return

    try:
        result = await check_leaks(email)

        with open("emails.txt", "a") as f:
            f.write(f"{email}\n")

        if result:
            await message.reply(
                f"⚠️ Ця електронна адреса була знайдена в {len(result)} порушеннях безпеки.\nЗахисти себе 👉 https://CPA-link.com"
            )
        else:
            await message.reply("✅ Все гаразд! Порушень не виявлено.")
    except Exception as e:
        await message.reply(f"❗ Помилка: {str(e)}")

async def on_startup(bot: Bot):
    await bot.set_webhook(f"{WEBHOOK_URL}/webhook/{BOT_TOKEN}")

async def on_shutdown(bot: Bot):
    await bot.delete_webhook()

async def main():
    app = web.Application()
    SimpleRequestHandler(dispatcher=dp, bot=bot).register(app, path=f"/webhook/{BOT_TOKEN}")
    setup_application(app, dp, bot=bot)
    await on_startup(bot)
    try:
        runner = web.AppRunner(app)
        await runner.setup()
        site = web.TCPSite(runner, "0.0.0.0", int(os.getenv("PORT", 8000)))
        await site.start()
        print("Bot is running...")
        while True:
            await asyncio.sleep(3600)
    finally:
        await on_shutdown(bot)

if __name__ == "__main__":
    asyncio.run(main())

