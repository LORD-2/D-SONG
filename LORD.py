from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes
from pytube import YouTube, Search
import os

TOKEN = os.getenv('TELEGRAM_TOKEN')

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text('أهلاً! استخدم الأمر /تحميل متبوعًا باسم الأغنية للبحث عنها وتنزيلها.')

async def download(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = ' '.join(context.args)
    if not query:
        await update.message.reply_text('يرجى إدخال اسم الأغنية بعد الأمر /تحميل.')
        return

    try:
        # البحث عن الفيديو باستخدام pytube
        search = Search(query)
        video = search.results[0]
        yt = YouTube(video.watch_url)
        
        # تنزيل الفيديو كملف صوتي
        stream = yt.streams.filter(only_audio=True).first()
        output_file = stream.download()
        
        # إرسال الملف الصوتي عبر تليجرام
        await update.message.reply_audio(audio=open(output_file, 'rb'))
        os.remove(output_file)
    except Exception as e:
        await update.message.reply_text(f'حدث خطأ أثناء التحميل: {e}')

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    message_text = update.message.text
    if message_text.startswith("/تحميل"):
        context.args = message_text.split()[1:]
        await download(update, context)

def main() -> None:
    application = ApplicationBuilder().token(TOKEN).build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    application.run_polling()

if __name__ == '__main__':
    main()
