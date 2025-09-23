from app.api import api_bp
app.register_blueprint(api_bp, url_prefix='/api')

from flask import Flask
from flask_cors import CORS          # пока фронт на localhost:3000
from flask_jwt_extended import JWTManager
from flask_wtf.csrf import CSRFProtect

from app import db
from app.api import api_bp, csrf
from app.models import Base

app = Flask(__name__)
app.config.update(
    SQLALCHEMY_DATABASE_URI='sqlite:///app.db',
    JWT_SECRET_KEY='REPLACE_WITH_STRONG_KEY',
    SECRET_KEY='REPLACE_FOR_CSRF',
    ATTACHMENT_FOLDER=Path('backend/static/attachments'),
    MAX_CONTENT_LENGTH=5 * 1024 * 1024,  # 5 Мб
)
app.config['ATTACHMENT_FOLDER'].mkdir(exist_ok=True)

db.init_app(app)
jwt = JWTManager(app)
CORS(app, supports_credentials=True, origins=['http://localhost:3000'])
csrf.init_app(app)

with app.app_context():
    Base.metadata.create_all(bind=db.engine)

app.register_blueprint(api_bp, url_prefix='/api')