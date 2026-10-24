import os
import time
import urllib.parse
import threading
from flask import Flask
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, WebAppInfo
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes
from telegram.error import NetworkError

server = Flask(__name__)

@server.route('/')
def home():
    return "Bot is running live!"

def run_flask():
    port = int(os.environ.get("PORT", 10000))
    server.run(host="0.0.0.0", port=port)

TOKEN = "8619065741:AAEfJxid4ahp66sG2DU0X8X34W4F0iCiCfc"
MINI_APP_URL = "https://ga11trading11-bot.github.io/Downloader-video/" # رابط موقعك على GitHub Pages

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("أهلاً بك في بوت التحميل 🚀\nأرسل لي أي رابط فيديو وسأجهزه لك فوراً.")

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_url = update.message.text.strip()
    
    if not user_url.startswith(("http://", "https://")):
        await update.message.reply_text("❌ يرجى إرسال رابط فيديو صحيح.")
        return

    # تمرير الرابط الأصلي للـ Mini App عبر الباراميتر
    encoded_url = urllib.parse.quote(user_url, safe='')
    full_miniapp_link = f"{MINI_APP_URL}?url={encoded_url}"

    keyboard = [
        [
            InlineKeyboardButton(
                text="📥 اضغط هنا للتحميل ومشاهدة الفيديو",
                web_app=WebAppInfo(url=full_miniapp_link)
            )
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await update.message.reply_text(
        "✅ تم تجهيز رابطك بنجاح!\nاضغط على الزر أدناه للتحميل المباشر:",
        reply_markup=reply_markup
    )

def main():
    t = threading.Thread(target=run_flask)
    t.start()

    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    
    while True:
        try:
            app.run_polling(drop_pending_updates=True)
        except NetworkError:
            time.sleep(10)
        except Exception:
            time.sleep(15)

if __name__ == '__main__':
    main()
