import threading
import time
from datetime import datetime, timedelta
from app.models import Message
from app import db,app
from app.mail import send_fatigue_alert

class FatigueMonitorThread(threading.Thread):
    sent = False
    
    def __init__(self):
        threading.Thread.__init__(self)
        self._stop_event = threading.Event()

    def run(self):
        print("Fatigue monitor thread started")
        while not self._stop_event.is_set():
            if(not self.sent):
                self.check_fatigue_status()
                time.sleep(10)  # 每10秒检查一次
            else:
                print("The message have been sent during the last 10 minutes")
                time.sleep(590)

    def stop(self):
        self._stop_event.set()

    def check_fatigue_status(self):
        with app.app_context():
            # 获取当前时间的前10分钟
            ten_minutes_ago = datetime.utcnow() - timedelta(minutes=10)
            # 查询过去10分钟内数据库中的所有True值
            count = db.session.query(Message).filter(Message.content == 'True', Message.timestamp >= ten_minutes_ago).count()

            if count >= 20 and not self.sent:
                print("Fatigue detected! Sending alert...")
                # 在这里添加发送邮件或其他通知的逻辑
                send_fatigue_alert()
                self.sent = True
            elif self.sent:
                print("The message have been sent during the last 10 minutes")
            else:
                print("No fatigue detected in the last 10 minutes")
