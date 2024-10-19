from flask import Blueprint, jsonify, request, render_template
from app.tcp_server import start_tcp_server, stop_tcp_server, monitor_thread
from app.esp32_client import send_message_to_esp32
from sqlalchemy import func
import pandas as pd
from app import db
from app.models import Message
import socket
from datetime import timedelta
from flask_mail import Message as MailMessage
from app import mail
from app.mail import send_fatigue_alert
from app.FatigueMonitorThread import FatigueMonitorThread

# Define a Flask blueprint to group routes for the application
main = Blueprint('main', __name__)

@main.route('/', methods=['GET'])
def index():
    """ Renders the home page. """
    return render_template('index.html')

@main.route('/test', methods=['GET'])
def send_test_email():
    """ Test function to start the monitor thread and simulate sending an email. """
    try:
        if not monitor_thread.is_alive():
            monitor_thread.start()  # Start the fatigue monitor thread if it's not already running
        return jsonify({"status": "success", "message": "Test email sent successfully!"}), 200
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

# This route sends a start signal to Raspberry Pi and starts the monitoring thread
@main.route('/send-signal', methods=['POST'])
def send_signal():
    start_server()  # Start the TCP server
    global monitor_thread
    if not monitor_thread.is_alive():
        monitor_thread = FatigueMonitorThread()  # Create a new monitor thread
        monitor_thread.start()  # Start monitoring
    return send_tcp_signal("start_signal", '172.20.10.6', 5011)  # Send the "start_signal" to Raspberry Pi

# This route sends a stop signal to Raspberry Pi and stops the monitoring thread
@main.route('/stop-signal', methods=['POST'])
def stop_signal():
    stop_server()  # Stop the TCP server
    global monitor_thread
    if monitor_thread.is_alive():
        monitor_thread.stop()  # Stop the monitor thread
        monitor_thread.join()  # Wait for the thread to fully stop
    return send_tcp_signal("stop_signal", '172.20.10.6', 5011)  # Send the "stop_signal" to Raspberry Pi

# Function to send TCP signals to the Raspberry Pi
def send_tcp_signal(message, ip, port):
    """ Sends a TCP signal to Raspberry Pi using the provided message, IP, and port. """
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            sock.connect((ip, port))  # Connect to the Raspberry Pi
            sock.sendall(message.encode('utf-8'))  # Send the signal message
        print(f'Signal "{message}" sent to Raspberry Pi')
        return jsonify({"message": f'Signal "{message}" sent to Raspberry Pi'}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Route to start the TCP server
@main.route('/start_tcp_server', methods=['GET'])
def start_server():
    """ Starts the TCP server. """
    try:
        start_tcp_server()  # Calls the function to start the server
        return jsonify({"message": "TCP Server started successfully"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Route to stop the TCP server
@main.route('/stop_tcp_server', methods=['GET'])
def stop_server():
    """ Stops the TCP server. """
    try:
        return jsonify({"message": "TCP Server stopped successfully"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Route to clear all data from the Message table
@main.route('/clear_all', methods=['POST'])
def clear_all():
    """ Clears all records from the database. """
    try:
        # Delete all records from the Message table
        num_rows_deleted = db.session.query(Message).delete()
        db.session.commit()
        return jsonify({"message": f"Deleted {num_rows_deleted} rows from the database"}), 200
    except Exception as e:
        db.session.rollback()  # Rollback the transaction if any error occurs
        return jsonify({"error": str(e)}), 500

# Route to send a message to the ESP32
@main.route('/send_message/<string:message>', methods=['POST'])
def send_message(message):
    """ Sends a message to the ESP32. Only "ON" and "OFF" messages are allowed. """
    if message in ["ON", "OFF"]:
        send_message_to_esp32(message)  # Send the message to the ESP32
        return jsonify({"status": "success", "message": f"Message '{message}' sent to ESP32."}), 200
    else:
        return jsonify({"status": "error", "message": "Invalid message. Use 'ON' or 'OFF'."}), 400

# Route to group data into 30-second intervals and return as JSON
@main.route('/get_grouped_data', methods=['GET'])
def get_grouped_data():
    """ Retrieves and groups data in 30-second intervals from the database. """
    try:
        # Retrieve all messages from the database
        messages = Message.query.all()

        # Create a DataFrame with timestamps and content (True/False)
        data = {
            'timestamp': [msg.timestamp for msg in messages],
            'content': [1 if msg.content == "True" else 0 for msg in messages]  # Map True to 1 and False to 0
        }
        df = pd.DataFrame(data)

        # Round timestamps to the nearest 30 seconds
        df['rounded_time'] = pd.to_datetime(df['timestamp']).dt.floor('30S')

        # Group by 30-second intervals and sum the number of "True" entries
        grouped_df = df.groupby('rounded_time').agg({'content': 'sum'}).reset_index()

        # Return the grouped data as JSON
        result = grouped_df.to_dict(orient='records')
        return jsonify(result), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Route to render the chart page for visualizing grouped data
@main.route('/get_chart_page', methods=['GET'])
def get_chart_page():
    """ Renders the chart page for data visualization. """
    return render_template('chart.html')
