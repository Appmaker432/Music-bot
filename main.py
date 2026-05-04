import os
import yt_dlp
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, filters, CallbackQueryHandler, ContextTypes

# Bot Token එක
TOKEN = '8733817561:AAH3u0j0fNgP3dkGPuVAX6ziE9YPaBgcH1A'

# Welcome Message
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_name = update.effective_user.first_name
    welcome_text = (
        f"ආයුබෝවන් {user_name} මචං! 🎶\n\n"
        "මම සින්දු ඩවුන්ලෝඩර් බොට්. වැඩේ ලේසියි:\n"
        "1. සින්දුවේ නම හරි YouTube Link එක හරි එවන්න.\n"
        "2. Quality එක තෝරන්න.\n"
        "3. සින්දුව බාගන්න! ✅"
    )
    await update.message.reply_text(welcome_text)

# සින්දුව හෝ ලින්ක් එක ආවම Quality තෝරන්න Button දෙන එක
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.message.text
    msg = await update.message.reply_text("සින්දුවේ විස්තර පරීක්ෂා කරමින් පවතිනවා... ⏳")

    keyboard = [
        [
            InlineKeyboardButton("128 kbps", callback_data=f"128|{query}"),
            InlineKeyboardButton("192 kbps", callback_data=f"192|{query}"),
            InlineKeyboardButton("320 kbps", callback_data=f"320|{query}"),
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await msg.edit_text("ඔයාට සින්දුව බාගන්න ඕන Quality එක තෝරන්න: 👇", reply_markup=reply_markup)

# Button එකක් එබුවම සින්දුව Download කරන එක
async def button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    quality, search_query = query.data.split("|")
    await query.edit_message_text(f"නියමයි! {quality}kbps Quality එකෙන් සින්දුව සකස් කරනවා... ⏳")

    # YouTube Bot detection මගහරවා ගන්න Settings
    ydl_opts = {
        'format': 'bestaudio/best',
        'default_search': 'ytsearch',
        'outtmpl': 'song_%(id)s.%(ext)s',
        'noplaylist': True,
        'quiet': True,
        'no_warnings': True,
        'nocheckcertificate': True,
        'addheader': [
            'User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36'
        ],
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': quality,
        }],
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(search_query, download=True)
            if 'entries' in info:
                video_info = info['entries'][0]
            else:
                video_info = info
                
            temp_file = ydl.prepare_filename(video_info).replace(video_info['ext'], 'mp3')
            title = video_info.get('title', 'Music')

            await context.bot.send_audio(
                chat_id=query.message.chat_id,
                audio=open(temp_file, 'rb'),
                title=title,
                caption=f"🎧 **{title}**\n✅ Quality: {quality}kbps"
            )
            
            if os.path.exists(temp_file):
                os.remove(temp_file)
            await query.message.delete()
            
    except Exception as e:
        await query.message.reply_text(f"වැඩේ අවුල් වුණා මචං! ❌\nError: {str(e)[:100]}")

if __name__ == '__main__':
    app = Application.builder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    app.add_handler(CallbackQueryHandler(button))
    print("Bot is starting...")
    app.run_polling()
