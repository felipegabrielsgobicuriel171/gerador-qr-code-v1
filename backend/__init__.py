# backend/__init__.py

from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_bcrypt import Bcrypt
from backend.config import Config

# Inicialização das extensões
db = SQLAlchemy()
migrate = Migrate()
bcrypt = Bcrypt()

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    # Inicializa as extensões com a instância do app
    db.init_app(app)
    migrate.init_app(app, db)
    bcrypt.init_app(app)

    # Importa e registra os blueprints
    from backend.routes import routes
    from backend.qrcode_routes import qr

    app.register_blueprint(routes)
    app.register_blueprint(qr)

    return app
