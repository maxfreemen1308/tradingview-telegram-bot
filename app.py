from flask import Flask, request
import requests
import os
import re

app = Flask(__name__)

TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')
CHAT_ID = os.getenv('CHAT_ID')

# Зберігаємо останню ціну сигналу (в оперативній пам’яті)
last_price = None

@app.route('/', methods=['POST'])
def webhook():
    global last_price
    data = request.json
    message = data.get('message', '')

    match = re.search(r'(\bBUY\b|\bSELL\b)\s+(\w+)\s+@\s+([\d.]+)', message)

    if match:
        action = match.group(1)
        symbol = match.group(2)
        price = float(match.group(3))

        percent_diff = ""
        if last_price is not None:
            change = ((price - last_price) / last_price) * 100
            percent_diff = f"\n📊 Зміна від попереднього сигналу: {change:.2f}%"

        last_price = price

        send_text = f'📈 Сигнал: {action} {symbol} @ {price}{percent_diff}'
    else:
        send_text = '⚠️ Новий сигнал без розпізнаної ціни.'

    url = f'https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage'
    requests.post(url, json={'chat_id': CHAT_ID, 'text': send_text})

    return 'OK', 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))
