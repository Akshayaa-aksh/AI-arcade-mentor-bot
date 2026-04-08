import os
import socket

os.environ.pop("SSL_CERT_FILE", None)
os.environ.pop("REQUESTS_CA_BUNDLE", None)

from app.ui.app import build_ui
from app.ui.styles import CSS

def find_available_port(start_port=7860):
    for port in range(start_port, start_port + 100):
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.bind(("127.0.0.1", port))
            sock.close()
            return port
        except OSError:
            continue
    return start_port

if __name__ == "__main__":
    demo = build_ui()
    port = find_available_port(7860)
    demo.launch(server_name="127.0.0.1", server_port=port, css=CSS)