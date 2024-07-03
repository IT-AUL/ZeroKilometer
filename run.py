import os
from datetime import timedelta

from dotenv import load_dotenv, dotenv_values

from fl import create_app
from fl.models import db, User, Quest, GeoPoint

load_dotenv()

app = create_app()
app.config.from_mapping(dotenv_values())
app.config['JWT_ACCESS_TOKEN_EXPIRES'] = timedelta(minutes=int(os.getenv('JWT_ACCESS_TOKEN_EXPIRES')))
app.config['JWT_REFRESH_TOKEN_EXPIRES'] = timedelta(days=int(os.getenv('JWT_REFRESH_TOKEN_EXPIRES')))

with app.app_context():
    db.init_app(app)
    db.drop_all()
    db.create_all()

    # user = User(457454, "egeg", "")
    # db.session.add(user)
    # db.session.commit()
    #
    # point = GeoPoint("25236", "rrh")
    # point.user_id = user.id
    # db.session.add(point)
    # db.session.commit()
    #
    # q = Quest("4257248458", "quest 1")
    # q.user_id = user.id
    # q.geopoints.append(point)
    # q.geopoints.append(point)
    # db.session.add(q)
    # db.session.commit()
    #
    # q = Quest("4257248", "quest 2")
    # q.user_id = user.id
    # q.geopoints.append(point)
    # q.geopoints.append(point)
    # db.session.add(q)
    # db.session.commit()
    #
    # user = User(45744, "egeg", "rr")
    # db.session.add(user)
    # db.session.commit()
    # user = User.query.filter(User.id == 457454).first()
    #
    # user.quests.append(q)
    # db.session.commit()
    # print(user.quests)
    #
    # print(user.geo_points)

if __name__ == '__main__':
    app.run()
