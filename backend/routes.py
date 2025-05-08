from flask import Blueprint, request, jsonify, make_response, current_app, send_file
from backend import db, bcrypt
from backend.models import User
import jwt
import datetime
from functools import wraps
from flask_cors import CORS

routes = Blueprint('routes', __name__)
CORS(routes, origins='http://localhost:3000')


def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None
        if 'Authorization' in request.headers:
            auth_header = request.headers['Authorization']
            try:
                token = auth_header.split(" ")[1]
            except IndexError:
                return jsonify({'message': 'Token Bearer inválido!'}), 401

        if not token:
            return jsonify({'message': 'Token ausente!'}), 401

        try:
            data = jwt.decode(token, current_app.config['SECRET_KEY'], algorithms=["HS256"])
            current_user = User.query.filter_by(id=data['user_id']).first()
            if current_user is None:
                return jsonify({'message': 'Usuário não encontrado!'}), 401
        except jwt.ExpiredSignatureError:
            return jsonify({'message': 'Token expirado!'}), 401
        except jwt.InvalidTokenError:
            return jsonify({'message': 'Token inválido!'}), 401
        except Exception as e:
            return jsonify({'message': 'Algo deu errado com o token!', 'error': str(e)}), 500

        return f(current_user, *args, **kwargs)
    return decorated



@routes.route('/login', methods=['POST', 'OPTIONS'])
def login():
    if request.method == 'OPTIONS':
        response = make_response('', 200)
        response.headers['Access-Control-Allow-Origin'] = 'http://localhost:3000'
        response.headers['Access-Control-Allow-Methods'] = 'POST, OPTIONS'
        response.headers['Access-Control-Allow-Headers'] = 'Content-Type, Authorization'
        return response

    data = request.get_json()
    username = data.get('username')
    password = data.get('password')

    if not username or not password:
        return jsonify({'message': 'Preencha todos os campos'}), 400

    user = User.query.filter_by(username=username).first()

    if user and user.check_password(password):
        token = jwt.encode(
            {'user_id': user.id, 'exp': datetime.datetime.utcnow() + datetime.timedelta(hours=1)},
            current_app.config['SECRET_KEY'], algorithm='HS256'
        )
        response = jsonify({'message': 'Login realizado com sucesso', 'token': token})
        response.headers['Access-Control-Allow-Origin'] = 'http://localhost:3000'
        return response, 200

    return jsonify({'message': 'Credenciais inválidas'}), 401


@routes.route('/register', methods=['POST', 'OPTIONS'])
def register():
    if request.method == 'OPTIONS':
        response = make_response('', 200)
        response.headers['Access-Control-Allow-Origin'] = 'http://localhost:3000'
        response.headers['Access-Control-Allow-Methods'] = 'POST, OPTIONS'
        response.headers['Access-Control-Allow-Headers'] = 'Content-Type'
        return response

    data = request.get_json()
    username = data.get('username')
    email = data.get('email')
    password = data.get('password')

    if not username or not email or not password:
        return jsonify({'message': 'Preencha todos os campos'}), 400

    if User.query.filter_by(username=username).first():
        return jsonify({'message': 'Usuário já existe'}), 409

    if User.query.filter_by(email=email).first():
        return jsonify({'message': 'Email já cadastrado'}), 409

    new_user = User(username=username, email=email)
    new_user.set_password(password)

    try:
        db.session.add(new_user)
        db.session.commit()

        response = jsonify({'message': 'Usuário registrado com sucesso'})
        response.headers['Access-Control-Allow-Origin'] = 'http://localhost:3000'
        return response, 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 400



@routes.route('/verify_token', methods=['GET', 'OPTIONS'])
def verify_token(): # Remova o parâmetro current_user
    if request.method == 'OPTIONS':
        response = make_response('', 200)
        response.headers['Access-Control-Allow-Origin'] = 'http://localhost:3000'
        response.headers['Access-Control-Allow-Methods'] = 'GET, OPTIONS'
        response.headers['Access-Control-Allow-Headers'] = 'Content-Type, Authorization'
        return response
    elif request.method == 'GET':
        return token_required(verify_token_handler)() # Chame a função com ()
    return None

def verify_token_handler(current_user): # Mantenha o parâmetro current_user
    response = jsonify({'message': 'Token válido'})
    return response, 200

@routes.route('/generate_qrcode', methods=['POST', 'OPTIONS'])
@token_required
def generate_qrcode(current_user):
    if request.method == 'OPTIONS':
        response = make_response('', 200)
        response.headers['Access-Control-Allow-Origin'] = 'http://localhost:3000'
        response.headers['Access-Control-Allow-Methods'] = 'POST, OPTIONS'
        response.headers['Access-Control-Allow-Headers'] = 'Content-Type, Authorization'
        return response

    data = request.get_json()
    qr_data = data.get('data')

    if not qr_data:
        return jsonify({'message': 'No data provided'}), 400

    import qrcode
    import io
    img = qrcode.make(qr_data)
    img_bytes = io.BytesIO()
    img.save(img_bytes, format='PNG')
    img_bytes.seek(0)
    
    return send_file(img_bytes, mimetype='image/png')
