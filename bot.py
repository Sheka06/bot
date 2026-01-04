import asyncio
import os
import logging
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from aiogram.types import FSInputFile
from aiogram.webhook.aiohttp_server import SimpleRequestHandler
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiohttp import web
import yt_dlp
from mutagen.easyid3 import EasyID3
from mutagen.id3 import ID3, APIC

BOT_TOKEN = os.getenv("BOT_TOKEN")
CHANNEL_ID = "@sheka_muzic"
CHANNEL_LINK = "https://t.me/sheka_muzic"
CUSTOM_COVER = "custom_cover.jpg"  # Твоя Honda Fit

logging.basicConfig(level=logging.INFO)

bot = Bot(token=BOT_TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
dp = Dispatcher()

@dp.message(Command("start"))
async def start_cmd(message: types.Message):
    await message.answer("Отправь ссылку на YouTube — скачаю трек с твоей обложкой Honda Fit 🔥")

@dp.message()
async def handle_message(message: types.Message):
    if not message.text or ("youtube.com" not in message.text and "youtu.be" not in message.text):
        await message.answer("Отправь ссылку на видео с YouTube.")
        return

    status_msg = await message.answer("Скачиваю трек... ⏳")

    url = message.text
    ydl_opts = {
        "format": "bestaudio/best",
        "outtmpl": "music.%(ext)s",
        "postprocessors": [{
            "key": "FFmpegExtractAudio",
            "preferredcodec": "mp3",
            "preferredquality": "192",
        }],
        "quiet": True,
        "no_warnings": True,
        "ignoreerrors": True,  # Игнорируем ошибки видео
        "no_check_certificate": True,
        "extract_audio": True,
        "audioformat": "mp3",
        "nocheckcertificate": True,
        "cookiefile": None,  # Не используем куки
        "retries": 10,
        "fragment_retries": 10,
        "skip_unavailable_fragments": True,
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            if not info:
                await status_msg.edit_text("Видео недоступно или заблокировано.")
                return
            title = info.get("title", "Музыка")
        filename = "music.mp3"

        # Метаданные
        audio = EasyID3(filename)
        audio["title"] = title
        audio["artist"] = "SHEKAmuzic"
        audio.save()

        # Кастомная обложка (твоя Honda Fit)
        if os.path.exists(CUSTOM_COVER):
            audiofile = ID3(filename)
            with open(CUSTOM_COVER, "rb") as f:
                audiofile["APIC"] = APIC(
                    encoding=3,
                    mime="image/jpeg",
                    type=3,
                    desc="Cover",
                    data=f.read()
                )
            audiofile.save(v2_version=3)

        # Отправка
        await bot.send_audio(
            chat_id=CHANNEL_ID,
            audio=FSInputFile(filename),
            caption=CHANNEL_LINK,
            title=title,
            performer="SHEKAmuzic",
            thumbnail=FSInputFile(CUSTOM_COVER) if os.path.exists(CUSTOM_COVER) else None
        )

        await status_msg.edit_text("Трек загружен с твоей обложкой Honda Fit! 🔥")

        # Удаление временных
        for f in [filename, "music.webm"]:
            if os.path.exists(f):
                os.remove(f)

    except Exception as e:
        logging.error(f"Ошибка: {e}")
        await status_msg.edit_text(f"Не удалось скачать: {str(e)[:200]}... Попробуй другую ссылку.")

# Веб-сервер (без изменений)
async def on_startup(app):
    webhook_url = f"https://{os.getenv('RENDER_EXTERNAL_HOSTNAME')}/webhook"
    await bot.set_webhook(webhook_url)
    logging.info(f"Webhook установлен: {webhook_url}")

async def on_shutdown(app):
    await bot.delete_webhook()

app = web.Application()
app["bot"] = bot
app["dispatcher"] = dp

async def healthz(request):
    return web.Response(text="OK")
app.router.add_get("/healthz", healthz)

SimpleRequestHandler(dispatcher=dp, bot=bot).register(app, path="/webhook")
app.on_startup.append(on_startup)
app.on_shutdown.append(on_shutdown)

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    web.run_app(app, host="0.0.0.0", port=port)
