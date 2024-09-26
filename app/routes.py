from flask import Blueprint, jsonify
from app.tcp_server import start_tcp_server, stop_tcp_server
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
