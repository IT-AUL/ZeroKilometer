import uuid

from dotenv import load_dotenv, dotenv_values
from flask import Flask
from flask_sqlalchemy import SQLAlchemy

load_dotenv()

SECRET_KEY = "6329580650:AAFy9JCT62aHwTVqHJDFCwfG9skvw_MEiEw"
BOT_USERNAME = 'kazan_game_bot'
uuid = uuid

app = Flask(__name__)
app.config.from_mapping(dotenv_values())
db = SQLAlchemy(app)

from routes import main
app.register_blueprint(main)

with app.app_context():
    db.drop_all()
    db.create_all()
if __name__ == '__main__':
    app.run(debug=True)
