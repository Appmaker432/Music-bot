import os
import asyncio
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
import yt_dlp


TOKEN = '8733817561:AAH3u0j0fNgP3dkGPuVAX6ziE9YPaBgcH1A'

def download_song(query):
    ydl_opts = {
        'format': 'bestaudio/best',
        'default_search': 'ytsearch',
        'noplaylist': True,
        'outtmpl': 'song.%(ext)s',
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192',
        }],
    }
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(query, download=True)
        video_info = info['entries'][0]
        return "song.mp3", video_info['title']

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("මචං, සින්දුවක නම එවන්න. මම එවන්නම්! 🎶")

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.message.text
    msg = await update.message.reply_text("සින්දුව හොයනවා... ⏳")
    try:
        file_path, title = download_song(query)
        await update.message.reply_audio(audio=open(file_path, 'rb'), title=title)
        await msg.delete()
        os.remove(file_path)
    except Exception as e:
        await msg.edit_text(f"අවුලක් වුණා මචං! ❌")

if __name__ == '__main__':
    app = Application.builder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    app.run_polling()
