import os
import requests
from flask import Flask, request

app = Flask(__name__)

TOKEN = os.getenv("BOT_TOKEN")  # ustawiony w Render → Environment
URL = f"https://api.telegram.org/bot{TOKEN}"

@app.route("/", methods=["GET"])
def home():
    return "🌴 Jungle BOT działa ✅", 200

@app.route(f"/{TOKEN}", methods=["POST"])
def webhook():
    update = request.get_json()
    if not update:
        return "no data", 400

    if "message" in update and "text" in update["message"]:
        chat_id = update["message"]["chat"]["id"]
        text = update["message"]["text"]

        if text.lower() in ["/start", "start"]:
            send_message(chat_id, "🌴 Welcome to Jungle BOT! 🚀")
        else:
            send_message(chat_id, f"Otrzymałem: {text}")

    return "ok", 200

def send_message(chat_id, text):
    url = f"{URL}/sendMessage"
    payload = {"chat_id": chat_id, "text": text}
    requests.post(url, json=payload)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.getenv("PORT", 10000)))

