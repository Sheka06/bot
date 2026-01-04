import asyncio
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
import yt_dlp
import os
from mutagen.easyid3 import EasyID3
from mutagen.id3 import ID3, APIC
# 🔹 Настройки
BOT_TOKEN = "8285787019:AAGb2taeKw6e6CdnfFnUdx7xyf2zX6SU908"
CHANNEL_ID = "@sheka_muzic"
CHANNEL_LINK = "https://t.me/sheka_muzic"
COVER_PATH = "custom_cover.jpg" # <--- Твоя обложка (фон)
bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()
# === Команда /start ===
@dp.message(Command("start"))
async def start_cmd(message: types.Message):
    await message.answer("👋 Отправь ссылку на YouTube — я загружу трек и добавлю фон 🎵")
# === Обработка ссылки ===
@dp.message()
async def handle_message(message: types.Message):
    if "youtube.com" in message.text or "youtu.be" in message.text:
        await message.answer("🎶 Скачиваю трек... Подожди немного ⏳")
        url = message.text
        output_file = "music.%(ext)s"
        ydl_opts = {
            "format": "bestaudio/best",
            "outtmpl": output_file,
            "postprocessors": [
                {
                    "key": "FFmpegExtractAudio",
                    "preferredcodec": "mp3",
                    "preferredquality": "192",
                }
            ],
        }
        try:
            # Скачиваем трек
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=True)
                title = info.get("title", "Музыка")
                filename = "music.mp3"
            # === Добавляем метаданные ===
            audio = EasyID3(filename)
            audio["title"] = title
            audio["artist"] = "SHEKAmuzic"
            audio.save()
            # === Добавляем обложку ===
            if os.path.exists(COVER_PATH):
                audiofile = ID3(filename)
                with open(COVER_PATH, "rb") as albumart:
                    audiofile["APIC"] = APIC(
                        encoding=3,
                        mime="image/jpeg",
                        type=3, # Cover(front)
                        desc=u"Cover",
                        data=albumart.read()
                    )
                audiofile.save(v2_version=3)
            caption = f"{CHANNEL_LINK}"
            # === Отправляем в канал ===
            await bot.send_audio(
                chat_id=CHANNEL_ID,
                audio=types.FSInputFile(filename),
                caption=caption,
                title=title,
                performer="SHEKAmuzic",
                thumbnail=types.FSInputFile(COVER_PATH) if os.path.exists(COVER_PATH) else None
            )
            await message.answer("✅ Трек успешно загружен и опубликован в канал!")
            os.remove(filename)
        except Exception as e:
            await message.answer(f"❌ Ошибка при загрузке: {e}")
    else:
        await message.answer("❗ Отправь ссылку на видео с YouTube.")
# === Запуск ===
async def main():
    print("🚀 Бот запущен и готов к работе!")
    await dp.start_polling(bot)
if __name__ == "__main__":
    asyncio.run(main())
