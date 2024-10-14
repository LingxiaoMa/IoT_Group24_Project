from flask_mail import Message as MailMessage
from app import mail,app
from flask import jsonify

def send_fatigue_alert():
    """发送疲劳驾驶提醒邮件"""
    try:
        msg = MailMessage(
            subject="Fatigue Alert: Driver Needs Rest",
            sender="malingxiao930@gmail.com",  # 你的Gmail邮箱
            recipients=["1531921981@qq.com"],  # 收件人邮箱，替换为实际邮箱
            body="The driver has shown signs of fatigue. Please advise them to take a rest."
        )
        mail.send(msg)
        print("Fatigue alert email sent successfully!")
    except Exception as e:
        print(f"Error sending fatigue alert email: {e}")