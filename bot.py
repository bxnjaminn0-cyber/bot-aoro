import os
import threading
from flask import Flask, request
import telebot
import requests
from google import genai

# Cliente moderno de Gemini
client = genai.Client(api_key=os.environ.get("GEMINI_API_KEY"))

app = Flask(__name__)

@app.route('/')
def home():
    return "Bot IA AORO Activo", 200

def run_flask():
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)

# Lee el token de las variables de entorno de forma segura
TOKEN_TELEGRAM = os.environ.get("TELEGRAM_TOKEN")

bot = telebot.TeleBot(TOKEN_TELEGRAM)

SYSTEM_PROMPT = """
Sos el Agente Inteligente Oficial del ecosistema AORO.
Tus funciones son:
1. Responder dudas técnicas y comerciales sobre el token AORO.
2. Explicar la paridad 1:1 respaldada en oro físico.
3. Ayudar a los usuarios con soporte de billeteras.
4. Mantener un tono profesional, preciso, conciso y seguro.
"""

def obtener_precios_crypto():
    try:
        url = "https://api.coingecko.com/api/v3/simple/price?ids=pax-gold,tether-gold&vs_currencies=usd"
        res = requests.get(url, timeout=5).json()
        paxg = float(res.get('pax-gold', {}).get('usd', 0))
        xaut = float(res.get('tether-gold', {}).get('usd', 0))
        return paxg, xaut
    except Exception:
        return None, None

@bot.message_handler(commands=['start', 'help'])
def send_welcome(message):
    bot.reply_to(message, "¡Hola! Soy el Agente IA de AORO.")

@bot.message_handler(func=lambda message: message.text in ['📊 Cotización Oro / RWA', '/precio', '/oro'])
def send_price(message):
    paxg, xaut = obtener_precios_crypto()
    if paxg and xaut:
        res = f"📊 **Monitorear RWA en Vivo:**\n• PAX Gold: ${paxg}\n• Tether Gold: ${xaut}"
    else:
        res = "⚠️ No se pudo obtener la cotización en vivo."
    bot.reply_to(message, res, parse_mode="Markdown")

@bot.message_handler(func=lambda message: True)
def responder_ia(message):
    try:
        prompt_text = f"{SYSTEM_PROMPT}\n\n{message.text}"
        response = client.models.generate_content(
            model='gemini-2.0-flash',
            contents=prompt_text
        )
        bot.reply_to(message, response.text)
    except Exception as e:
        print(f"ERROR GEMINI DETALLADO: {e}")
        bot.reply_to(message, "⚠️ Ocurrió un inconveniente al consultar con el módulo de IA. Intentalo de nuevo.")

if __name__ == "__main__":
    threading.Thread(target=run_flask, daemon=True).start()
    print(">>> Agente IA AORO v2.0 activo...")
    bot.infinity_polling()
