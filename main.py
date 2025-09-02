import http.server
import socketserver
import urllib.parse
import json
import os
from datetime import datetime
from jinja2 import Environment, FileSystemLoader


class HttpHandler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        self.jinja_env = Environment(loader=FileSystemLoader("templates"))
        super().__init__(*args, **kwargs)

    def do_GET(self):
        pr_url = urllib.parse.urlparse(self.path)

        if pr_url.path == "/":
            self.send_html_file("index.html")
        elif pr_url.path == "/message.html":
            self.send_html_file("message.html")
        elif pr_url.path == "/style.css":
            self.send_static_file("style.css", "text/css")
        elif pr_url.path == "/logo.png":
            self.send_static_file("logo.png", "image/png")
        elif pr_url.path == "/read":
            self.send_read_page()
        else:
            self.send_html_file("error.html", 404)

    def do_POST(self):
        pr_url = urllib.parse.urlparse(self.path)

        if pr_url.path == "/message":
            self.send_message()
        else:
            self.send_html_file("error.html", 404)

    def send_html_file(self, filename, status=200):
        self.send_response(status)
        self.send_header("Content-type", "text/html")
        self.end_headers()
        with open(filename, "rb") as fd:
            self.wfile.write(fd.read())

    def send_static_file(self, filename, content_type):
        if os.path.exists(filename):
            self.send_response(200)
            self.send_header("Content-type", content_type)
            self.end_headers()
            with open(filename, "rb") as fd:
                self.wfile.write(fd.read())
        else:
            self.send_html_file("error.html", 404)

    def send_read_page(self):
        # Читаємо дані з JSON файлу
        data = {}
        if os.path.exists("storage/data.json"):
            try:
                with open("storage/data.json", "r", encoding="utf-8") as f:
                    data = json.load(f)
            except json.JSONDecodeError:
                data = {}

        # Рендеримо шаблон
        template = self.jinja_env.get_template("read.html")
        html_content = template.render(messages=data)

        self.send_response(200)
        self.send_header("Content-type", "text/html; charset=utf-8")
        self.end_headers()
        self.wfile.write(html_content.encode("utf-8"))

    def send_message(self):
        content_length = int(self.headers["Content-Length"])
        post_data = self.rfile.read(content_length).decode("utf-8")

        # Парсимо дані форми
        data = urllib.parse.parse_qs(post_data)
        username = data.get("username", [""])[0]
        message = data.get("message", [""])[0]

        # Створюємо запис з часовою міткою
        timestamp = str(datetime.now())

        # Читаємо існуючі дані
        json_data = {}
        if os.path.exists("storage/data.json"):
            try:
                with open("storage/data.json", "r", encoding="utf-8") as f:
                    json_data = json.load(f)
            except json.JSONDecodeError:
                json_data = {}

        # Додаємо нове повідомлення
        json_data[timestamp] = {"username": username, "message": message}

        # Зберігаємо у файл
        os.makedirs("storage", exist_ok=True)
        with open("storage/data.json", "w", encoding="utf-8") as f:
            json.dump(json_data, f, ensure_ascii=False, indent=2)

        # Перенаправляємо на головну сторінку
        self.send_response(302)
        self.send_header("Location", "/")
        self.end_headers()


def run():
    print("Setting up server...")
    server_address = ("", 3000)
    print(f"Server address: {server_address}")
    http_server = socketserver.TCPServer(server_address, HttpHandler)
    print("Server created successfully")
    try:
        print("Starting server on port 3000...")
        print("Open http://localhost:3000 in your browser")
        print("Press Ctrl+C to stop the server")
        http_server.serve_forever()
    except KeyboardInterrupt:
        print("\nShutting down server...")
        http_server.server_close()
        print("Server stopped")


if __name__ == "__main__":
    run()
