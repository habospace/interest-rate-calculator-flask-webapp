from flask import Flask
from sqlalchemy import create_engine

from web_api.views import Loan


def create_app(api_title: str, api_version: str, openapi_version: str, db_connection_string: str) -> Flask:
    app = Flask(__name__)
    app.config["API_TITLE"] = api_title
    app.config["API_VERSION"] = api_version
    app.config["OPENAPI_VERSION"] = openapi_version
    app.db_connection = create_engine(db_connection_string)
    register_views(app)
    return app


def register_views(app: Flask):
    loan_view = Loan.as_view("loan")
    # keeping it simple so registering /api/version/ prefixed blueprints
    app.add_url_rule("/loan/", defaults={"loan_id": None}, view_func=loan_view, methods=["GET"])
    app.add_url_rule("/loan/", view_func=loan_view, methods=["POST"])
    app.add_url_rule("/loan/<int:loan_id>", view_func=loan_view, methods=["GET", "PUT", "DELETE"])
