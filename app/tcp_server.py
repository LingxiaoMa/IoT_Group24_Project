import socket
import threading
from app.models import Message  # Importing the Message model to store the received data in the database
from datetime import datetime  # Importing datetime for timestamp handling
from app import app, db  # Importing the app and db objects from the Flask app
from app.esp32_client import send_message_to_esp32  # Function to send messages to ESP32
from flask_mail import Message as MailMessage  # Importing the Message class from Flask-Mail for sending emails
from app import mail  # Importing the mail object to send emails
from app.FatigueMonitorThread import FatigueMonitorThread  # Importing a custom thread for monitoring fatigue status

class TCPServer:
    def __init__(self, host='0.0.0.0', port=5010):
        """ Initializes the TCP server with the host and port. """
        self.host = host  # Server will listen on this host (0.0.0.0 means all available network interfaces)
        self.port = port  # Server will listen on this port
        self.server_socket = None  # Placeholder for the server's socket
        self.conn = None  # Placeholder for the client connection
        self.addr = None  # Placeholder for the client's address
        self.running = False  # Flag to indicate whether the server is running

    def start_server(self):
        """ Starts the TCP server and listens for incoming connections. """
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  # Creating a TCP socket
        self.server_socket.bind((self.host, self.port))  # Binding the socket to the specified host and port
        self.server_socket.listen(1)  # Listening for incoming connections (max 1 connection in the queue)
        self.running = True  # Mark the server as running
        print(f"Server listening on port {self.port}")

        # Start a new thread to handle client connections
        threading.Thread(target=self.accept_client).start()

    def accept_client(self):
        """ Accepts incoming client connections and processes received data. """
        self.conn, self.addr = self.server_socket.accept()  # Accept a new client connection
        print(f"Connected to {self.addr}")

        while self.running:
            try:
                data = self.conn.recv(1024).decode('utf-8')  # Receive data from the client
                if not data:
                    break  # Break the loop if no data is received
                data = data.strip()  # Clean up the received data
                print(f"Received data: {data}")

                # Store received data into the database
                with app.app_context():  # Use Flask's app context to access the database
                    msg = Message()  # Create a new Message instance
                    msg.content = data  # Store the received data in the content field
                    db.session.add(msg)  # Add the new message to the session
                    db.session.commit()  # Commit the transaction to save the message in the database
                    print(f"Stored into database data: {data}")
                    
                    # If the data indicates the driver is fatigued, send a signal to the ESP32
                    if data == "True":
                        print("Sent 'ON' to ESP32")
                        send_message_to_esp32("ON")  # Send an "ON" signal to the ESP32
                    elif data == "False":
                        send_message_to_esp32("OFF")  # Send an "OFF" signal to the ESP32

            except Exception as e:
                print(f"Error receiving data: {e}")  # Print any errors that occur during data reception
                break

        self.stop_server()  # Stop the server when the loop ends

    def send_fatigue_alert(self):
        """ Sends an email alert when fatigue is detected multiple times in a short period. """
        try:
            # Use Flask's app context to send an email
            with app.app_context():
                msg = MailMessage(
                    subject="Fatigue Alert: Driver Needs Rest",  # Email subject
                    sender="malingxiao930@gmail.com",  # Sender's email
                    recipients=["1531921981@qq.com"],  # Recipient's email
                    body="The driver has shown signs of fatigue multiple times in the past 10 minutes. Please advise them to take a rest."  # Email body
                )
                mail.send(msg)  # Send the email using Flask-Mail
                print("Fatigue alert email sent to driver.")
        except Exception as e:
            print(f"Error sending fatigue alert email: {e}")  # Print any errors that occur while sending the email

    def stop_server(self):
        """ Stops the TCP server and closes any open connections. """
        self.running = False  # Mark the server as no longer running
        if self.conn:
            self.conn.close()  # Close the client connection if it exists
        if self.server_socket:
            self.server_socket.close()  # Close the server's socket
        print("Server stopped")  # Confirm the server has stopped

# Create a global TCP server instance
tcp_server_instance = TCPServer()

# Create a global fatigue monitor thread instance
monitor_thread = FatigueMonitorThread()

def start_tcp_server():
    """ Starts the global TCP server instance. """
    tcp_server_instance.start_server()

def stop_tcp_server():
    """ Stops the global TCP server instance. """
    tcp_server_instance.stop_server()
