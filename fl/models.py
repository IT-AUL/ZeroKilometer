from sqlalchemy import JSON, Column, ForeignKey, Table, Integer
from sqlalchemy.ext.mutable import MutableDict, MutableList
from sqlalchemy.orm import Mapped, mapped_column, relationship
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

# quest_geopoint_product = Table('quest_geopoint_product', db.Model.metadata,
#                                Column('quest_id', Integer, ForeignKey('quest.id'), primary_key=True),
#                                Column('geopoint_id', Integer, ForeignKey('geopoint.id'), primary_key=True)
#                                )
#
# quest_geopoint_testing = Table('quest_geopoint_testing', db.Model.metadata,
#                                Column('quest_id', Integer, ForeignKey('quest.id'), primary_key=True),
#                                Column('geopoint_id', Integer, ForeignKey('geopoint.id'), primary_key=True)
#                                )
#


quest_geopoint = db.Table('quest_geopoint',
                          db.Column('quest_id', db.Integer, db.ForeignKey('quest.id'), primary_key=True),
                          db.Column('geopoint_id', db.Integer, db.ForeignKey('geopoint.id'), primary_key=True)
                          )

quest_geopoint_draft = db.Table('quest_geopoint_draft',
                                db.Column('quest_id', db.Integer, db.ForeignKey('quest.id'), primary_key=True),
                                db.Column('geopoint_id', db.Integer, db.ForeignKey('geopoint.id'), primary_key=True)
                                )


class User(db.Model):
    id: Mapped[int] = mapped_column(primary_key=True)
    username: Mapped[str] = mapped_column(nullable=False)
    # link_to_profile_picture: Mapped[str] = mapped_column(nullable=True)
    # progress: Mapped[MutableDict] = mapped_column(MutableDict.as_mutable(JSON), nullable=True, default=dict)
    # quests: Mapped[list['Quest']] = db.relationship('Quest', backref='author', lazy=True)
    # geo_points: Mapped[list['GeoPoint']] = db.relationship('GeoPoint', backref='author', lazy=True)
    quests = db.relationship('Quest', backref='user', lazy=True)
    geo_points = db.relationship('GeoPoint', backref='user', lazy=True)

    def __init__(self, id, username):
        self.id = id
        self.username = username

    def __repr__(self):
        return '<User %r>' % self.id


class Quest(db.Model):
    __tablename__ = 'quest'

    id: Mapped[str] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(nullable=False)
    # link_to_promo: Mapped[str] = mapped_column(nullable=False)
    # description: Mapped[str] = mapped_column(nullable=False)
    # author_id: Mapped[int] = mapped_column(ForeignKey('user.id'), nullable=False)
    # geo_points_product: Mapped[list['GeoPoint']] = relationship('GeoPoint', secondary=quest_geopoint_product,
    #                                                             lazy='subquery',
    # backref=db.backref('quests_product', lazy=True))
    # geo_points_testing: Mapped[list['GeoPoint']] = relationship('GeoPoint', secondary=quest_geopoint_testing,
    #                                                             lazy='subquery',
    #                                                             backref=db.backref('quests_testing', lazy=True))
    geopoints = db.relationship('GeoPoint', secondary='quest_geopoint', backref=db.backref('quests', lazy='dynamic'))
    geopoints_draft = db.relationship('GeoPoint', secondary='quest_geopoint_draft',
                                      backref=db.backref('draft_quests', lazy='dynamic'))

    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

    def __init__(self, id, title):
        self.id = id
        self.title = title

    def __repr__(self):
        return '<Quest %r>' % self.id

    def to_dict(self):
        return {"id": self.id, "name": self.name, "plot": self.plot}


class GeoPoint(db.Model):
    __tablename__ = 'geopoint'
    id: Mapped[str] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(nullable=False)
    coords: Mapped[str] = mapped_column(nullable=False)

    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

    # link_to_promo: Mapped[str] = mapped_column(nullable=True)
    # description: Mapped[str] = mapped_column(nullable=True)
    # links_to_media: Mapped[MutableList] = mapped_column(MutableList.as_mutable(JSON), nullable=True, default=list)
    # link_to_audio: Mapped[str] = mapped_column(nullable=True)
    # author_id: Mapped[int] = mapped_column(ForeignKey('user.id'), nullable=False)

    def __init__(self, id, title, coords):
        self.id = id
        self.title = title
        self.coords = coords

    def __repr__(self):
        return '<GeoPoint %r>' % self.id
