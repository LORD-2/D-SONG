from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes
from pytube import YouTube
from mutagen.easyid3 import EasyID3
from mutagen.id3 import ID3, APIC, TIT2, TPE1, TALB
from youtubesearchpython import VideosSearch
import os
import re

TOKEN = os.getenv('TELEGRAM_TOKEN')

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text(
        'أهلاً! استخدم كلمة "تحميل" متبوعًا باسم الأغنية للبحث عنها وتنزيلها.',
        reply_to_message_id=update.message.message_id
    )

def sanitize_filename(filename: str) -> str:
    # Remove or replace invalid characters
    return re.sub(r'[\\/*?:"<>|]', "", filename)

async def download(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    message_text = update.message.text
    if message_text.startswith("تحميل"):
        query = message_text[len("تحميل"):].strip()
    else:
        await update.message.reply_text(
            'يرجى استخدام كلمة "تحميل" متبوعًا باسم الأغنية.',
            reply_to_message_id=update.message.message_id
        )
        return

    if not query:
        await update.message.reply_text(
            'يرجى إدخال اسم الأغنية بعد كلمة "تحميل".',
            reply_to_message_id=update.message.message_id
        )
        return

    # Send "جاري تحميل الأغنية" message
    loading_message = await update.message.reply_text(
        'جاري تحميل الأغنية...',
        reply_to_message_id=update.message.message_id
    )

    try:
        videos_search = VideosSearch(query, limit=1)
        results = videos_search.result()
        if not results['result']:
            await update.message.reply_text(
                'لم يتم العثور على نتائج.',
                reply_to_message_id=update.message.message_id
            )
            return

        video = results['result'][0]
        video_url = video['link']

        yt = YouTube(video_url)
        audio_stream = yt.streams.filter(only_audio=True).first()

        sanitized_title = sanitize_filename(yt.title)
        file_name = audio_stream.download(filename=f"{sanitized_title}.mp3")

        # إضافة علامة ID3 الأساسية إذا لم تكن موجودة
        try:
            audio = EasyID3(file_name)
        except Exception:
            audio = ID3()
            audio.add(TIT2(encoding=3, text=sanitized_title))
            audio.add(TPE1(encoding=3, text='BY LORD'))
            audio.save(file_name)

        # تعديل البيانات الوصفية للملف الصوتي
        audio = EasyID3(file_name)
        audio['artist'] = 'BY LORD'
        audio.save()

        await update.message.reply_audio(
            audio=open(file_name, 'rb'),
            reply_to_message_id=update.message.message_id
        )
        os.remove(file_name)
    except Exception as e:
        await update.message.reply_text(
            f'حدث خطأ أثناء التحميل: {e}',
            reply_to_message_id=update.message.message_id
        )
    finally:
        # Delete "جاري تحميل الأغنية" message
        await context.bot.delete_message(
            chat_id=update.message.chat_id,
            message_id=loading_message.message_id
        )

def main() -> None:
    application = ApplicationBuilder().token(TOKEN).build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.TEXT & filters.Regex(r'^تحميل'), download))

    application.run_polling()

if __name__ == '__main__':
    main()
