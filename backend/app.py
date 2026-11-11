import os

from flask import Flask

from models import db


def create_app(database_url=None):
    app = Flask(__name__)
    app.config["SQLALCHEMY_DATABASE_URI"] = database_url or os.environ.get(
        "DATABASE_URL", "postgresql+psycopg://localhost/splitspace"
    )
    app.config["SECRET_KEY"] = os.environ.get("SECRET_KEY", "dev")
    app.config["SESSION_COOKIE_HTTPONLY"] = True
    app.config["SESSION_COOKIE_SAMESITE"] = "Lax"
    db.init_app(app)

    # ponytail: create_all can't alter existing tables; add Flask-Migrate once deployed data must survive schema changes.
    with app.app_context():
        db.create_all()

    @app.get("/api/health")
    def health():
        return {"status": "ok"}

    return app
