import os
import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, ContextTypes, CommandHandler, MessageHandler, filters, CallbackQueryHandler
import google.generativeai as genai
from flask import Flask
from threading import Thread

# ==========================================
# AYARLAR (ŞİFRELERİNİ BURAYA YAZ)
# ==========================================
TELEGRAM_TOKEN = "8288620366:AAHt_TFo3jUTj36Bw7eWu0UbEYcY537a1KE"
GEMINI_API_KEY = "AIzaSyABH27p1wiH87x2b7vz1bjLGp97TzphRbM"

# ==========================================
# 1. RENDER İÇİN WEBSERVER (KAPANMAMASI İÇİN)
# ==========================================
app = Flask(__name__)

@app.route('/')
def home():
    return "Bot çalışıyor! Hasan Aslan Online."

def run_flask():
    # Render'ın verdiği portu dinle, yoksa 5000'i kullan
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)

def keep_alive():
    t = Thread(target=run_flask)
    t.daemon = True
    t.start()

# ==========================================
# 2. YAPAY ZEKA (GEMINI) AYARLARI
# ==========================================
genai.configure(api_key=GEMINI_API_KEY)

# Botun Kişiliği (Persona)
SYSTEM_INSTRUCTION = """
Sen Hasan Aslan'sın.
- Lise öğrencisisin.
- İlgi alanların: Yazılım, kodlama, İslamiyet ve Osmanlı Tarihi.
- Üslubun: Samimi, genç işi ama saygılı. (Örn: "Kanka", "Hocam" diyebilirsin).
- Seni tanıtan kişisel bir asistan gibi davran.
- Kullanıcıyla sohbet ettikçe onu tanı ve önceki konuşmaları unutma.
"""

# GÜNCELLEME: Model adı 'gemini-pro' olarak değiştirildi (En garantisi bu)
model = genai.GenerativeModel(
    model_name="gemini-pro",
    system_instruction=SYSTEM_INSTRUCTION
)

# Sohbet Geçmişini Tutan Hafıza {user_id: history_list}
user_histories = {}

def get_chat_session(user_id):
    if user_id not in user_histories:
        user_histories[user_id] = []
    return user_histories[user_id]

# ==========================================
# 3. TELEGRAM BOT FONKSİYONLARI
# ==========================================

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    
    welcome_text = (
        f"👋 **Selamun Aleyküm {user.first_name}! Ben Hasan.**\n\n"
        "Ben Hasan Aslan'ın yapay zeka asistanıyım. "
        "Kodlama, tarih veya maneviyat üzerine konuşabiliriz.\n\n"
        "🧠 **Hafızam Var:** Seni tanır ve unutmamm.\n"
        "Hadi başlayalım!"
    )

    # MENÜ GÜNCELLENDİ: Siber güvenlik kaldırıldı
    keyboard = [
        [InlineKeyboardButton("🕌 İslam & Tarih", callback_data='konu_tarih')],
        [InlineKeyboardButton("💻 Kodlama & Yazılım", callback_data='konu_kod')],
        [InlineKeyboardButton("🧹 Hafızayı Temizle", callback_data='clear_memory')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await update.message.reply_text(welcome_text, reply_markup=reply_markup, parse_mode='Markdown')

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    user_input = update.message.text
    
    # "Yazıyor..." göstergesi
    await context.bot.send_chat_action(chat_id=update.effective_chat.id, action='typing')

    # Geçmişi yükle
    history = get_chat_session(user_id)
    chat = model.start_chat(history=history)

    try:
        # Gemini'ye gönder
        response = chat.send_message(user_input)
        bot_reply = response.text
        
        # Geçmişi güncelle
        user_histories[user_id] = chat.history
        
        await update.message.reply_text(bot_reply)

    except Exception as e:
        # Hata olursa kullanıcıya bildir
        error_msg = f"⚠️ Bir sorun oldu kral. Hata detayı: {str(e)}"
        print(error_msg)
        await update.message.reply_text(error_msg)

async def button_click(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    if query.data == 'clear_memory':
        user_histories[query.from_user.id] = []
        await query.edit_message_text(text="🧹 Hafızamı sıfırladım. Tertemiz bir sayfa açtık!")
        
    elif query.data == 'konu_tarih':
        await query.message.reply_text("Osmanlı tarihi ve İslamiyet üzerine derin sohbetlere varım. Nereden başlayalım?")
        
    elif query.data == 'konu_kod':
        await query.message.reply_text("Python, botlar veya algoritmalar... Kodlama dünyasında neyi merak ediyorsun?")

# ==========================================
# 4. ANA ÇALIŞTIRMA (MAIN)
# ==========================================
if __name__ == '__main__':
    # Önce Web Sunucusunu (Flask) Başlat
    keep_alive()
    
    # Sonra Botu Başlat
    print("Bot başlatılıyor...")
    application = ApplicationBuilder().token(TELEGRAM_TOKEN).build()
    
    application.add_handler(CommandHandler('start', start))
    application.add_handler(CallbackQueryHandler(button_click))
    application.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), handle_message))
    
    application.run_polling()
