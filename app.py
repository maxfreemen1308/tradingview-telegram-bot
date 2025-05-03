from flask import Flask, request
import requests
import os

app = Flask(__name__)

TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')
CHAT_ID = os.getenv('CHAT_ID')

@app.route('/', methods=['POST'])
def webhook():
    data = request.json
    message = data.get('message', '⚠️ Новий сигнал без тексту')

    send_text = f'📈 TradingView Signal:\n{message}'
    url = f'https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage'
    requests.post(url, json={'chat_id': CHAT_ID, 'text': send_text})

    return 'OK', 200