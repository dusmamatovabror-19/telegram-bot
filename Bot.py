
import os
import glob
import yt_dlp
from telegram import Update
from telegram.ext import ApplicationBuilder, MessageHandler, filters, ContextTypes

BOT_TOKEN = "8327848961:AAHW-NYy8PuvjcDs-QxhL0A5IgDJsn5T4sQ"

async def download_video(update: Update, context: ContextTypes.DEFAULT_TYPE):
    url = update.message.text.strip()
    if not url.startswith("http"):
        await update.message.reply_text("❌ Iltimos, to'g'ri havola yuboring!")
        return
    await update.message.reply_text("⏳ Yuklanmoqda, kuting...")
    os.makedirs("downloads", exist_ok=True)
    ydl_opts = {
        'format': 'best[filesize<50M]/best',
        'outtmpl': 'downloads/%(title)s.%(ext)s',
        'quiet': True,
        'noplaylist': True,
    }
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.extract_info(url, download=True)
        
        files = glob.glob('downloads/*')
        if not files:
            await update.message.reply_text("❌ Fayl topilmadi!")
            return
        
        filename = max(files, key=os.path.getctime)
        ext = filename.split('.')[-1].lower()
        
        if ext in ['jpg', 'jpeg', 'png', 'webp']:
            await update.message.reply_text("✅ Rasm yuborilmoqda...")
            with open(filename, 'rb') as f:
                await update.message.reply_photo(f, read_timeout=300, write_timeout=300, connect_timeout=300)
        else:
            await update.message.reply_text("✅ Video yuborilmoqda...")
            with open(filename, 'rb') as f:
                await update.message.reply_video(f, read_timeout=300, write_timeout=300, connect_timeout=300)
        
        os.remove(filename)
    except Exception as e:
        await update.message.reply_text(f"❌ Xatolik: {str(e)}")

if __name__ == "__main__":
    app = ApplicationBuilder().token(BOT_TOKEN).build()
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, download_video))
    print("Bot ishga tushdi...")
    app.run_polling()
