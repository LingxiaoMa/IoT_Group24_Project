import random
from datetime import datetime, timedelta
from app import db
from app.models import Message

def generate_random_data():
    # 当前时间
    current_time = datetime.now()
    
    # 生成两天的数据，每隔 30 秒生成一条记录
    time_interval = timedelta(seconds=10)
    start_time = current_time - timedelta(days=2)  # 从两天前开始

    # 生成两天共 2880 条记录 (2天 * 24小时 * 60分钟 * 60秒 / 30秒)
    for i in range(100):
        timestamp = start_time + i * time_interval
        content = random.choice(["True", "False"])  # 随机生成 True 或 False

        # 创建 Message 对象并插入到数据库
        message = Message(timestamp=timestamp, content=content)
        db.session.add(message)
    
    # 提交所有更改
    db.session.commit()
    print("Random data generated and added to the database.")
