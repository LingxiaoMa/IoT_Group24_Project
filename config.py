import os
basedir = os.path.abspath(os.path.dirname(__file__))

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'you-will-never-guess'
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
        'sqlite:///' + os.path.join(basedir, 'app.db')
        
     # 邮件服务器配置
    MAIL_SERVER = os.environ.get('MAIL_SERVER') or 'smtp.gmail.com'  # 邮件服务器（例如Gmail、Outlook等）
    MAIL_PORT = int(os.environ.get('MAIL_PORT') or 587)  # 邮件服务器端口号，通常TLS使用587端口
    MAIL_USE_TLS = True  # 是否启用 TLS
    MAIL_USE_SSL = False  # 是否启用 SSL
    MAIL_USERNAME = 'malingxiao930@gmail.com'  # 邮件服务器的用户名（例如邮箱地址）
    MAIL_PASSWORD = 'jrqr nqjr nbcx cjmu'  # 邮件服务器的密码
    MAIL_DEFAULT_SENDER = os.environ.get('MAIL_DEFAULT_SENDER') or 'malingxiao930@gmail.com'  # 默认发送者邮箱