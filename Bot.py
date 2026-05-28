import os
import yt_dlp
from telegram import Update
from telegram.ext import ApplicationBuilder, MessageHandler, filters, ContextTypes

BOT_TOKEN = "8327848961:AAHW-NYy8PuvjcDs-QxhL0A5IgDJsn5T4sQ"

async def download_video(update: Update, context: ContextTypes.DEFAULT_TYPE):
    url = update.message.text.strip()
    if not url.startswith("http"):
        await update.message.reply_text("❌ Iltimos, to'g'ri havola yuboring!")
        return
    await update.message.reply_text("⏳ Video yuklanmoqda, kuting...")
    ydl_opts = {
        'format': 'best[filesize<50M]/best',
        'outtmpl': 'downloads/%(title)s.%(ext)s',
        'quiet': True,
    }
    try:
        os.makedirs("downloads", exist_ok=True)
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            filename = ydl.prepare_filename(info)
        await update.message.reply_text("✅ Yuborilmoqda...")
        with open(filename, 'rb') as video_file:
            await update.message.reply_video(video_file)
        os.remove(filename)
    except Exception as e:
        await update.message.reply_text(f"❌ Xatolik: {str(e)}")

if __name__ == "__main__":
    app = ApplicationBuilder().token(BOT_TOKEN).build()
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, download_video))
    print("Bot ishga tushdi...")
    app.run_polling()
