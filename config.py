import os
# from werkzeug.security import generate_password_hash

SQLALCHEMY_DATABASE_URI = os.getenv("SQLALCHEMY_DATABASE_URI", "mysql+pymysql://root@localhost/photo_app")
# ADMIN_USERNAME = os.getenv("ADMIN_USERNAME", "admin")
# ADMIN_PASSWORD_HASH = os.getenv("ADMIN_PASSWORD_HASH", generate_password_hash("1234"))
SECRET_KEY = os.getenv("SECRET_KEY", "supersecretkey")
DATA_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data")