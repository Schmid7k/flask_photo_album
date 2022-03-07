from .db import db


class Photo(db.Document):
    name = db.StringField(required=True)
    # complete the remaining code
    tags = db.ListField(db.StringField())
    location = db.StringField()
    image_file = db.ImageField(required=True)
    albums = db.ListField(db.ReferenceField("Album"))


class Album(db.Document):
    # complete the remaining code
    name = db.StringField(required=True, unique=True)
    description = db.StringField()
