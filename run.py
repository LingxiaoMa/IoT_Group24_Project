import sqlalchemy as sa
import sqlalchemy.orm as so
from app import app, db
from app.models import Message


# 注册路由
from app.routes import main
app.register_blueprint(main)

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5012, debug=True)


@app.shell_context_processor
def make_shell_context():
    return {'sa': sa, 'so': so, 'db': db, 'Message': Message}