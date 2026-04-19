"""HTTP tests for Flask routes."""
import os

# In-memory SQLite before importing the app
os.environ["SQLALCHEMY_DATABASE_URI"] = "sqlite:///:memory:"

import pytest

from models import Keyword, Photo, db


@pytest.fixture
def app():
    from app import app as flask_app

    flask_app.config["TESTING"] = True
    with flask_app.app_context():
        db.create_all()
        yield flask_app
        db.drop_all()


@pytest.fixture
def client(app):
    return app.test_client()


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


def test_home_get_returns_200_and_title(client):
    response = client.get("/")
    assert response.status_code == 200
    assert b"Photo Explorer" in response.data


def test_home_post_search(client, sample_photo_with_keyword):
    response = client.post("/", data={"keyword": "nature"})
    assert response.status_code == 200
    assert b"Photo Explorer" in response.data


def test_suggest_keywords_empty_query_returns_empty_json(client):
    response = client.get("/suggest_keywords")
    assert response.status_code == 200
    assert response.json == []


def test_suggest_keywords_empty_q_param_returns_empty_json(client):
    response = client.get("/suggest_keywords?q=")
    assert response.status_code == 200
    assert response.json == []


def test_suggest_keywords_returns_matches(client, sample_photo_with_keyword):
    response = client.get("/suggest_keywords?q=nat")
    assert response.status_code == 200
    data = response.get_json()
    assert isinstance(data, list)
    assert "nature" in data
