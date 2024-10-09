import socket
import threading
from app.models import Message
from datetime import datetime
from app import app, db
from app.esp32_client import send_message_to_esp32 

class TCPServer:
    def __init__(self, host='0.0.0.0', port=5010):
        self.host = host
        self.port = port
        self.server_socket = None
        self.conn = None
        self.addr = None
        self.running = False

    def start_server(self):
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.bind((self.host, self.port))
        self.server_socket.listen(1)
        self.running = True
        print(f"Server listening on port {self.port}")

        # 启动新线程来接受客户端连接
        threading.Thread(target=self.accept_client).start()

    def accept_client(self):
        self.conn, self.addr = self.server_socket.accept()
        print(f"Connected to {self.addr}")

        while self.running:
            try:
                data = self.conn.recv(1024).decode('utf-8')
                if not data:
                    break
                data = data.strip()
                print(f"Received data: {data}")
                # 在这里处理接收到的数据
                with app.app_context():
                    msg = Message()
                    msg.content = data
                    db.session.add(msg)
                    db.session.commit()
                    
                    print(f"Stored into database data: {data}")
                    
                    if data == "True":
                        print("Sent 'ON' to esp32")
                        send_message_to_esp32("ON")
                    elif data == "False":
                        send_message_to_esp32("OFF")

            except Exception as e:
                print(f"Error receiving data: {e}")
                break

        self.stop_server()

    def stop_server(self):
        self.running = False
        if self.conn:
            self.conn.close()
        if self.server_socket:
            self.server_socket.close()
        print("Server stopped")

# 创建全局 TCP 服务器实例
tcp_server_instance = TCPServer()

def start_tcp_server():
    tcp_server_instance.start_server()

def stop_tcp_server():
    tcp_server_instance.stop_server()
