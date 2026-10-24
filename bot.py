import os
import time
import urllib.parse
import threading
import requests
from flask import Flask, request, jsonify
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, WebAppInfo
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes
from telegram.error import NetworkError

server = Flask(__name__)

# السماح بالاتصال من أي منصة وتخطي قيود CORS
@server.after_request
def after_request(response):
    response.headers.add('Access-Control-Allow-Origin', '*')
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
    response.headers.add('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE,OPTIONS')
    return response

@server.route('/')
def home():
    return "Bot is running live!"

# مسار استخراج الرابط النهائي والمضمون
@server.route('/api/extract', methods=['GET'])
def extract_video():
    video_url = request.args.get('url')
    if not video_url:
        return jsonify({"success": False, "error": "No URL provided"})
    
    try:
        direct_url = None
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}

        # 1. إذا كان الرابط يخص تيك توك، نستخدم محرك tikwm المضمون 100% لتخطي الحظر
        if "tiktok.com" in video_url:
            api_url = f"https://tikwm.com/api/?url={urllib.parse.quote(video_url)}"
            response = requests.get(api_url, headers=headers, timeout=10)
            data = response.json()
            if data.get("code") == 0 and "data" in data and "play" in data["data"]:
                direct_url = data["data"]["play"]

        # 2. إذا لم يكن تيك توك أو فشلت الطريقة الأولى، نستخدم Cobalt API كبديل
        if not direct_url:
            payload = {"url": video_url, "vQuality": "720"}
            headers_cobalt = {"Accept": "application/json", "Content-Type": "application/json"}
            response = requests.post("https://api.cobalt.tools/api/json", json=payload, headers=headers_cobalt, timeout=15)
            res_data = response.json()
            if "url" in res_data:
                direct_url = res_data["url"]
            elif "picker" in res_data and len(res_data["picker"]) > 0:
                direct_url = res_data["picker"][0].get("url")
        
        if direct_url:
            return jsonify({"success": True, "download_url": direct_url})
        else:
            return jsonify({"success": False, "error": "Could not extract link"})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)})

def run_flask():
    port = int(os.environ.get("PORT", 10000))
    server.run(host="0.0.0.0", port=port)

TOKEN = "8619065741:AAEfJxid4ahp66sG2DU0X8X34W4F0iCiCfc"
MINI_APP_URL = "https://ga11trading11-bot.github.io/Downloader-video/"

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("أهلاً بك في بوت التحميل 🚀\nأرسل لي أي رابط فيديو وسأجهزه لك فوراً.")

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_url = update.message.text.strip()
    
    if not user_url.startswith(("http://", "https://")):
        await update.message.reply_text("❌ يرجى إرسال رابط فيديو صحيح.")
        return

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
