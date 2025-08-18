import os
import logging
from flask import Flask, request, jsonify
import requests

BOT_TOKEN = os.getenv("BOT_TOKEN")
USE_WEBHOOK = os.getenv("USE_WEBHOOK", "false").lower() == "true"
WEBHOOK_SECRET = os.getenv("WEBHOOK_SECRET", "supersecret")
PUBLIC_BASE_URL = os.getenv("PUBLIC_BASE_URL", "")
ADGEM_APPID = os.getenv("ADGEM_APPID", "30887")

app = Flask(__name__)

# In-memory baza demo
players = {}

@app.route('/healthz')
def health():
    return "ok", 200

@app.route('/telegram/webhook', methods=['POST'])
def telegram_webhook():
    if request.args.get("secret") != WEBHOOK_SECRET:
        return "forbidden", 403
    data = request.json
    if "message" in data:
        chat_id = data["message"]["chat"]["id"]
        text = data["message"].get("text", "")
        if text == "/start":
            players[chat_id] = players.get(chat_id, {"coins": 0, "ads": 0, "keys": 0})
            send_message(chat_id, "🌴 Welcome to TONchaser demo! Use /stats to view your progress.")
        elif text == "/stats":
            p = players.get(chat_id, {"coins": 0, "ads": 0, "keys": 0})
            msg = f"💰 Coins: {p['coins']}\n📺 Ads Watched: {p['ads']}\n🗝 Keys: {p['keys']}"
            send_message(chat_id, msg)
    return "ok"

@app.route('/postback')
def postback():
    playerid = request.args.get("playerid")
    amount = int(request.args.get("amount", "0"))
    tx = request.args.get("tx")
    if not playerid or amount <= 0:
        return "invalid", 400
    p = players.get(int(playerid), {"coins": 0, "ads": 0, "keys": 0})
    p["coins"] += amount
    p["ads"] += 1
    if p["ads"] % 30 == 0:
        p["keys"] += 1
    players[int(playerid)] = p
    return "ok"

def send_message(chat_id, text):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    requests.post(url, json={"chat_id": chat_id, "text": text})

if __name__ == "__main__":
    port = int(os.getenv("PORT", 8080))
    if USE_WEBHOOK and BOT_TOKEN and PUBLIC_BASE_URL:
        setwh_url = f"https://api.telegram.org/bot{BOT_TOKEN}/setWebhook?url={PUBLIC_BASE_URL}/telegram/webhook?secret={WEBHOOK_SECRET}"
        r = requests.get(setwh_url)
        logging.info(f"Webhook set: {r.text}")
    app.run(host="0.0.0.0", port=port)
