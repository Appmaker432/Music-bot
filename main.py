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
        f"ආයුබෝවන් {user_name} මචං! 🇱🇰\n\n"
        "මම ඔයාගේ සින්දු ඩවුන්ලෝඩර් බොට්. වැඩේ ලේසියි:\n"
        "1. මට YouTube Link එකක් එවන්න.\n"
        "2. ඔයාට ඕන Quality එක තෝරන්න.\n"
        "3. සින්දුව බාගන්න! 🎶"
    )
    await update.message.reply_text(welcome_text)

# ලින්ක් එක ආවම Quality තෝරන්න Button දෙන එක
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    url = update.message.text
    if "youtube.com" not in url and "youtu.be" not in url:
        await update.message.reply_text("මචං, කරුණාකරලා වලංගු YouTube Link එකක් එවන්න! ❌")
        return

    msg = await update.message.reply_text("සින්දුවේ විස්තර පරීක්ෂා කරමින් පවතිනවා... ⏳")

    keyboard = [
        [
            InlineKeyboardButton("128 kbps", callback_data=f"128|{url}"),
            InlineKeyboardButton("192 kbps", callback_data=f"192|{url}"),
            InlineKeyboardButton("320 kbps", callback_data=f"320|{url}"),
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await msg.edit_text("ඔයාට සින්දුව බාගන්න ඕන Quality එක තෝරන්න: 👇", reply_markup=reply_markup)

# Button එකක් එබුවම සින්දුව Download කරන එක
async def button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    quality, url = query.data.split("|")
    await query.edit_message_text(f"නියමයි! {quality}kbps Quality එකෙන් සින්දුව බාගන්නවා... ⏳")

    file_path = f"song_{quality}.mp3"
    
    ydl_opts = {
        'format': 'bestaudio/best',
        'outtmpl': 'song_%(id)s.%(ext)s',
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': quality,
        }],
        'quiet': True,
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            temp_file = ydl.prepare_filename(info).replace(info['ext'], 'mp3')
            title = info.get('title', 'Music')

            # සින්දුව ටෙලිග්‍රෑම් එකට යැවීම
            await context.bot.send_audio(
                chat_id=query.message.chat_id,
                audio=open(temp_file, 'rb'),
                title=title,
                caption=f"✅ {title}\n🎧 Quality: {quality}kbps\n\nBy @MusicBot"
            )
            
            # File එක delete කිරීම
            os.remove(temp_file)
            await query.message.delete()
            
    except Exception as e:
        await query.message.reply_text(f"අයියෝ වැඩේ අවුල් වුණා මචං! ❌\nError: {str(e)[:50]}")

if __name__ == '__main__':
    app = Application.builder().token(TOKEN).build()
    
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    app.add_handler(CallbackQueryHandler(button))
    
    print("Bot is running...")
    app.run_polling()
