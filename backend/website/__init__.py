from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import JWTManager
from flask_security import Security, SQLAlchemyUserDatastore
from flask_cors import CORS
from datetime import timedelta
from website.models import User, Role,db


jwt = JWTManager()

def create_app():
    app = Flask(__name__)

    CORS(app)

    app.config["SECRET_KEY"] = "your_secret_key"
    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///database_1.db"
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    app.config["JWT_SECRET_KEY"] = "jwt_secret_key"
    app.config["JWT_ACCESS_TOKEN_EXPIRES"] = timedelta(hours=24)
    app.config["SECURITY_TOKEN_AUTHENTICATION_HEADER"] = 'Authentication-Token'


    db.init_app(app)
    jwt.init_app(app)


    user_datastore = SQLAlchemyUserDatastore(db, User, Role)
    security = Security(app, user_datastore)

    with app.app_context():
        db.create_all()

    return app
