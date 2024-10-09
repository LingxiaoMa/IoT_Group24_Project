from flask import Blueprint, jsonify, request, render_template
from app.tcp_server import start_tcp_server, stop_tcp_server
from app.esp32_client import send_message_to_esp32
from sqlalchemy import func
import pandas as pd
from app import db
from app.models import Message
import socket
from datetime import timedelta

main = Blueprint('main', __name__)

@main.route('/',methods=['GET'])
def index():
    start_server()
    return render_template('index.html')

@main.route('/send-signal', methods=['POST'])
def send_signal():
    try:
        # Raspberry Pi 的 IP 和端口
        rasp_ip = '172.20.10.6' 
        rasp_port = 5011 

        # 创建 TCP 连接到 Raspberry Pi
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            sock.connect((rasp_ip, rasp_port))
            message = "start_signal"
            sock.sendall(message.encode('utf-8'))
        print('button clicked')
        return jsonify({"message": "Signal sent to Raspberry Pi"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    

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


# @main.route('/')
# def index():
#     return jsonify({"message": "Flask server is running!"})

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




@main.route('/get_grouped_data', methods=['GET'])
def get_grouped_data():
    try:
        # 查询数据库，获取所有时间戳和对应的 content (True/False)
        messages = Message.query.all()

        # 构建 DataFrame
        data = {
            'timestamp': [msg.timestamp for msg in messages],
            'content': [1 if msg.content == "True" else 0 for msg in messages]  # 用 1 表示 True，用 0 表示 False
        }
        df = pd.DataFrame(data)

        # 将时间戳转换为每 30 秒的时间段
        df['rounded_time'] = pd.to_datetime(df['timestamp']).dt.floor('30S')

        # 按 30 秒分组统计 True 的数量
        grouped_df = df.groupby('rounded_time').agg({'content': 'sum'}).reset_index()

        # 如果有需要平滑，可以在这里应用滑动窗口
        # grouped_df['content_smoothed'] = grouped_df['content'].rolling(window=3, min_periods=1).mean()

        # 构建返回的 JSON 数据
        result = grouped_df.to_dict(orient='records')

        return jsonify(result), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500
    
@main.route('/get_chart_page',methods=['GET'])
def get_chart_page():
    return render_template('chart.html')