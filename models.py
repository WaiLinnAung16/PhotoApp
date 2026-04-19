from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class Photo(db.Model):
    __tablename__ = "photos"
    photo_id = db.Column(db.String(50), primary_key=True)
    image_url = db.Column(db.Text)
    description = db.Column(db.Text)
    width = db.Column(db.Integer)
    height = db.Column(db.Integer)
    username = db.Column(db.String(100))
    keywords = db.relationship("Keyword", backref="photo", lazy=True)
    colors = db.relationship("Color", backref="photo", lazy=True)

class Keyword(db.Model):
    __tablename__ = "keywords"
    id = db.Column(db.Integer, primary_key=True)
    photo_id = db.Column(db.String(50), db.ForeignKey("photos.photo_id"))
    keyword = db.Column(db.String(255))

class Color(db.Model):
    __tablename__ = "colors"
    id = db.Column(db.Integer, primary_key=True)
    photo_id = db.Column(db.String(50), db.ForeignKey("photos.photo_id"))
    hex = db.Column(db.String(10))
    color_name = db.Column(db.String(50))