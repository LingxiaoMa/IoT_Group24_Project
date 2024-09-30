from flask import Blueprint, jsonify, request
from app.tcp_server import start_tcp_server, stop_tcp_server
from app.esp32_client import send_message_to_esp32
from app import db
from app.models import Message

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
    
@main.route('/clear_all', methods =['POST'])
def clear_all():
    try:
        # 删除所有 Message 表中的数据
        num_rows_deleted = db.session.query(Message).delete()
        db.session.commit()
        return jsonify({"message": f"Deleted {num_rows_deleted} rows from the database"}), 200
    except Exception as e:
        db.session.rollback()  # 如果发生异常，回滚事务
        return jsonify({"error": str(e)}), 500


@main.route('/')
def index():
    return jsonify({"message": "Flask server is running!"})

# Route to send a message to the ESP32
@main.route('/send_message/<string:message>', methods=['POST'])
def send_message(message):
    # Ensure that only "ON" and "OFF" messages are allowed
    if message in ["ON", "OFF"]:
        # Send the message to the ESP32
        send_message_to_esp32(message)
        return jsonify({"status": "success", "message": f"Message '{message}' sent to ESP32."}), 200
    else:
        return jsonify({"status": "error", "message": "Invalid message. Use 'ON' or 'OFF'."}), 400