from flask import Flask, jsonify
import logging
from logging.config import dictConfig
import socket
import time
from datetime import datetime
import threading

# Налаштування логування
dictConfig({
    'version': 1,
    'formatters': {
        'default': {
            'format': '%(asctime)s [%(levelname)s] %(message)s',
        }
    },
    'handlers': {
        'file': {
            'class': 'logging.FileHandler',
            'filename': 'app.log',
            'formatter': 'default',
            'level': 'INFO'
        },
        'console': {
            'class': 'logging.StreamHandler',
            'formatter': 'default',
            'level': 'INFO'
        }
    },
    'root': {
        'level': 'INFO',
        'handlers': ['file', 'console']
    }
})

app = Flask(__name__)
logger = logging.getLogger()

# Імітація StatsD — відправка UDP-повідомлень
STATSD_HOST = '127.0.0.1'
STATSD_PORT = 8125
statsd_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

# Лічильники та час старту
start_time = time.time()
request_count = 0
count_lock = threading.Lock()

def send_metric(metric_name, value=1, metric_type='c'):
    message = f"{metric_name}:{value}|{metric_type}"
    try:
        statsd_socket.sendto(message.encode('utf-8'), (STATSD_HOST, STATSD_PORT))
    except Exception:
        pass  # Ігноруємо помилки відправки

@app.before_request
def before_request():
    global request_count
    with count_lock:
        request_count += 1

@app.route('/')
def home():
    logger.info("Запит до кореневого маршруту '/'")
    return "Сервіс працює"

@app.route('/error')
def error():
    logger.info("Запит до '/error' — буде викликано помилку")
    try:
        result = 1 / 0
    except Exception as e:
        logger.exception("Виникла помилка при обробці /error")
        send_metric('app.errors', 1, 'c')
        raise
    return "Це не виконається"

@app.errorhandler(Exception)
def handle_exception(e):
    # Логуємо всі непіймані винятки
    logger.exception("Непіймана помилка")
    send_metric('app.errors', 1, 'c')
    return "Внутрішня помилка сервера", 500

@app.route('/status')
def status():
    uptime = time.time() - start_time
    with count_lock:
        requests = request_count
    status_data = {
        "status": "ok",
        "uptime_seconds": round(uptime, 2),
        "requests_processed": requests,
        "timestamp": datetime.now().isoformat()
    }
    logger.info(f"Запит до /status: оброблено {requests} запитів, uptime: {uptime:.2f}с")
    return jsonify(status_data)

if __name__ == '__main__':
    logger.info("Запуск Flask-додатку")
    app.run(host='0.0.0.0', port=5000, debug=False)
