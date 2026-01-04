from mutagen.easyid3 import EasyID3
from mutagen.id3 import ID3, APIC

# Настройки
BOT_TOKEN = os.getenv("BOT_TOKEN")
CHANNEL_ID = "@sheka_muzic"
CHANNEL_LINK = "https://t.me/sheka_muzic"
COVER_PATH = "cover.jpg"

# Логи
logging.basicConfig(level=logging.INFO)

# Правильный способ задать parse_mode в aiogram 3.13+
bot = Bot(token=BOT_TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
dp = Dispatcher()

# Команда /start
@dp.message(Command("start"))
async def start_cmd(message: types.Message):
    await message.answer("Отправь ссылку на YouTube — я загружу трек и добавлю фон")

# Обработка ссылки
@dp.message()
async def handle_message(message: types.Message):
    if not message.text or ("youtube.com" not in message.text and "youtu.be" not in message.text):
@@ -59,13 +54,11 @@ async def handle_message(message: types.Message):
            title = info.get("title", "Музыка")
        filename = "music.mp3"

        # Метаданные
        audio = EasyID3(filename)
        audio["title"] = title
        audio["artist"] = "SHEKAmuzic"
        audio.save()

        # Обложка
        if os.path.exists(COVER_PATH):
            audiofile = ID3(filename)
            with open(COVER_PATH, "rb") as f:
@@ -78,7 +71,6 @@ async def handle_message(message: types.Message):
                )
            audiofile.save(v2_version=3)

        # Отправка в канал
        await bot.send_audio(
            chat_id=CHANNEL_ID,
            audio=FSInputFile(filename),
@@ -90,7 +82,6 @@ async def handle_message(message: types.Message):

        await message.answer("Трек успешно загружен и опубликован в канал!")

        # Удаление временных файлов
        for f in [filename, "music.webm"]:
            if os.path.exists(f):
                os.remove(f)
@@ -99,7 +90,6 @@ async def handle_message(message: types.Message):
        logging.error(f"Ошибка: {e}")
        await message.answer(f"Ошибка при загрузке: {str(e)}")

# Веб-сервер + healthz
async def on_startup(app):
    webhook_url = f"https://{os.getenv('RENDER_EXTERNAL_HOSTNAME')}/webhook"
    await bot.set_webhook(webhook_url)
@@ -112,24 +102,14 @@ async def on_shutdown(app):
app["bot"] = bot
app["dispatcher"] = dp

# Health check (чтобы Render не спал)
async def healthz(request):
    return web.Response(text="OK")
app.router.add_get("/healthz", healthz)

# Webhook
SimpleRequestHandler(dispatcher=dp, bot=bot).register(app, path="/webhook")
app.on_startup.append(on_startup)
app.on_shutdown.append(on_shutdown)

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    web.run_app(app, host="0.0.0.0", port=port)
    Commit changes
┌───────────────────────────────────────────────────────┐
│ ВСЕ СДЕЛАНО!!!!!!!!!!!!!!!                            │ ← сюда печатаешь любой текст, хоть «готово»
└───────────────────────────────────────────────────────┘
( ) Commit directly to the main branch.   ← галочка уже стоит
( ) Create a new branch...                ← не трогай

               [Commit changes]   ← большая зелёная кнопка
