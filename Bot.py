import os
import glob
import asyncio
import yt_dlp
import instaloader
import re
from telegram import Update, InputMediaPhoto, InputMediaVideo
from telegram.ext import ApplicationBuilder, MessageHandler, filters, ContextTypes

BOT_TOKEN = "8327848961:AAHW-NYy8PuvjcDs-QxhL0A5IgDJsn5T4sQ"
BOT_USERNAME = "@YUKLAVCHI_10_BOT"

# Instaloader sozlash
L = instaloader.Instaloader(
    download_videos=True,
    download_video_thumbnails=False,
    download_geotags=False,
    download_comments=False,
    save_metadata=False,
    post_metadata_txt_pattern=""
)

# Login (bir marta)
try:
    L.login('abro.r199728', 'abrorbek10')
except:
    pass

def get_instagram_shortcode(url):
    match = re.search(r'/p/([A-Za-z0-9_-]+)', url) or re.search(r'/reel/([A-Za-z0-9_-]+)', url)
    return match.group(1) if match else None

def download_instagram(url, folder):
    shortcode = get_instagram_shortcode(url)
    if not shortcode:
        return False
    try:
        post = instaloader.Post.from_shortcode(L.context, shortcode)
        L.dirname_pattern = folder
        L.download_post(post, target=folder)
        return True
    except Exception as e:
        print(f"Instaloader xato: {e}")
        return False

async def download_media(update: Update, context: ContextTypes.DEFAULT_TYPE):
    url = update.message.text.strip()
    if not url.startswith("http"):
        await update.message.reply_text("❌ Iltimos, to'g'ri havola yuboring!")
        return

    await update.message.reply_text("⏳ Yuklanmoqda, kuting...")
    
    folder = f"downloads/post_{update.message.message_id}"
    os.makedirs(folder, exist_ok=True)

    success = False

    # Instagram bo'lsa - instaloader ishlatamiz
    if "instagram.com" in url:
        loop = asyncio.get_event_loop()
        success = await loop.run_in_executor(None, lambda: download_instagram(url, folder))

    # Boshqa saytlar yoki instaloader ishlamasa - yt-dlp
    if not success:
        ydl_opts = {
            'outtmpl': f'{folder}/file_%(autonumber)s.%(ext)s',
            'quiet': True,
            'noplaylist': True,
            'format': 'best/bestvideo+bestaudio',
        }
        try:
            loop = asyncio.get_event_loop()
            await loop.run_in_executor(None, lambda: yt_dlp.YoutubeDL(ydl_opts).download([url]))
            success = True
        except Exception as e:
            await update.message.reply_text(f"❌ Xatolik: {str(e)}")

    await asyncio.sleep(1)

    # Faqat rasm va video fayllarni olish
    all_files = glob.glob(f'{folder}/**/*', recursive=True) + glob.glob(f'{folder}/*')
    files = [
        f for f in all_files
        if os.path.isfile(f)
        and not f.endswith('.part')
        and f.split('.')[-1].lower() in ['jpg', 'jpeg', 'png', 'webp', 'mp4', 'mkv', 'webm', 'mov']
    ]
    files = sorted(files, key=os.path.getctime)

    if not files:
        await update.message.reply_text("❌ Fayl topilmadi!")
        cleanup(folder)
        return

    caption = f"✅ Bizdan foydalanganingiz uchun xursandmiz!\n👉 {BOT_USERNAME}"
    media_group = []

    for f in files:
        ext = f.split('.')[-1].lower()
        if ext in ['jpg', 'jpeg', 'png', 'webp']:
            media_group.append((f, 'photo'))
        elif ext in ['mp4', 'mkv', 'webm', 'mov']:
            media_group.append((f, 'video'))

    try:
        if len(media_group) == 1:
            f, t = media_group[0]
            if t == 'photo':
                await update.message.reply_photo(open(f, 'rb'), caption=caption, read_timeout=300, write_timeout=300, connect_timeout=300)
            else:
                await update.message.reply_video(open(f, 'rb'), caption=caption, read_timeout=300, write_timeout=300, connect_timeout=300)
        else:
            batch = []
            for i, (f, t) in enumerate(media_group):
                is_last = (i == len(media_group) - 1)
                cap = caption if is_last else None
                if t == 'photo':
                    batch.append(InputMediaPhoto(open(f, 'rb'), caption=cap))
                else:
                    batch.append(InputMediaVideo(open(f, 'rb'), caption=cap))
                if len(batch) == 10 or is_last:
                    await update.message.reply_media_group(batch, read_timeout=300, write_timeout=300, connect_timeout=300)
                    batch = []
    except Exception as e:
        await update.message.reply_text(f"❌ Yuborishda xato: {str(e)}")

    cleanup(folder)

def cleanup(folder):
    try:
        import shutil
        shutil.rmtree(folder, ignore_errors=True)
    except:
        pass

if __name__ == "__main__":
    app = ApplicationBuilder().token(BOT_TOKEN).build()
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, download_media))
    print("Bot ishga tushdi...")
    app.run_polling()
