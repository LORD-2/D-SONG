from telegram import Update
from telegram.ext import Updater, CommandHandler, CallbackContext
import youtube_dl
import os

TOKEN = os.getenv('TELEGRAM_TOKEN')

def start(update: Update, context: CallbackContext) -> None:
    update.message.reply_text('أهلاً! استخدم الأمر /تحميل متبوعًا باسم الأغنية للبحث عنها وتنزيلها.')

def download(update: Update, context: CallbackContext) -> None:
    query = ' '.join(context.args)
    if not query:
        update.message.reply_text('يرجى إدخال اسم الأغنية بعد الأمر /تحميل.')
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

    update.message.reply_audio(audio=open(file_name, 'rb'))
    os.remove(file_name)

def main() -> None:
    updater = Updater(TOKEN, use_context=True)
    dispatcher = updater.dispatcher

    dispatcher.add_handler(CommandHandler("start", start))
    dispatcher.add_handler(CommandHandler("تحميل", download))

    updater.start_polling()
    updater.idle()

if __name__ == '__main__':
    main()