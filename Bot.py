import os
import glob
import asyncio
import yt_dlp
import requests
import re
import json
from telegram import Update, InputMediaPhoto, InputMediaVideo
from telegram.ext import ApplicationBuilder, MessageHandler, CommandHandler, filters, ContextTypes

BOT_TOKEN = "8327848961:AAHJR8c9LMbKmiMGULn4jT4YbVkXzKexr0U"
BOT_USERNAME = "@YUKLAVCHI_10_BOT"
ADMIN_ID =699337665   # Bu yerga o'z Telegram ID ingizni yozing

def load_users():
    try:
        with open('users.json', 'r') as f:
            return set(json.load(f))
    except:
        return set()

def save_users(users):
    with open('users.json', 'w') as f:
        json.dump(list(users), f)

users = load_users()

async def stats(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message.chat_id != ADMIN_ID:
        return
    await update.message.reply_text(f"👥 Jami foydalanuvchilar: {len(users)} ta")

def download_instagram_photos(url, folder):
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 16_0 like Mac OS X) AppleWebKit/605.1.15',
            'Accept': 'text/html,application/xhtml+xml',
        }
        r = requests.get(url, headers=headers)
        matches = re.findall(r'"display_url":"(https://[^"]+)"', r.text)
        if not matches:
            matches = re.findall(r'content="(https://[^"]+\.jpg[^"]*)"', r.text)
        files = []
        for i, img_url in enumerate(matches[:10]):
            img_url = img_url.replace('\\u0026', '&')
            img_r = requests.get(img_url, headers=headers)
            path = f"{folder}/photo_{i}.jpg"
            with open(path, 'wb') as f:
                f.write(img_r.content)
            files.append(path)
        return files
    except:
        return []

async def download_media(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    users.add(user_id)
    save_users(users)

    url = update.message.text.strip()
    if not url.startswith("http"):
        await update.message.reply_text("❌ Iltimos, to'g'ri havola yuboring!")
        return

    await update.message.reply_text("⏳ Yuklanmoqda, kuting...")

    folder = f"downloads/{update.message.message_id}"
    os.makedirs(folder, exist_ok=True)

    files = []

    if "instagram.com/p/" in url:
        loop = asyncio.get_event_loop()
        photo_files = await loop.run_in_executor(
            None, lambda: download_instagram_photos(url, folder)
        )
        files = [(f, 'photo') for f in photo_files]

    if not files:
        ydl_opts = {
            'outtmpl': f'{folder}/%(title)s.%(ext)s',
            'quiet': True,
            'noplaylist': True,
            'format': 'best[filesize<50M]/best',
        }
        if "instagram.com" in url:
            ydl_opts['username'] = 'lion.7795326'
            ydl_opts['password'] = 'Dusmamatov&19'

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
        raw_files = sorted([
            f for f in glob.glob(f'{folder}/*')
            if os.path.isfile(f) and not f.endswith('.part')
            and f.split('.')[-1].lower() in ['mp4', 'mkv', 'webm', 'mov', 'jpg', 'jpeg', 'png']
        ], key=os.path.getctime)
        files = [(f, 'photo' if f.split('.')[-1].lower() in ['jpg','jpeg','png'] else 'video') for f in raw_files]

    if not files:
        await update.message.reply_text("❌ Fayl topilmadi!")
        cleanup(folder)
        return

    caption = f"✅ Bizdan foydalanganingiz uchun xursandmiz!\n👉 {BOT_USERNAME}"

    try:
        for f, t in files:
            if t == 'photo':
                await update.message.reply_photo(open(f, 'rb'), caption=caption,
                    read_timeout=300, write_timeout=300, connect_timeout=300)
            else:
                await update.message.reply_video(open(f, 'rb'), caption=caption,
                    read_timeout=300, write_timeout=300, connect_timeout=300)
    except Exception as e:
        await update.message.reply_text(f"❌ Yuborishda xato: {str(e)}")

    cleanup(folder)

def cleanup(folder):
    import shutil
    shutil.rmtree(folder, ignore_errors=True)

if __name__ == "__main__":
    app = ApplicationBuilder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("stats", stats))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, download_media))
    print("Bot ishga tushdi...")
    app.run_polling()
