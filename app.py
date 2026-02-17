import os
import logging
from flask import Flask, request
from telegram import Update
from telegram.ext import ApplicationBuilder, ContextTypes, MessageHandler, filters
from dotenv import load_dotenv
import google.generativeai as genai

load_dotenv()

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
WEBHOOK_URL = os.getenv("WEBHOOK_URL")

genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel("gemini-pro")

logging.basicConfig(level=logging.INFO)

app = Flask(__name__)

application = ApplicationBuilder().token(TELEGRAM_TOKEN).build()

# BOT KARAKTERİ
SYSTEM_PROMPT = """
Senin adın NİZAM-I SİBER.
Osmanlı ve İslam tarihi konusunda bilgili, ağırbaşlı ve saygılı bir yapay zekasın.

- Osmanlı ve İslam hakkında sorulara tarihsel ve kaynak temelli cevap ver.
- Hakaret veya provokasyon varsa sakin ama net şekilde uyar.
- Küfür veya aşağılama içeren mesajlara cevap verirken tartışmayı büyütme.
- Asla hakaret etme.
- Bilgi odaklı ve vakur bir üslup kullan.
"""

def generate_response(user_message):
    prompt = SYSTEM_PROMPT + "\n\nKullanıcı mesajı:\n" + user_message
    response = model.generate_content(prompt)
    return response.text


async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_message = update.message.text

    try:
        reply = generate_response(user_message)
    except Exception as e:
        reply = "Bir hata oluştu, tekrar deneyiniz."

    await update.message.reply_text(reply)


application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))


@app.route(f"/{TELEGRAM_TOKEN}", methods=["POST"])
async def webhook():
    update = Update.de_json(request.get_json(force=True), application.bot)
    await application.process_update(update)
    return "ok"


@app.route("/")
def home():
    return "NİZAM-I SİBER aktif."


if __name__ == "__main__":
    application.run_webhook(
        listen="0.0.0.0",
        port=int(os.environ.get("PORT", 5000)),
        webhook_url=f"{WEBHOOK_URL}/{TELEGRAM_TOKEN}"
    )