from flask import Flask, request
import requests
import os
import re

app = Flask(__name__)

TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')
CHAT_ID = os.getenv('CHAT_ID')

# Глобальна змінна для зберігання попередньої ціни
last_price = None

@app.route('/', methods=['POST'])
def webhook():
    global last_price

    data = request.json
    message = data.get('message', '⚠️ Новий сигнал без тексту')

    # Парсимо з тексту: "SELL on BTCUSDT at price 67200.55"
    match = re.search(r'(BUY|SELL) on (\w+) at price (\d+(?:\.\d+)?)', message, re.IGNORECASE)
    
    if match:
        action = match.group(1).upper()
        symbol = match.group(2)
        current_price = float(match.group(3))

        # Розрахунок різниці у %
        if last_price is not None:
            percent_change = ((current_price - last_price) / last_price) * 100
            diff_text = f'📊 Зміна з минулого сигналу: {percent_change:.2f}%'
        else:
            diff_text = 'ℹ️ Перший сигнал, немає з чим порівняти.'

        last_price = current_price

        send_text = (
            f'📈 TradingView Signal\n'
            f'🔔 Дія: {action}\n'
            f'💰 Актив: {symbol}\n'
            f'💵 Ціна: {current_price}\n'
            f'{diff_text}'
        )
    else:
        send_text = '⚠️ Новий сигнал без розпізнаної ціни.'

    # Надсилаємо в Telegram
    url = f'https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage'
    requests.post(url, json={'chat_id': CHAT_ID, 'text': send_text})

    return 'OK', 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))
