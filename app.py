import os
import requests
import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, ContextTypes, CommandHandler, MessageHandler, filters, CallbackQueryHandler
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
    return "Bot çalışıyor! Nizam-ı Siber Online."

def run_flask():
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)

def keep_alive():
    t = Thread(target=run_flask)
    t.daemon = True
    t.start()

# ==========================================
# 2. MANUEL GEMINI API BAĞLANTISI (Kütüphanesiz)
# ==========================================
# Hafıza: {user_id: [ {"role": "user", "parts": [{"text": "..."}]}, ... ]}
user_histories = {}

def get_gemini_response(user_id, user_message):
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={GEMINI_API_KEY}"
    
    # Geçmişi al veya oluştur
    if user_id not in user_histories:
        user_histories[user_id] = []
    
    history = user_histories[user_id]
    
    # Yeni mesajı geçmişe ekle (API formatına uygun)
    history.append({"role": "user", "parts": [{"text": user_message}]})
    
    # Sistem talimatını başa ekle (Sadece gönderirken, hafızaya kaydetmeden)
    system_instruction = {
        "role": "user", 
        "parts": [{"text": "Sen Hasan Aslan'sın. Lise öğrencisi, siber güvenlikçi, kodlama ve İslam tarihi meraklısı. Samimi ve genç bir dille konuş."}]
    }
    
    payload = {
        "contents": [system_instruction] + history
    }
    
    try:
        response = requests.post(url, json=payload)
        response.raise_for_status() # Hata varsa yakala
        data = response.json()
        
        # Cevabı al
        bot_reply = data['candidates'][0]['content']['parts'][0]['text']
        
        # Botun cevabını da hafızaya ekle
        history.append({"role": "model", "parts": [{"text": bot_reply}]})
        
        # Hafıza çok şişerse başını kes (Son 20 mesaj kalsın)
        if len(history) > 20:
            user_histories[user_id] = history[-20:]
            
        return bot_reply
        
    except Exception as e:
        print(f"API Hatası: {e}")
        return f"⚠️ Bağlantı hatası: {str(e)}"

# ==========================================
# 3. TELEGRAM FONKSİYONLARI
# ==========================================

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    welcome_text = (
        f"👋 **Selamun Aleyküm {user.first_name}! Ben Hasan.**\n\n"
        "Yazılım, Tarih ve Siber Güvenlik konuşmaya hazırım.\n"
        "Hafızam açık, seni dinliyorum."
    )
    keyboard = [[InlineKeyboardButton("🧹 Hafızayı Temizle", callback_data='clear_memory')]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text(welcome_text, reply_markup=reply_markup, parse_mode='Markdown')

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    user_input = update.message.text
    
    await context.bot.send_chat_action(chat_id=update.effective_chat.id, action='typing')
    
    # Manuel fonksiyonu çağır
    response_text = get_gemini_response(user_id, user_input)
    
    await update.message.reply_text(response_text)

async def button_click(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    if query.data == 'clear_memory':
        user_histories[query.from_user.id] = []
        await query.edit_message_text(text="🧹 Hafızam sıfırlandı.")

if __name__ == '__main__':
    keep_alive()
    application = ApplicationBuilder().token(TELEGRAM_TOKEN).build()
    application.add_handler(CommandHandler('start', start))
    application.add_handler(CallbackQueryHandler(button_click))
    application.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), handle_message))
    application.run_polling()
