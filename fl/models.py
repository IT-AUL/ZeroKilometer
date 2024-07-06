from sqlalchemy import JSON
from sqlalchemy.event import listens_for
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
    published: Mapped[bool] = mapped_column(default=False, nullable=False)

    def __init__(self, id):
        self.id = id

    def __repr__(self):
        return '<Quest %r>' % self.id

    def ready_for_publish(self) -> bool:
        return self.title_draft and self.link_to_promo_draft and self.description_draft and len(
            self.geopoints_draft) > 0 and all(geo.published for geo in self.geopoints_draft)

    def prepare_for_publishing(self):
        self.title = self.title_draft
        self.link_to_promo = f'quest/{self.id}/promo.{self.link_to_promo_draft.split(".")[-1]}'
        self.description = self.description_draft
        self.geopoints.clear()
        self.geopoints.extend(self.geopoints_draft)
        self.published = True


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

    published: Mapped[bool] = mapped_column(default=False, nullable=False)

    def __init__(self, id):
        self.id = id

    def __repr__(self):
        return '<GeoPoint %r>' % self.id

    def ready_for_publish(self) -> bool:
        return bool(self.title_draft and self.coords_draft and self.link_to_promo_draft and self.description_draft)

    def prepare_for_publishing(self):
        self.title = self.title_draft
        self.coords = self.coords_draft
        self.link_to_promo = f'geopoint/{self.id}/promo.{self.link_to_promo_draft.split(".")[-1]}'
        self.description = self.description_draft
        if self.link_to_audio_draft:
            self.link_to_audio = f'geopoint/{self.id}/audio.{self.link_to_audio_draft.split(".")[-1]}'
        else:
            self.link_to_audio = None
        self.links_to_media.clear()
        cnt = 0
        for media in self.links_to_media_draft:
            self.links_to_media.append(f'geopoint/{self.id}/media_{cnt}.{media.split(".")[-1]}')
            cnt += 1
        self.published = True
