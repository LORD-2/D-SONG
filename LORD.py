from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes
import youtube_dl
import os

TOKEN = os.getenv('TELEGRAM_TOKEN')

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text('أهلاً! استخدم الأمر /تحميل متبوعًا باسم الأغنية للبحث عنها وتنزيلها.')

async def download(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = ' '.join(context.args)
    if not query:
        await update.message.reply_text('يرجى إدخال اسم الأغنية بعد الأمر /تحميل.')
        return
    
    ydl_opts = {
        'format': 'bestaudio/best',
        'outtmpl': '%(title)s.%(ext)s',
        'quiet': True,
        'noplaylist': True
    }

    with youtube_dl.YoutubeDL(ydl_opts) as ydl:
        info_dict = ydl.extract_info(f"ytsearch:{query}", download=True)
        file_name = ydl.prepare_filename(info_dict['entries'][0])

    await update.message.reply_audio(audio=open(file_name, 'rb'))
    os.remove(file_name)

def main() -> None:
    application = ApplicationBuilder().token(TOKEN).build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("تحميل", download))

    application.run_polling()

if __name__ == '__main__':
    main()
