import threading
import time
from datetime import datetime, timedelta
from app.models import Message
from app import db, app
from app.mail import send_fatigue_alert

# FatigueMonitorThread class is used to monitor driver fatigue and send an alert if necessary
class FatigueMonitorThread(threading.Thread):
    sent = False  # A flag to track if a fatigue alert has been sent in the last 10 minutes
    
    # Initialize the thread
    def __init__(self):
        threading.Thread.__init__(self)
        self._stop_event = threading.Event()  # Event to stop the thread

    # The main function that runs when the thread starts
    def run(self):
        print("Fatigue monitor thread started")
        while not self._stop_event.is_set():  # Keep running until the stop event is triggered
            if not self.sent:  # Check if an alert has not been sent in the last 10 minutes
                self.check_fatigue_status()
                time.sleep(10)  # Check every 10 seconds
            else:
                print("The message has been sent during the last 10 minutes")
                time.sleep(590)  # Wait for almost 10 minutes before checking again

    # Function to stop the thread
    def stop(self):
        self._stop_event.set()

    # Function to check the fatigue status based on the data in the database
    def check_fatigue_status(self):
        with app.app_context():  # Ensures the database operations run within the Flask app context
            # Get the timestamp of 10 minutes ago
            ten_minutes_ago = datetime.utcnow() - timedelta(minutes=10)
            
            # Query the database for 'True' values (indicating fatigue) in the last 10 minutes
            count = db.session.query(Message).filter(Message.content == 'True', Message.timestamp >= ten_minutes_ago).count()

            # If 20 or more instances of fatigue are detected and an alert has not been sent yet
            if count >= 20 and not self.sent:
                print("Fatigue detected! Sending alert...")
                send_fatigue_alert()  # Send an alert (e.g., email notification)
                self.sent = True  # Set the flag to indicate an alert has been sent

            # If an alert has already been sent, notify that the message was already sent
            elif self.sent:
                print("The message has been sent during the last 10 minutes")

            # If no fatigue is detected, print that no fatigue was found
            else:
                print("No fatigue detected in the last 10 minutes")
