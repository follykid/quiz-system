from flask import Flask
from config import Config

from routes.admin import admin_bp
from routes.display import display_bp
from routes.student import student_bp

from models.database import init_db

app = Flask(__name__)
app.config.from_object(Config)

init_db()

app.register_blueprint(admin_bp)
app.register_blueprint(display_bp)
app.register_blueprint(student_bp)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)