"""Unit tests for ``PhotoService``."""
import os

os.environ["SQLALCHEMY_DATABASE_URI"] = "sqlite:///:memory:"

import pytest

from models import Keyword, Photo, db
from services import PhotoService


@pytest.fixture
def app():
    from app import app as flask_app

    flask_app.config["TESTING"] = True
    with flask_app.app_context():
        db.create_all()
        yield flask_app
        db.drop_all()


@pytest.fixture
def sample_photo_with_keyword(app):
    with app.app_context():
        photo = Photo(
            photo_id="test-1",
            image_url="https://example.com/p.jpg",
            description="A test photo",
            width=800,
            height=600,
            username="tester",
        )
        db.session.add(photo)
        db.session.add(Keyword(photo_id="test-1", keyword="nature"))
        db.session.commit()
        return "test-1"


def test_get_all_photos_respects_limit(app):
    with app.app_context():
        for i in range(5):
            db.session.add(
                Photo(
                    photo_id=f"id-{i}",
                    image_url=f"https://example.com/{i}.jpg",
                    description="",
                    width=1,
                    height=1,
                    username="u",
                )
            )
        db.session.commit()

        assert len(PhotoService.get_all_photos(limit=3)) == 3
        assert len(PhotoService.get_all_photos(limit=20)) == 5


def test_get_all_photos_default_limit(app):
    with app.app_context():
        for i in range(25):
            db.session.add(
                Photo(
                    photo_id=f"p-{i}",
                    image_url="https://x",
                    description="",
                    width=1,
                    height=1,
                    username="u",
                )
            )
        db.session.commit()
        assert len(PhotoService.get_all_photos()) == 20


def test_search_by_keyword_finds_matching_photo(app, sample_photo_with_keyword):
    with app.app_context():
        results = PhotoService.search_by_keyword("nature")
        assert len(results) == 1
        assert results[0].photo_id == sample_photo_with_keyword


def test_search_by_keyword_no_match(app, sample_photo_with_keyword):
    with app.app_context():
        assert PhotoService.search_by_keyword("nonexistent-term-xyz") == []
