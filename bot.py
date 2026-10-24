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
        
        # استخدام Cobalt API الموثوق لتجاوز حظر السيرفرات لجميع المنصات
        payload = {
            "url": user_url,
            "vQuality": "720"
        }
        headers = {
            "Accept": "application/json",
            "Content-Type": "application/json"
        }
        
        response = requests.post("https://api.cobalt.tools/api/json", json=payload, headers=headers, timeout=15)
        res_data = response.json()
        
        if "url" in res_data:
            direct_download_url = res_data["url"]
        elif "picker" in res_data and len(res_data["picker"]) > 0:
            direct_download_url = res_data["picker"][0].get("url")

        if not direct_download_url:
            raise Exception("لم يتم العثور على رابط التحميل المباشر.")

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
