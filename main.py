import os
import asyncio
import yt_dlp
from aiogram import Bot, Dispatcher, types
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.filters import Command

# Берём токен из секретов Replit
BOT_TOKEN = os.getenv("BOT_TOKEN")
if not BOT_TOKEN:
    raise ValueError("❌ BOT_TOKEN не найден! Добавь его в Secrets.")

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()


# --- Главное меню ---
def main_menu():
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="🎥 Скачать видео", callback_data="video_mode"),
                InlineKeyboardButton(text="🎵 Скачать аудио", callback_data="audio_mode"),
            ],
            [InlineKeyboardButton(text="ℹ️ Помощь", callback_data="help")]
        ]
    )
    return keyboard


# --- /start ---
@dp.message(Command("start"))
async def start_cmd(message: types.Message):
    await message.answer(
        "👋 Привет! Я бот для скачивания видео и аудио из соцсетей.\n\n"
        "📌 Поддерживаю YouTube, TikTok, Instagram, VK, Twitter, Facebook и др.\n"
        "Просто отправь ссылку 🔗, и я помогу скачать 🎥 или 🎵.",
        reply_markup=main_menu()
    )


# --- Помощь ---
@dp.callback_query()
async def callback_handler(callback: types.CallbackQuery):
    if callback.data == "help":
        await callback.message.answer(
            "ℹ️ Отправь ссылку на видео, и выбери формат (🎥 или 🎵).\n"
            "Я скачаю и отправлю файл прямо сюда.\n\n"
            "Поддержка: @woxda"
        )
    elif callback.data == "video_mode":
        await callback.message.answer("📥 Отправь ссылку на видео, и я скачаю его 🎥")
    elif callback.data == "audio_mode":
        await callback.message.answer("📥 Отправь ссылку на видео, я сделаю из него аудио 🎵")
    await callback.answer()


# --- Обработка ссылок ---
@dp.message()
async def handle_links(message: types.Message):
    url = message.text.strip()
    if not url.startswith("http"):
        await message.answer("⚠️ Это не похоже на ссылку, попробуй ещё раз.")
        return

    # Кнопки выбора формата
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="🎥 Видео", callback_data=f"download|video|{url}"),
                InlineKeyboardButton(text="🎵 Аудио", callback_data=f"download|audio|{url}")
            ]
        ]
    )
    await message.answer("Что хочешь скачать? 🎯", reply_markup=keyboard)


# --- Скачивание ---
@dp.callback_query()
async def process_download(callback: types.CallbackQuery):
    if not callback.data.startswith("download|"):
        return

    _, mode, url = callback.data.split("|", 2)
    await callback.message.answer("⏳ Скачиваю, подожди немного...")

    filename = "download"

    # Опции yt-dlp
    if mode == "video":
        ydl_opts = {"outtmpl": f"{filename}.mp4", "format": "mp4"}
    else:  # audio
        ydl_opts = {
            "outtmpl": f"{filename}.mp3",
            "format": "bestaudio/best",
            "postprocessors": [
                {"key": "FFmpegExtractAudio", "preferredcodec": "mp3", "preferredquality": "192"}
            ]
        }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])

        # Отправляем файл
        if mode == "video" and os.path.exists(f"{filename}.mp4"):
            await callback.message.answer_video(open(f"{filename}.mp4", "rb"))
            os.remove(f"{filename}.mp4")
        elif mode == "audio" and os.path.exists(f"{filename}.mp3"):
            await callback.message.answer_audio(open(f"{filename}.mp3", "rb"))
            os.remove(f"{filename}.mp3")
        else:
            await callback.message.answer("⚠️ Не удалось скачать файл.")

    except Exception as e:
        await callback.message.answer(f"❌ Ошибка при скачивании: {e}")

    await callback.answer()


# --- Запуск ---
async def main():
    print("🤖 Бот запущен...")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
