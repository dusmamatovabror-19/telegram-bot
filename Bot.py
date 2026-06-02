import os
import asyncio
import aiohttp
import aiofiles
from telegram import Update, InputMediaPhoto, InputMediaVideo
from telegram.ext import ApplicationBuilder, MessageHandler, filters, ContextTypes

BOT_TOKEN = "8327848961:AAHW-NYy8PuvjcDs-QxhL0A5IgDJsn5T4sQ"
BOT_USERNAME = "@YUKLAVCHI_10_BOT"
RAPIDAPI_KEY = "66e7939672msh9215a6bb7e4538bp17c2d2jsn80269ebf2f39"
RAPIDAPI_HOST = "instagram-downloader-scraper-reels-igtv-posts-stories.p.rapidapi.com"

async def get_instagram_media(url):
    headers = {
        "x-rapidapi-key": RAPIDAPI_KEY,
        "x-rapidapi-host": RAPIDAPI_HOST,
        "Content-Type": "application/json"
    }
    api_url = f"https://{RAPIDAPI_HOST}/fetch?url={url}"
    async with aiohttp.ClientSession() as session:
        async with session.get(api_url, headers=headers) as resp:
            return await resp.json()

async def download_file(url, path):
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as resp:
            async with aiofiles.open(path, 'wb') as f:
                await f.write(await resp.read())

async def download_media(update: Update, context: ContextTypes.DEFAULT_TYPE):
    url = update.message.text.strip()
    if not url.startswith("http"):
        await update.message.reply_text("❌ Iltimos, to'g'ri havola yuboring!")
        return

    await update.message.reply_text("⏳ Yuklanmoqda, kuting...")

    folder = f"downloads/post_{update.message.message_id}"
    os.makedirs(folder, exist_ok=True)

    try:
        # Instagram uchun RapidAPI
        if "instagram.com" in url:
            data = await get_instagram_media(url)
            media_urls = []

            # Javobdan media URL larini olish
            if isinstance(data, dict):
                if "media" in data:
                    for item in data["media"]:
                        if "url" in item:
                            media_urls.append((item["url"], item.get("type", "video")))
                elif "url" in data:
                    media_urls.append((data["url"], "video"))
                elif "data" in data:
                    d = data["data"]
                    if isinstance(d, list):
                        for item in d:
                            if "url" in item:
                                media_urls.append((item["url"], item.get("type", "video")))
                    elif isinstance(d, dict) and "url" in d:
                        media_urls.append((d["url"], "video"))

            if not media_urls:
                await update.message.reply_text(f"❌ Media topilmadi! API javobi: {str(data)[:200]}")
                return

            # Fayllarni yuklab olish
            files = []
            for i, (media_url, media_type) in enumerate(media_urls):
                ext = "mp4" if "video" in media_type else "jpg"
                path = f"{folder}/file_{i}.{ext}"
                await download_file(media_url, path)
                files.append((path, media_type))

        else:
            # Boshqa saytlar uchun yt-dlp
            import yt_dlp
            import glob
            ydl_opts = {
                'outtmpl': f'{folder}/file_%(autonumber)s.%(ext)s',
                'quiet': True,
                'noplaylist': True,
                'format': 'best/bestvideo+bestaudio',
            }
            loop = asyncio.get_event_loop()
            await loop.run_in_executor(
                None, lambda: yt_dlp.YoutubeDL(ydl_opts).download([url])
            )
            await asyncio.sleep(1)
            raw_files = sorted([
                f for f in glob.glob(f'{folder}/*')
                if os.path.isfile(f) and not f.endswith('.part')
                and f.split('.')[-1].lower() in ['jpg','jpeg','png','mp4','mkv','webm','mov']
            ], key=os.path.getctime)
            files = [(f, "photo" if f.split('.')[-1].lower() in ['jpg','jpeg','png'] else "video") for f in raw_files]

    except Exception as e:
        await update.message.reply_text(f"❌ Xatolik: {str(e)}")
        cleanup(folder)
        return

    if not files:
        await update.message.reply_text("❌ Fayl topilmadi!")
        cleanup(folder)
        return

    caption = f"✅ Bizdan foydalanganingiz uchun xursandmiz!\n👉 {BOT_USERNAME}"

    try:
        if len(files) == 1:
            path, mtype = files[0]
            if "video" not in mtype:
                await update.message.reply_photo(open(path, 'rb'), caption=caption,
                    read_timeout=300, write_timeout=300, connect_timeout=300)
            else:
                await update.message.reply_video(open(path, 'rb'), caption=caption,
                    read_timeout=300, write_timeout=300, connect_timeout=300)
        else:
            batch = []
            for i, (path, mtype) in enumerate(files):
                cap = caption if i == len(files) - 1 else None
                if "video" not in mtype:
                    batch.append(InputMediaPhoto(open(path, 'rb'), caption=cap))
                else:
                    batch.append(InputMediaVideo(open(path, 'rb'), caption=cap))
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
