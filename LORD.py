from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes
import yt_dlp as youtube_dl
import os

TOKEN = os.getenv('TELEGRAM_TOKEN')

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text('أهلاً! استخدم كلمة "تحميل" متبوعًا باسم الأغنية للبحث عنها وتنزيلها.')

async def download(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    message_text = update.message.text
    if message_text.startswith("تحميل"):
        query = message_text[len("تحميل"):].strip()
    else:
        await update.message.reply_text('يرجى استخدام كلمة "تحميل" متبوعًا باسم الأغنية.')
        return

    if not query:
        await update.message.reply_text('يرجى إدخال اسم الأغنية بعد كلمة "تحميل".')
        return

    ydl_opts = {
        'format': 'bestaudio/best',
        'outtmpl': '%(title)s.%(ext)s',
        'quiet': True,
        'noplaylist': True,
    }

    try:
        with youtube_dl.YoutubeDL(ydl_opts) as ydl:
            info_dict = ydl.extract_info(f"ytsearch:{query}", download=True)
            video = info_dict['entries'][0]
            file_name = ydl.prepare_filename(video)
        
        await update.message.reply_audio(audio=open(file_name, 'rb'))
        os.remove(file_name)
    except Exception as e:
        await update.message.reply_text(f'حدث خطأ أثناء التحميل: {e}')

def main() -> None:
    application = ApplicationBuilder().token(TOKEN).build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.TEXT & filters.Regex(r'^تحميل'), download))

    application.run_polling()

if __name__ == '__main__':
    main()
