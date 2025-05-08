# backend/app.py

from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_cors import CORS
from backend.config import Config

# Inicializando o banco de dados
db = SQLAlchemy()
migrate = Migrate()

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    # Configuração do CORS globalmente
    CORS(app, origins="http://localhost:3000", methods=["POST", "GET", "OPTIONS"], allow_headers=["Content-Type", "Authorization"])  # Permite o frontend rodando em localhost:3000

    # Inicializando o banco de dados e migrações
    db.init_app(app)
    migrate.init_app(app, db)

    # Importando e registrando rotas
    from backend import routes

    return app

# Instanciando e rodando o app
if __name__ == '__main__':
    app = create_app()
    app.run(debug=True)
