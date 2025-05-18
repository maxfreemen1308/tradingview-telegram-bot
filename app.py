from flask import Flask, request
import requests
import os
import re

app = Flask(__name__)

# Отримуємо токен і чат ID з середовища
TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')
CHAT_ID = os.getenv('CHAT_ID')

# Зберігаємо попередню ціну для обчислення відсоткової різниці
last_price = None

@app.route('/', methods=['POST'])
def webhook():
    global last_price

    data = request.get_json()  # ✅ TradingView надсилає JSON

    message = data.get('message', '⚠️ Новий сигнал без тексту')
    print(f"🔍 Отримано повідомлення: {message}")

    # Розпізнаємо BUY/SELL, назву тикера і ціну
    match = re.search(r'(BUY|SELL) on (\w+) at price (\d+(?:\.\d+)?)', message, re.IGNORECASE)

    if match:
        action, ticker, price_str = match.groups()
        price = float(price_str)
        response = f"📈 Signal: {action.upper()} on {ticker} at ${price:.2f}"

        if last_price is not None:
            diff = price - last_price
            diff_percent = (diff / last_price) * 100
            sign = "▲" if diff > 0 else "▼"
            response += f"\n{sign} Зміна від попередньої ціни: {diff:.2f} USD ({diff_percent:.2f}%)"

        last_price = price
    else:
        response = "⚠️ Новий сигнал без розпізнаної ціни."

    # Надсилаємо повідомлення в Telegram
    url = f'https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage'
    requests.post(url, json={'chat_id': CHAT_ID, 'text': response})

    return 'OK', 200

# Запуск Flask-сервера
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))
