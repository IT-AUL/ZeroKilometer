# run.py
from fl import create_app
from fl.models import db

app = create_app()
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///test.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = 'secret!'

with app.app_context():
    db.init_app(app)
    db.drop_all()
    db.create_all()

if __name__ == '__main__':
    app.run(debug=True)
