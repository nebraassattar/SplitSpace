import os
from flask import Flask, jsonify, request
from dotenv import load_dotenv
from models import db
from api import api

load_dotenv()

def create_app(database_url=None):
    app = Flask(__name__)
    app.config.update(
        SQLALCHEMY_DATABASE_URI=database_url or os.getenv('DATABASE_URL', 'postgresql+psycopg://localhost/splitspace'),
        SQLALCHEMY_TRACK_MODIFICATIONS=False,
        SECRET_KEY=os.getenv('SECRET_KEY', 'development-only-change-me'),
        SESSION_COOKIE_HTTPONLY=True,
        SESSION_COOKIE_SAMESITE='Lax',
        SESSION_COOKIE_SECURE=os.getenv('COOKIE_SECURE', 'false').lower() == 'true',
    )
    db.init_app(app)
    app.register_blueprint(api)
    @app.get('/api/health')
    def health(): return {'status': 'ok'}
    @app.before_request
    def csrf_origin_check():
        if request.method in ('POST','PUT','PATCH','DELETE') and request.path.startswith('/api/'):
            origin = request.headers.get('Origin')
            allowed = os.getenv('ALLOWED_ORIGINS', 'http://localhost:5173,http://127.0.0.1:5173').split(',')
            if origin and origin not in allowed:
                return jsonify(error='Untrusted origin'), 403
    with app.app_context():
        db.create_all()
    return app

app = create_app() if __name__ != '__main__' else None
