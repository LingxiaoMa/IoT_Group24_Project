from flask_mail import Message as MailMessage
from app import mail, app
from flask import jsonify

def send_fatigue_alert():
    """Send an email alert for fatigue driving."""
    try:
        # Create an email message with subject, sender, recipients, and body
        msg = MailMessage(
            subject="Fatigue Alert: Driver Needs Rest",
            sender="malingxiao930@gmail.com",  # Your Gmail email (replace with actual email)
            recipients=["1531921981@qq.com"],  # Recipient email (replace with the actual recipient)
            body="The driver has shown signs of fatigue. Please advise them to take a rest."
        )
        # Send the email using Flask-Mail's send method
        mail.send(msg)
        print("Fatigue alert email sent successfully!")
    except Exception as e:
        # If there is an error in sending the email, print the error message
        print(f"Error sending fatigue alert email: {e}")
