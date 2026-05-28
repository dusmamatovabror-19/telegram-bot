
import os
import glob
import yt_dlp
import instaloader
from telegram import Update
from telegram.ext import ApplicationBuilder, MessageHandler, filters, ContextTypes

BOT_TOKEN = "8327848961:AAHW-NYy8PuvjcDs-QxhL0A5IgDJsn5T4sQ"

L = instaloader.Instaloader(download_videos=True, download_pictures=True, save_metadata=False, post_metadata_txt_pattern="")

async def download_video(update: Update, context: ContextTypes.DEFAULT_TYPE):
    url = update.message.text.strip()
    if not url.startswith("http"):
        await update.message.reply_text("❌ Iltimos, to'g'ri havola yuboring!")
        return
    await update.message.reply_text("⏳ Yuklanmoqda, kuting...")
    
    try:
        if "instagram.com" in url:
            shortcode = url.split("/p/")[-1].split("/")[0] if "/p/" in url else url.split("/reel/")[-1].split("/")[0]
            post = instaloader.Post.from_shortcode(L.context, shortcode)
            L.download_post(post, target="downloads")
            
            files = glob.glob('downloads/**/*', recursive=True)
            files = [f for f in files if os.path.isfile(f) and f.endswith(('.jpg', '.jpeg', '.png', '.mp4'))]
            
            if not files:
                await update.message.reply_text("❌ Fayl topilmadi!")
                return
            
            for filename in files:
                ext = filename.split('.')[-1].lower()
                if ext in ['jpg', 'jpeg', 'png']:
                    with open(filename, 'rb') as f:
                        await update.message.reply_photo(f, read_timeout=300, write_timeout=300, connect_timeout=300)
                elif ext == 'mp4':
                    with open(filename, 'rb') as f:
                        await update.message.reply_video(f, read_timeout=300, write_timeout=300, connect_timeout=300)
                os.remove(filename)
        else:
            ydl_opts = {
                'format': 'best[filesize<50M]/best',
                'outtmpl': 'downloads/%(title)s.%(ext)s',
                'quiet': True,
            }
            os.makedirs("downloads", exist_ok=True)
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                ydl.extract_info(url, download=True)
            
            files = glob.glob('downloads/*')
            if not files:
                await update.message.reply_text("❌ Fayl topilmadi!")
                return
            
            filename = max(files, key=os.path.getctime)
            with open(filename, 'rb') as f:
                await update.message.reply_video(f, read_timeout=300, write_timeout=300, connect_timeout=300)
            os.remove(filename)
            
        await update.message.reply_text("✅ Tayyor!")
    except Exception as e:
        await update.message.reply_text(f"❌ Xatolik: {str(e)}")

if __name__ == "__main__":
    app = ApplicationBuilder().token(BOT_TOKEN).build()
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, download_video))
    print("Bot ishga tushdi...")
    app.run_polling()
