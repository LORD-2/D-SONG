from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes
from mutagen.easyid3 import EasyID3
from youtube_search import YoutubeSearch
import yt_dlp
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
        # Search for the video on YouTube
        results = YoutubeSearch(query, max_results=1).to_dict()
        if not results:
            await update.message.reply_text(
                'لم يتم العثور على نتائج.',
                reply_to_message_id=update.message.message_id
            )
            return

        video = results[0]
        video_url = f"https://www.youtube.com{video['url_suffix']}"

        ydl_opts = {
            'format': 'bestaudio/best',
            'outtmpl': '%(title)s.%(ext)s',
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '192',
            }],
        }

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info_dict = ydl.extract_info(video_url, download=True)
            file_name = ydl.prepare_filename(info_dict).replace('.webm', '.mp3').replace('.m4a', '.mp3')

        sanitized_title = sanitize_filename(info_dict['title'])
        os.rename(file_name, f"{sanitized_title}.mp3")
        file_name = f"{sanitized_title}.mp3"

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
