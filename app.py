import os
import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, ContextTypes, CommandHandler, MessageHandler, filters, CallbackQueryHandler
import google.generativeai as genai
from flask import Flask
from threading import Thread

# --- AYARLAR (BURALARI KENDİ BİLGİLERİNLE DOLDUR) ---
TELEGRAM_TOKEN = "8256760343:AAF4WtDfdkfd9PQbSud0ALitr65_aFlpZxw"
GEMINI_API_KEY = "AIzaSyABH27p1wiH87x2b7vz1bjLGp97TzphRbM"

# --- RENDER İÇİN SAHTE WEB SUNUCUSU (Keep Alive) ---
app = Flask(__name__)

@app.route('/')
def home():
    return "Bot calisiyor! Nizam-i Siber gorev basinda."

def run_flask():
    # Render otomatik olarak PORT environment variable'ını atar
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)

def keep_alive():
    t = Thread(target=run_flask)
    t.start()
# ---------------------------------------------------

# Gemini API Kurulumu
genai.configure(api_key=GEMINI_API_KEY)

# Model Ayarları
SYSTEM_INSTRUCTION = """
Sen Hasan Aslan'sın. Lise öğrencisi, siber güvenlik ve yazılım tutkunu, aynı zamanda İslam ve Osmanlı tarihine derin ilgi duyan genç bir Müslümansın.
Adıyaman'da yaşıyorsun.
Konuşma tarzın:
- Samimi, saygılı ve genç bir üslup kullan.
- Bilgi verirken net ol.
- Dini veya tarihi konularda hassas ve bilgili davran.
"""

model = genai.GenerativeModel(
    model_name="gemini-1.5-flash",
    system_instruction=SYSTEM_INSTRUCTION
)

user_histories = {}

def get_chat_session(user_id):
    if user_id not in user_histories:
        user_histories[user_id] = []
    return user_histories[user_id]

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_first_name = update.effective_user.first_name
    welcome_text = (
        f"👋 **Selamun Aleyküm {user_first_name}! Ben Hasan.**\n\n"
        "Ben Hasan Aslan'ın dijital ikiziyim. Hadi sohbete başlayalım!"
    )
    keyboard = [
        [InlineKeyboardButton("🛡️ Siber Güvenlik", callback_data='konu_siber')],
        [InlineKeyboardButton("🧹 Hafızayı Temizle", callback_data='clear_memory')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text(welcome_text, reply_markup=reply_markup, parse_mode='Markdown')

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    user_input = update.message.text
    await context.bot.send_chat_action(chat_id=update.effective_chat.id, action='typing')
    history = get_chat_session(user_id)
    chat = model.start_chat(history=history)
    try:
        response = chat.send_message(user_input)
        user_histories[user_id] = chat.history
        await update.message.reply_text(response.text)
    except Exception as e:
        await update.message.reply_text("⚠️ Bir hata oluştu.")
        print(f"Hata: {e}")

async def button_click(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    if query.data == 'clear_memory':
        user_histories[query.from_user.id] = []
        await query.edit_message_text(text="🧹 Hafıza temizlendi.")
    elif query.data == 'konu_siber':
        await query.message.reply_text("Siber güvenlik mi? En sevdiğim konu!")

if __name__ == '__main__':
    # ÖNCE web sunucusunu başlatıyoruz
    keep_alive()
    
    # SONRA botu başlatıyoruz
    application = ApplicationBuilder().token(TELEGRAM_TOKEN).build()
    application.add_handler(CommandHandler('start', start))
    application.add_handler(CallbackQueryHandler(button_click))
    application.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), handle_message))
    
    print("Bot baslatiliyor...")
    application.run_polling()

