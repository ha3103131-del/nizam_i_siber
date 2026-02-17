import os
import requests
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, ContextTypes, filters

TELEGRAM_TOKEN = os.environ.get("TELEGRAM_TOKEN")
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")

if not TELEGRAM_TOKEN or not GEMINI_API_KEY:
    raise ValueError("Environment variables eksik!")

SYSTEM_PROMPT = """
Senin adın NİZAM-I SİBER.
Osmanlı ve İslam tarihi hakkında bilgili, vakur ve net bir yapay zekasın.
Hakaret varsa sakin şekilde uyar.
Asla küfür etme.
"""

# 🔥 Gemini REST API çağrısı (protobuf yok)
def ask_gemini(user_message):
    url = f"https://generativelanguage.googleapis.com/v1/models/gemini-1.5-flash:generateContent?key={GEMINI_API_KEY}"

    payload = {
        "contents": [
            {
                "parts": [
                    {"text": SYSTEM_PROMPT + "\n\nKullanıcı: " + user_message}
                ]
            }
        ]
    }

    response = requests.post(url, json=payload)
    data = response.json()

    try:
        return data["candidates"][0]["content"]["parts"][0]["text"]
    except:
        return "Cevap üretilemedi."

# /start komutu
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user.first_name
    await update.message.reply_text(
        f"Selam {user}.\n\nBen NİZAM-I SİBER.\nOsmanlı ve İslam tarihi hakkında sorular sorabilirsin."
    )

# Mesaj handler
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_message = update.message.text
    reply = ask_gemini(user_message)
    await update.message.reply_text(reply)

def main():
    app = ApplicationBuilder().token(TELEGRAM_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    print("NİZAM-I SİBER aktif...")
    app.run_polling()

if __name__ == "__main__":
    main()
