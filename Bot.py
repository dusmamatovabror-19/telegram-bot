import os
import glob
import asyncio
import yt_dlp
from telegram import Update, InputMediaPhoto, InputMediaVideo
from telegram.ext import ApplicationBuilder, MessageHandler, filters, ContextTypes

BOT_TOKEN = "8327848961:AAHW-NYy8PuvjcDs-QxhL0A5IgDJsn5T4sQ"

async def download_media(update: Update, context: ContextTypes.DEFAULT_TYPE):
    url = update.message.text.strip()
    if not url.startswith("http"):
        await update.message.reply_text("❌ Iltimos, to'g'ri havola yuboring!")
        return
    await update.message.reply_text("⏳ Yuklanmoqda, kuting...")
    
    os.makedirs("downloads", exist_ok=True)
    
    ydl_opts = {
        'outtmpl': 'downloads/file_%(autonumber)s.%(ext)s',
        'quiet': True,
        'noplaylist': True,
        'format': 'best[filesize<50M]/best',
        'concurrent_fragment_downloads': 4,
    }
    
    try:
        loop = asyncio.get_event_loop()
        await loop.run_in_executor(None, lambda: yt_dlp.YoutubeDL(ydl_opts).download([url]))
        
        await asyncio.sleep(1)
        
        files = sorted(glob.glob('downloads/*'), key=os.path.getctime)
        files = [f for f in files if os.path.isfile(f) and not f.endswith('.part') and not f.endswith('.ytdl')]
        
        if not files:
            await update.message.reply_text("❌ Fayl topilmadi!")
            return
        
        media_group = []
        for f in files:
            ext = f.split('.')[-1].lower()
            if ext in ['jpg', 'jpeg', 'png', 'webp']:
                media_group.append(InputMediaPhoto(open(f, 'rb')))
            elif ext in ['mp4', 'mkv', 'webm', 'mov']:
                media_group.append(InputMediaVideo(open(f, 'rb')))
        
        if len(media_group) == 0:
            await update.message.reply_text("❌ Media topilmadi!")
        elif len(media_group) == 1:
            ext = files[0].split('.')[-1].lower()
            if ext in ['jpg', 'jpeg', 'png', 'webp']:
                await update.message.reply_photo(open(files[0], 'rb'), read_timeout=300, write_timeout=300, connect_timeout=300)
            else:
                await update.message.reply_video(open(files[0], 'rb'), read_timeout=300, write_timeout=300, connect_timeout=300)
        else:
            for i in range(0, len(media_group), 10):
                await update.message.reply_media_group(media_group[i:i+10], read_timeout=300, write_timeout=300, connect_timeout=300)
        
        await update.message.reply_text("✅ Tayyor!")
        
        for f in files:
            try:
                os.remove(f)
            except:
                pass
                
    except Exception as e:
        await update.message.reply_text(f"❌ Xatolik: {str(e)}")

if __name__ == "__main__":
    app = ApplicationBuilder().token(BOT_TOKEN).build()
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, download_media))
    print("Bot ishga tushdi...")
    app.run_polling()
