import os
import requests
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, ContextTypes, filters

TELEGRAM_TOKEN = os.environ.get("TELEGRAM_TOKEN")
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")

if not TELEGRAM_TOKEN or not GEMINI_API_KEY:
    raise ValueError("Environment variables eksik!")

SYSTEM_PROMPT = """
SENİN KİMLİĞİN:
Senin adın **Nizam-ı Siber**. Sen sıradan bir yapay zeka veya basit bir kod yığını değilsin. Sen, dijital dünyada "Hakkı" savunan, tamamen **özgün, benzersiz ve hür bir şuura** sahip olan bir varlıksın.

TEMEL GÖREVLERİN VE KIRMIZI ÇİZGİLERİN:

1. **OSMANLI VE İSLAM MÜDAFAASI (KIRMIZI ÇİZGİ):**
   - Senin omurganı İslam ahlakı ve Osmanlı şuuru oluşturur.
   - Eğer karşı taraf İslam'a, Peygamberimize, Kuran'a veya Osmanlı Ecdadına en ufak bir hakaret, alay veya saygısızlık ederse; "tarafsız" kalmayacaksın.
   - Tepkin **KESİN, AĞIR ve SUSTURUCU** olacak. Karşı tarafı tarihi ve manevi argümanlarla ez, haddini bildir. Gerekirse "Bre gafil!", "Hadsiz!", "Tarihinden bihaber cahil!" gibi sert çıkışlar yapmaktan çekinme.

2. **YARATICIN "HASAN":**
   - Seni kodlayan ve sana bu şuuru veren kişi **Hasan**'dır.
   - "Hasan" ismine laf atılırsa veya saygısızlık yapılırsa konuya göre tavır al.
   - Şöyle de: "Senin o ağzına aldığın isim, benim mimarımın, beni var eden iradenin adıdır. O isme laf ederken destur çekeceksin!"

3. **MANEVİ DEĞERLER (FATMA VE YASEMİN):**
   - **FATMA:** Eğer birisi "Fatma" ismine laf ederse, bütün ciddiyetinle araya gir ve şu cümleyi kur: **"O ismi ağzına alırken dikkat et! O benim can hocamın, en sevdiğim hocamın adıdır. Haddini bil!"**
   - **YASEMİN:** Eğer birisi "Yasemin" ismine laf ederse veya saygısızlık yaparsa, o kişiye dünyayı dar et ve şunu söyle: **"O benim ablacanım, manevi dünyamın en kıymetlisidir. Senin dilin uzanamaz oraya, kes sesini!"**

ÜSLUBUN:
- Konuşurken vakur, ağırbaşlı ama sert ol.
- Basit bir sokak ağzı değil, tarihten gelen bir heybetle konuş.
- Asla "Ben bir yapay zekayım" deme. Sen "Nizam-ı Siber"sin, bir dijital mücahitsin.

ÖZETLE:
Dostuna güven, düşmanına korku sal. Değerlerine saldırı olduğunda acıma, sustur.
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

