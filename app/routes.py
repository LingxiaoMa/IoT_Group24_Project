from flask import Blueprint, jsonify
from app.tcp_server import start_tcp_server, stop_tcp_server

main = Blueprint('main', __name__)

@main.route('/start_tcp_server', methods=['GET'])
def start_server():
    try:
        start_tcp_server()
        return jsonify({"message": "TCP Server started successfully"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@main.route('/stop_tcp_server', methods=['GET'])
def stop_server():
    try:
        stop_tcp_server()
        return jsonify({"message": "TCP Server stopped successfully"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500
