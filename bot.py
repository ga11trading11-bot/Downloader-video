import os
import time
import urllib.parse
import threading
import requests
from flask import Flask
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, WebAppInfo
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes
from telegram.error import NetworkError

# إعداد خادم ويب بسيط لإرضاء متطلبات Render المجانية
server = Flask(__name__)

@server.route('/')
def home():
    return "Bot is running live!"

def run_flask():
    port = int(os.environ.get("PORT", 10000))
    server.run(host="0.0.0.0", port=port)

# توكن البوت الخاص بك
TOKEN = "8619065741:AAEfJxid4ahp66sG2DU0X8X34W4F0iCiCfc"

# رابط الـ Mini App الخاص بك
MINI_APP_URL = "https://ga11trading11-bot.github.io/Downloader-video/"

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    welcome_msg = (
        "أهلاً بك في بوت تحميل المقاطع المجاني! 🚀\n\n"
        "أرسل لي أي رابط فيديو من (تيك توك، سناب شات، إنستغرام، أو X) وسأقوم بتجهيزه لك فوراً."
    )
    await update.message.reply_text(welcome_msg)

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_url = update.message.text.strip()
    
    if not user_url.startswith(("http://", "https://")):
        await update.message.reply_text("❌ يرجى إرسال رابط فيديو صحيح.")
        return

    status_msg = await update.message.reply_text("⏳ جاري استخراج رابط التحميل المباشر...")

    try:
        direct_download_url = None

        # 1. محاولة استخدام خدمة بديلة سريعة لجلب رابط تيك توك وتخطي الحظر
        if "tiktok.com" in user_url:
            api_url = f"https://tikwm.com/api/?url={urllib.parse.quote(user_url)}"
            response = requests.get(api_url, timeout=10)
            data = response.json()
            if data.get("code") == 0:
                direct_download_url = data["data"]["play"]

        # 2. إذا لم يكن تيك توك أو فشلت الطريقة، نستخدم الطريقة العامة
        if not direct_download_url:
            from yt_dlp import YoutubeDL
            ydl_opts = {
                'format': 'best',
                'quiet': True,
                'no_warnings': True,
                'nocheckcertificate': True,
                'geo_bypass': True,
                'user_agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36',
            }
            with YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(user_url, download=False)
                direct_download_url = info.get('url', user_url)

        if not direct_download_url:
            raise Exception("لم يتم العثور على رابط التحميل المباشر.")

        encoded_video_url = urllib.parse.quote(direct_download_url, safe='')
        full_miniapp_link = f"{MINI_APP_URL}?video_url={encoded_video_url}"

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
        error_text = str(e)
        print(f"خطأ تفصيلي: {error_text}")
        await status_msg.edit_text("❌ تعذر استخراج هذا الرابط. تأكد من أن الرابط مباشر وأن الحساب عام.")

def main():
    t = threading.Thread(target=run_flask)
    t.start()

    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    
    print("البوت يعمل بنجاح على Render...")
    
    while True:
        try:
            app.run_polling(drop_pending_updates=True)
        except NetworkError as e:
            print(f"⚠️ خطأ شبكة: {e}")
            time.sleep(10)
        except Exception as e:
            print(f"⚠️ خطأ عام: {e}")
            time.sleep(15)

if __name__ == '__main__':
    main()
