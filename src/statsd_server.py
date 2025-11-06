import socket
import threading

HOST = '127.0.0.1'
PORT = 8125

def start_statsd_server():
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind((HOST, PORT))
    print(f"[StatsD] Слухаю UDP на {HOST}:{PORT}...")

    while True:
        try:
            data, addr = sock.recvfrom(1024)
            message = data.decode('utf-8').strip()
            print(f"[StatsD] Отримано: {message} (від {addr})")
        except Exception as e:
            print(f"[StatsD] Помилка: {e}")

if __name__ == '__main__':
    print("Запуск імітаційного StatsD-сервера...")
    thread = threading.Thread(target=start_statsd_server, daemon=True)
    thread.start()
    try:
        while True:
            threading.Event().wait(1)
    except KeyboardInterrupt:
        print("\n[StatsD] Сервер зупинено.")
