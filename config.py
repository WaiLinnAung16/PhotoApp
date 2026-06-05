import os

# MySQL connection string (override in CI/Docker with SQLALCHEMY_DATABASE_URI)
SQLALCHEMY_DATABASE_URI = os.getenv(
    "SQLALCHEMY_DATABASE_URI", "mysql+pymysql://root@localhost/photo_app"
)
# Required for Flask session signing (change in production)
SECRET_KEY = os.getenv("SECRET_KEY", "supersecretkey")
# ETL reads only from this directory; paths outside it are rejected
DATA_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data")
