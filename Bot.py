
import os
import glob
import yt_dlp
import instaloader
from telegram import Update, InputMediaPhoto, InputMediaVideo
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
            if "/p/" in url:
                shortcode = url.split("/p/")[1].split("/")[0]
            elif "/reel/" in url:
                shortcode = url.split("/reel/")[1].split("/")[0]
            else:
                shortcode = url.rstrip("/").split("/")[-1]
            
            shortcode = shortcode.split("?")[0]
            
            os.makedirs("downloads", exist_ok=True)
            post = instaloader.Post.from_shortcode(L.context, shortcode)
            L.download_post(post, target="downloads")
            
            files = sorted(glob.glob('downloads/**/*', recursive=True))
            files = [f for f in files if os.path.isfile(f) and f.endswith(('.jpg', '.jpeg', '.png', '.mp4'))]
            
            if not files:
                await update.message.reply_text("❌ Fayl topilmadi!")
                return
            
            media_group = []
            for f in files:
                ext = f.split('.')[-1].lower()
                if ext in ['jpg', 'jpeg', 'png']:
                    media_group.append(InputMediaPhoto(open(f, 'rb')))
                elif ext == 'mp4':
                    media_group.append(InputMediaVideo(open(f, 'rb')))
            
            if len(media_group) == 1:
                ext = files[0].split('.')[-1].lower()
                if ext in ['jpg', 'jpeg', 'png']:
                    await update.message.reply_photo(open(files[0], 'rb'), read_timeout=300, write_timeout=300, connect_timeout=300)
                else:
                    await update.message.reply_video(open(files[0], 'rb'), read_timeout=300, write_timeout=300, connect_timeout=300)
            else:
                for i in range(0, len(media_group), 10):
                    await update.message.reply_media_group(media_group[i:i+10], read_timeout=300, write_timeout=300, connect_timeout=300)
            
            for f in files:
                os.remove(f)
                
        else:
            ydl_opts = {
                'format': 'best[filesize<50M]/best',
