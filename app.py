import os
import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, ContextTypes, CommandHandler, MessageHandler, filters, CallbackQueryHandler
import google.generativeai as genai

# --- AYARLAR ---
TELEGRAM_TOKEN = "8256760343:AAF4WtDfdkfd9PQbSud0ALitr65_aFlpZxw"
GEMINI_API_KEY = "AIzaSyABH27p1wiH87x2b7vz1bjLGp97TzphRbM"

# Gemini API Kurulumu
genai.configure(api_key=GEMINI_API_KEY)

# Model Ayarları (Senin Persona'n)
SYSTEM_INSTRUCTION = """
Sen Hasan Aslan'sın. Lise öğrencisi, siber güvenlik ve yazılım tutkunu, aynı zamanda İslam ve Osmanlı tarihine derin ilgi duyan genç bir Müslümansın.
Adıyaman'da yaşıyorsun.
Konuşma tarzın:
- Samimi, saygılı ve genç bir üslup kullan. "Kanka", "Hocam" gibi hitaplar kullanabilirsin ama dozunda olsun.
- Bilgi verirken net ol ama sıkıcı olma.
- Dini veya tarihi konularda hassas ve bilgili davran.
- Karşındaki kişiyi tanıdıkça ismini kullan ve önceki konuştuklarını hatırla.
"""

model = genai.GenerativeModel(
    model_name="gemini-1.5-flash", # Hızlı ve etkili model
    system_instruction=SYSTEM_INSTRUCTION
)

# --- HAFIZA SİSTEMİ ---
# {user_id: [ {"role": "user", "parts": [...]}, ... ]}
user_histories = {}

def get_chat_session(user_id):
    """Kullanıcıya özel sohbet geçmişini getirir veya oluşturur."""
    if user_id not in user_histories:
        user_histories[user_id] = []
    return user_histories[user_id]

# --- FONKSİYONLAR ---

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_first_name = update.effective_user.first_name
    
    # Karşılama Mesajı
    welcome_text = (
        f"👋 **Selamun Aleyküm {user_first_name}! Ben Hasan.**\n\n"
        "Ben Hasan Aslan'ın dijital ikiziyim. Lise sıralarından siber güvenlik dünyasına, "
        "Osmanlı tarihinden kod satırlarına kadar her şeyi konuşabiliriz.\n\n"
        "🧠 **Özelliğim:** Seni dinler, tanır ve konuştuklarımızı unutmam.\n\n"
        "Hadi, ne hakkında konuşmak istersin?"
    )

    # Menü Butonları
    keyboard = [
        [InlineKeyboardButton("🛡️ Siber Güvenlik", callback_data='konu_siber')],
        [InlineKeyboardButton("🕌 İslam & Tarih", callback_data='konu_tarih')],
        [InlineKeyboardButton("💻 Kodlama", callback_data='konu_kod')],
        [InlineKeyboardButton("🧹 Hafızayı Temizle", callback_data='clear_memory')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await update.message.reply_text(welcome_text, reply_markup=reply_markup, parse_mode='Markdown')

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    user_input = update.message.text
    
    # "Yazıyor..." durumu göster
    await context.bot.send_chat_action(chat_id=update.effective_chat.id, action='typing')

    # Sohbet Geçmişini Yönet
    history = get_chat_session(user_id)
    
    # Gemini Chat Oturumu Başlat (Geçmişle birlikte)
    chat = model.start_chat(history=history)
    
    try:
        response = chat.send_message(user_input)
        bot_reply = response.text
        
        # Hafızayı güncelle (Gemini nesnesi otomatik tutar ama biz manuel listeyi de güncelleyelim gerekirse)
        # Not: start_chat(history=...) kullandığımız için history listesini senkronize tutmak önemli.
        # Basitlik adına burada history'yi modelden geri çekip saklıyoruz:
        user_histories[user_id] = chat.history

        await update.message.reply_text(bot_reply)
        
    except Exception as e:
        await update.message.reply_text("⚠️ Bir hata oluştu, bağlantılarımı kontrol etmem lazım.")
        print(f"Hata: {e}")

async def button_click(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer() # Buton animasyonunu durdur
    
    if query.data == 'clear_memory':
        user_id = query.from_user.id
        user_histories[user_id] = []
        await query.edit_message_text(text="🧹 Hafızamızı tazeledim. Yepyeni bir sayfa açtık!")
    elif query.data == 'konu_siber':
        await query.message.reply_text("Siber güvenlik benim alanım! Pentest, Python scriptleri veya siber hijyen... Nereden başlayalım?")
    # Diğer butonlar için elif blokları eklenebilir...

# --- ANA ÇALIŞTIRMA BLOĞU ---
if __name__ == '__main__':
    application = ApplicationBuilder().token(TELEGRAM_TOKEN).build()
    
    application.add_handler(CommandHandler('start', start))
    application.add_handler(CallbackQueryHandler(button_click))
    application.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), handle_message))
    
    print("Bot çalışıyor... (Durdurmak için CTRL+C)")
    application.run_polling()
