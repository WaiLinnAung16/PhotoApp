from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


class Photo(db.Model):
    """Core photo record displayed in the gallery."""

    __tablename__ = "photos"
    photo_id = db.Column(db.String(50), primary_key=True)
    image_url = db.Column(db.Text)
    description = db.Column(db.Text)
    width = db.Column(db.Integer)
    height = db.Column(db.Integer)
    username = db.Column(db.String(100))
    # One-to-many: a photo can have multiple keywords and color swatches
    keywords = db.relationship("Keyword", backref="photo", lazy=True)
    colors = db.relationship("Color", backref="photo", lazy=True)


class Keyword(db.Model):
    """Searchable tag linked to a photo; drives keyword search and autocomplete."""

    __tablename__ = "keywords"
    id = db.Column(db.Integer, primary_key=True)
    photo_id = db.Column(db.String(50), db.ForeignKey("photos.photo_id"))
    keyword = db.Column(db.String(255))


class Color(db.Model):
    """Dominant color associated with a photo (hex value and human-readable name)."""

    __tablename__ = "colors"
    id = db.Column(db.Integer, primary_key=True)
    photo_id = db.Column(db.String(50), db.ForeignKey("photos.photo_id"))
    hex = db.Column(db.String(10))
    color_name = db.Column(db.String(50))
