from dotenv import load_dotenv, dotenv_values

from fl import create_app
from fl.models import db

load_dotenv()

app = create_app()
app.config.from_mapping(dotenv_values())

with app.app_context():
    db.init_app(app)
    db.drop_all()
    db.create_all()

if __name__ == '__main__':
    app.run()
