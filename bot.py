import os
import time
import urllib.parse
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, WebAppInfo
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes
from telegram.error import NetworkError
from yt_dlp import YoutubeDL

# توكن البوت الخاص بك
TOKEN = "8619065741:AAEfJxid4ahp66sG2DU0X8X34W4F0iCiCfc"

# رابط الـ Mini App الخاص بك الذي تم استخراجه من GitHub Pages
MINI_APP_URL = "https://ga11trading11-bot.github.io/Downloader-video/"

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    welcome_msg = (
        "أهلاً بك في بوت تحميل المقاطع المجاني! 🚀\n\n"
        "أرسل لي أي رابط فيديو من (تيك توك، سناب شات، إنستغرام، أو X) وسأقوم بتجهيزه لك فوراً."
    )
    await update.message.reply_text(welcome_msg)

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_url = update.message.text.strip()
    
    # التأكد من أن الرسالة تحتوي على رابط
    if not user_url.startswith(("http://", "https://")):
        await update.message.reply_text("❌ يرجى إرسال رابط فيديو صحيح.")
        return

    status_msg = await update.message.reply_text("⏳ جاري استخراج رابط التحميل المباشر...")

    try:
        # استخراج رابط التحميل المباشر للمقطع باستعمال yt-dlp دون تنزيله على السيرفر
        ydl_opts = {
            'format': 'best',
            'quiet': True,
            'no_warnings': True,
        }
        with YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(user_url, download=False)
            direct_download_url = info.get('url', user_url)

        # تشفير الرابط لتمريره داخل رابط الـ Mini App
        encoded_video_url = urllib.parse.quote(direct_download_url, safe='')
        full_miniapp_link = f"{MINI_APP_URL}?video_url={encoded_video_url}"

        # بناء زر الـ Mini App التفاعلي
        keyboard = [
            [
                InlineKeyboardButton(
                    text="📥 اضغط هنا لتجهيز وتحميل المقطع",
                    web_app=WebAppInfo(url=full_miniapp_link)
                )
            ]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)

        await status_msg.delete()
        await update.message.reply_text(
            "✅ تم تجهيز الفيديو بنجاح!\nاضغط على الزر أدناه للتحميل المباشر:",
            reply_markup=reply_markup
        )

    except Exception as e:
        await status_msg.edit_text("❌ تعذر استخراج هذا الرابط. تأكد من أن الحساب عام وليس خاصاً.")

if __name__ == '__main__':
    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    
    print("البوت يعمل مع نظام إعادة الاتصال التلقائي...")
    
    # حلقة تكرار لمنع توقف البوت نهائياً عند حدوث خطأ 503 أو انقطاع الشبكة
    while True:
        try:
            app.run_polling(drop_pending_updates=True)
        except NetworkError as e:
            print(f"⚠️ حدث خطأ في الشبكة أو البروكسي (503): {e}")
            print("🔄 جاري إعادة المحاولة خلال 10 ثوانٍ...")
            time.sleep(10)
        except Exception as e:
            print(f"⚠️ حدث خطأ غير متوقع: {e}")
            print("🔄 جاري إعادة المحاولة خلال 15 ثانية...")
            time.sleep(15)
