from app import app, db


# 注册路由
from app.routes import main
app.register_blueprint(main)

if __name__ == "__main__":
    app.run(debug=True)
