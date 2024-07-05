import os
from datetime import timedelta

from dotenv import load_dotenv, dotenv_values

from fl import create_app
from fl.models import db

load_dotenv()

app = create_app()
app.config.from_mapping(dotenv_values())
app.config['JWT_ACCESS_TOKEN_EXPIRES'] = timedelta(minutes=int(os.getenv('JWT_ACCESS_TOKEN_EXPIRES')))
app.config['JWT_REFRESH_TOKEN_EXPIRES'] = timedelta(days=int(os.getenv('JWT_REFRESH_TOKEN_EXPIRES')))

with app.app_context():
    db.init_app(app)
    db.drop_all()
    db.create_all()

if __name__ == '__main__':
    app.run()
