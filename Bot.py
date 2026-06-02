import os
import glob
import asyncio
import yt_dlp
from telegram import Update, InputMediaPhoto, InputMediaVideo
from telegram.ext import ApplicationBuilder, MessageHandler, filters, ContextTypes

BOT_TOKEN = "8327848961:AAHW-NYy8PuvjcDs-QxhL0A5IgDJsn5T4sQ"
BOT_USERNAME = "@YUKLAVCHI_10_BOT"

async def download_media(update: Update, context: ContextTypes.DEFAULT_TYPE):
    url = update.message.text.strip()
    if not url.startswith("http"):
        await update.message.reply_text("❌ Iltimos, to'g'ri havola yuboring!")
        return

    await update.message.reply_text("⏳ Yuklanmoqda, kuting...")

    folder = f"downloads/post_{update.message.message_id}"
    os.makedirs(folder, exist_ok=True)

    ydl_opts = {
        'outtmpl': f'{folder}/file_%(autonumber)s.%(ext)s',
        'quiet': True,
        'noplaylist': True,
        'format': 'best/bestvideo+bestaudio',
        'username': 'abro.r199728',
        'password': 'abrorbek10',
        'http_headers': {
            'User-Agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 16_0 like Mac OS X) AppleWebKit/605.1.15',
        },
    }

    try:
        loop = asyncio.get_event_loop()
        await loop.run_in_executor(
            None, lambda: yt_dlp.YoutubeDL(ydl_opts).download([url])
        )
    except Exception as e:
        await update.message.reply_text(f"❌ Xatolik: {str(e)}")
        cleanup(folder)
        return

    await asyncio.sleep(1)

    files = sorted([
        f for f in glob.glob(f'{folder}/*')
        if os.path.isfile(f)
        and not f.endswith('.part')
        and f.split('.')[-1].lower() in ['jpg', 'jpeg', 'png', 'webp', 'mp4', 'mkv', 'webm', 'mov']
    ], key=os.path.getctime)

    if not files:
        await update.message.reply_text("❌ Fayl topilmadi!")
        cleanup(folder)
        return

    caption = f"✅ Bizdan foydalanganingiz uchun xursandmiz!\n👉 {BOT_USERNAME}"

    try:
        if len(files) == 1:
            ext = files[0].split('.')[-1].lower()
            if ext in ['jpg', 'jpeg', 'png', 'webp']:
                await update.message.reply_photo(open(files[0], 'rb'), caption=caption,
                    read_timeout=300, write_timeout=300, connect_timeout=300)
            else:
                await update.message.reply_video(open(files[0], 'rb'), caption=caption,
                    read_timeout=300, write_timeout=300, connect_timeout=300)
        else:
            batch = []
            for i, f in enumerate(files):
                ext = f.split('.')[-1].lower()
                cap = caption if i == len(files) - 1 else None
                if ext in ['jpg', 'jpeg', 'png', 'webp']:
                    batch.append(InputMediaPhoto(open(f, 'rb'), caption=cap))
                else:
                    batch.append(InputMediaVideo(open(f, 'rb'), caption=cap))
                if len(batch) == 10 or i == len(files) - 1:
                    await update.message.reply_media_group(batch,
                        read_timeout=300, write_timeout=300, connect_timeout=300)
                    batch = []
    except Exception as e:
        await update.message.reply_text(f"❌ Yuborishda xato: {str(e)}")

    cleanup(folder)

def cleanup(folder):
    import shutil
    shutil.rmtree(folder, ignore_errors=True)

if __name__ == "__main__":
    app = ApplicationBuilder().token(BOT_TOKEN).build()
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, download_media))
    print("Bot ishga tushdi...")
    app.run_polling()
