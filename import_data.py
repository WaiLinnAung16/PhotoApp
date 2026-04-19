from app import app
from models import db
from etl_service import ETLService

if __name__ == "__main__":
    with app.app_context():
        db.create_all()

        etl = ETLService()
        etl.run()