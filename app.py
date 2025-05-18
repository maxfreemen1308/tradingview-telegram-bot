from flask import Flask, request
import requests
import os
import re

app = Flask(__name__)

TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')
CHAT_ID = os.getenv('CHAT_ID')

last_price = None

@app.route('/', methods=['POST'])
def webhook():
    global last_price

    if request.content_type == 'application/json':
        data = request.get_json()
        message = data.get('message', '')
    else:
        message = request.data.decode('utf-8')

    print(f"🔍 Отримано повідомлення: {message}")

    match = re.search(r'(BUY|SELL) on (\w+) at price (\d+(?:\.\d+)?)', message, re.IGNORECASE)

    if match:
        action, ticker, price_str = match.groups()
        price = float(price_str)
        response = f"📈 Signal: {action.upper()} on {ticker} at ${price:.4f}"

        if last_price is not None:
            diff = price - last_price
            diff_percent = (diff / last_price) * 100
            sign = "▲" if diff > 0 else "▼"
            response += f"\n{sign} Зміна від попередньої ціни: {diff:.4f} USD ({diff_percent:.4f}%)"

        last_price = price
    else:
        response = "⚠️ Новий сигнал без розпізнаної ціни."

    url = f'https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage'
    requests.post(url, json={'chat_id': CHAT_ID, 'text': response})

    return 'OK', 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))
