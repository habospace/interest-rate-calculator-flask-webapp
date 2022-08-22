from flask import Flask
from sqlalchemy import create_engine
from flask_smorest import Api

from web_api.views import api_blp


def create_app(api_title: str, api_version: str, openapi_version: str, db_connection_string: str) -> Flask:
    app = Flask(__name__)
    app.config["API_TITLE"] = api_title
    app.config["API_VERSION"] = api_version
    app.config["OPENAPI_VERSION"] = openapi_version
    app.db_connection = create_engine(db_connection_string)
    api = Api(app)
    api.register_blueprint(api_blp)
    return app
