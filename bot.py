import os
import threading
from flask import Flask
import telebot
import requests
import google.generativeai as genai

# Servidor web liviano para el plan gratuito de Render
app = Flask(__name__)

@app.route('/')
def home():
    return "Bot IA AORO Activo", 200

def run_flask():
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port)

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN", "").strip()
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "").strip()


genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel("gemini-1.5-flash")

bot = telebot.TeleBot(TELEGRAM_TOKEN)

SYSTEM_PROMPT = """
Sos el Agente Inteligente Oficial del ecosistema AORO.
Tus funciones son:
1. Responder dudas técnicas y comerciales sobre el token AORO y activos RWA (Real World Assets).
2. Explicar la paridad 1:1 respaldada en oro físico, la quema del 99% de tokens y la migración hacia aoro.ai.
3. Ayudar a los usuarios con soporte de billeteras (como Bitget), staking y operaciones.
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
    bot.reply_to(message, "¡Hola! Soy el Agente IA de AORO. Podés preguntarme cualquier duda sobre el ecosistema, cotizaciones RWA o soporte de billeteras.")

@bot.message_handler(commands=['precio', 'oro'])
def send_price(message):
    paxg, xaut = obtener_precios_crypto()
    if paxg and xaut:
        res = f"📊 **Monitor RWA en Vivo:**\n• PAX Gold (PAXG): ${paxg:,.2f} USD\n• Tether Gold (XAUt): ${xaut:,.2f} USD\n• AORO Index: Paridad 1:1 respaldada en oro."
    else:
        res = "⚠️ No se pudo obtener la cotización en vivo."
    bot.reply_to(message, res, parse_mode="Markdown")

@bot.message_handler(func=lambda m: True)
def responder_con_ia(message):
    try:
        prompt = f"{SYSTEM_PROMPT}\n\nPregunta del usuario: {message.text}"
        response = model.generate_content(prompt)
        bot.reply_to(message, response.text)
    except Exception:
        bot.reply_to(message, "⚠️ Ocurrió un inconveniente al consultar con el módulo de IA. Intentalo de nuevo.")

if __name__ == "__main__":
    threading.Thread(target=run_flask, daemon=True).start()
    print(">>> Agente IA AORO v2.0 activo...")
    bot.infinity_polling()
