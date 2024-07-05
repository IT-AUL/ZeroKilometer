from sqlalchemy import JSON
from sqlalchemy.ext.mutable import MutableDict, MutableList
from sqlalchemy.orm import Mapped, mapped_column
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

quest_geopoint = db.Table('quest_geopoint',
                          db.Column('quest_id', db.Integer, db.ForeignKey('quest.id'), primary_key=True),
                          db.Column('geopoint_id', db.Integer, db.ForeignKey('geopoint.id'), primary_key=True)
                          )

quest_geopoint_draft = db.Table('quest_geopoint_draft',
                                db.Column('quest_id', db.Integer, db.ForeignKey('quest.id'), primary_key=True),
                                db.Column('geopoint_id', db.Integer, db.ForeignKey('geopoint.id'), primary_key=True)
                                )


class User(db.Model):
    __tablename__ = 'user'

    id: Mapped[int] = mapped_column(primary_key=True)
    username: Mapped[str] = mapped_column(nullable=False)
    link_to_profile_picture: Mapped[str] = mapped_column(nullable=True)
    progress: Mapped[MutableDict] = mapped_column(MutableDict.as_mutable(JSON), nullable=True, default=dict)
    rating: Mapped[MutableDict] = mapped_column(MutableDict.as_mutable(JSON), nullable=True, default=dict)
    quests: Mapped[list['Quest']] = db.relationship('Quest', backref='user', lazy=True)
    geo_points: Mapped[list['GeoPoint']] = db.relationship('GeoPoint', backref='user', lazy=True)

    def __init__(self, id, username):
        self.id = id
        self.username = username

    def __repr__(self):
        return '<User %r>' % self.id


class Quest(db.Model):
    __tablename__ = 'quest'

    id: Mapped[str] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(nullable=True)
    link_to_promo: Mapped[str] = mapped_column(nullable=True)
    description: Mapped[str] = mapped_column(nullable=True)
    geopoints: Mapped[list['GeoPoint']] = db.relationship('GeoPoint', secondary='quest_geopoint',
                                                          backref=db.backref('quests', lazy='dynamic'))

    # draft
    title_draft: Mapped[str] = mapped_column(nullable=True)
    link_to_promo_draft: Mapped[str] = mapped_column(nullable=True)
    description_draft: Mapped[str] = mapped_column(nullable=True)
    geopoints_draft: Mapped[list['GeoPoint']] = db.relationship('GeoPoint', secondary='quest_geopoint_draft',
                                                                backref=db.backref('draft_quests', lazy='dynamic'))

    rating: Mapped[float] = mapped_column(nullable=False, default=0)
    rating_count: Mapped[int] = mapped_column(nullable=False, default=0)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

    def __init__(self, id):
        self.id = id

    def __repr__(self):
        return '<Quest %r>' % self.id

    def ready_for_publish(self) -> bool:
        return self.title_draft and self.link_to_promo_draft and self.description_draft and len(
            self.geopoints_draft) > 0

    def prepare_for_publishing(self):
        self.title = self.title_draft
        self.link_to_promo = f'quest/{self.id}_promo.{self.link_to_promo_draft.split(".")[-1]}'
        self.description = self.description_draft
        self.geopoints.clear()
        self.geopoints.extend(self.geopoints_draft)


class GeoPoint(db.Model):
    __tablename__ = 'geopoint'

    id: Mapped[str] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(nullable=True)
    coords: Mapped[str] = mapped_column(nullable=True)
    link_to_promo: Mapped[str] = mapped_column(nullable=True)
    description: Mapped[str] = mapped_column(nullable=True)
    links_to_media: Mapped[MutableList] = mapped_column(MutableList.as_mutable(JSON), nullable=True, default=list)
    link_to_audio: Mapped[str] = mapped_column(nullable=True)

    # draft
    title_draft: Mapped[str] = mapped_column(nullable=True)
    coords_draft: Mapped[str] = mapped_column(nullable=True)
    link_to_promo_draft: Mapped[str] = mapped_column(nullable=True)
    description_draft: Mapped[str] = mapped_column(nullable=True)
    links_to_media_draft: Mapped[MutableList] = mapped_column(MutableList.as_mutable(JSON), nullable=True, default=list)
    link_to_audio_draft: Mapped[str] = mapped_column(nullable=True)

    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

    def __init__(self, id):
        self.id = id

    def __repr__(self):
        return '<GeoPoint %r>' % self.id
