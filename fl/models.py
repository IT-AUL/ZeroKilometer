from sqlalchemy import JSON
from sqlalchemy.ext.mutable import MutableDict, MutableList
from sqlalchemy.orm import Mapped, mapped_column
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


class User(db.Model):
    id: Mapped[int] = mapped_column(primary_key=True)
    username: Mapped[str] = mapped_column(nullable=False)
    progress: Mapped[MutableDict] = mapped_column(MutableDict.as_mutable(JSON), nullable=True, default=dict)
    quests: Mapped[MutableList] = mapped_column(MutableList.as_mutable(JSON), nullable=True, default=list)

    def __init__(self, id, username):
        self.id = id
        self.username = username

    def __repr__(self):
        return '<User %r>' % self.id


class Quest(db.Model):
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(nullable=False)
    plot: Mapped[str] = mapped_column(nullable=True)

    def __init__(self, id, name, plot):
        self.id = id
        self.name = name
        self.plot = plot

    def __repr__(self):
        return '<Quest %r>' % self.id

    def to_dict(self):
        return {"id": self.id, "name": self.name, "plot": self.plot}
